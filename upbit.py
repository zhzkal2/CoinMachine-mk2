from flask import request
from flask_restx import Resource, Api, Namespace, fields
import pyupbit
import config
import numpy as np
import time
from prophet import Prophet

Upbit = Namespace(
    name="Upbit",
    description="Upbit 리스트를 작성하기 위해 사용하는 API.",
)
pairSeporator = "-"
errorText = "오류 발생"
successText = "정상 동작"


@Upbit.route("/price/<string:code>/<string:ticker>")
@Upbit.doc(
    params={"code": "KRW", "ticker": "BTC"},
    description="Upbit ticker에 해당하는 현재 가격을 가져옵니다.",
)
class CurrentPrice(Resource):
    @Upbit.response(200, "Success")
    @Upbit.response(500, "Failed")
    def get(self, code, ticker):
        msg = successText
        price = 0
        try:
            """Upbit ticker에 해당하는 현재 가격을 가져옵니다.."""
            price = pyupbit.get_orderbook(code + pairSeporator + ticker)[
                "orderbook_units"
            ][0]["ask_price"]
        except:
            msg = errorText
        return {"ticker": ticker, "ask_price": price, "msg": msg}

# 중복제거 검토
# @Upbit.route("/price-start/<string:code>/<string:ticker>")
# @Upbit.doc(params={"code": "KRW", "ticker": "BTC"})
# class StartPrice(Resource):
#     @Upbit.response(200, "Success")
#     @Upbit.response(500, "Failed")
#     def get(self, code, ticker):
#         msg = successText
#         price = 0
#         try:
#             """Upbit ticker에 해당하는 현재 가격을 가져옵니다.."""
#             print(
#                 pyupbit.get_orderbook(code + pairSeporator + ticker)["orderbook_units"]
#             )
#             price = pyupbit.get_orderbook(code + pairSeporator + ticker)[
#                 "orderbook_units"
#             ][0]["ask_price"]
#         except:
#             msg = errorText
#         return {"ticker": ticker, "ask_price": price, "msg": msg}


@Upbit.route(
    "/moving-average/<string:code>/<string:ticker>/<string:interval>/<int:count>"
)
@Upbit.doc(params={"code": "KRW", "ticker": "BTC", "interval": "day", "count": 5})
class MovingAverage(Resource):
    @Upbit.response(200, "Success")
    @Upbit.response(500, "Failed")
    def get(self, code, ticker, count, interval):
        msg = successText
        ma5 = 0
        try:
            """5일 이동 평균선 조회"""
            df = pyupbit.get_ohlcv(
                code + pairSeporator + ticker, interval=interval, count=count
            )
            ma5 = df["close"].rolling(count).mean().iloc[-1]
        except:
            msg = errorText
        return {
            "ticker": ticker,
            "interval": interval,
            "count": count,
            "price": ma5,
            "msg": msg,
        }


@Upbit.route("/balance/<string:ticker>")
@Upbit.doc(params={"ticker": "BTC"})
class Balance(Resource):
    @Upbit.response(200, "Success")
    @Upbit.response(500, "Failed")
    def get(self, ticker):
        msg = successText
        balance = 0
        balances = {}
        try:
            """잔고 조회"""
            balances = pyupbit.Upbit(
                config.upbit_access_key, config.upbit_secret_key
            ).get_balances()

            for b in balances:
                if b["currency"] == ticker:
                    if b["balance"] is not None:
                        balance = float(b["balance"])
                    else:
                        balance = 0
        except:
            msg = balances["error"]["message"]
        balance, msg = get_balance(ticker)

        return {"ticker": ticker, "balance": balance, "msg": msg}


@Upbit.route("/target-price/<string:code>/<string:ticker>/<float:k>")
@Upbit.doc(params={"code": "KRW", "ticker": "BTC", "k": 0.5})
class TargetPrice(Resource):
    @Upbit.response(200, "Success")
    @Upbit.response(500, "Failed")
    def get(self, code, ticker, k):
        msg = successText
        target_price = 0

        try:
            """변동성 돌파 전략으로 매수 목표가 조회"""
            df = pyupbit.get_ohlcv(
                code + pairSeporator + ticker, interval="day", count=2
            )  # 당일과 전일 데이터 취득
            target_price = (
                df.iloc[0]["close"] + (df.iloc[0]["high"] - df.iloc[0]["low"]) * k
            )
        except:
            msg = errorText

        return {
            "code": code,
            "ticker": ticker,
            "target_price": target_price,
            "msg": msg,
        }


# k값 취득
@Upbit.route("/best-kvalue/<string:code>/<string:ticker>/<int:count>")
@Upbit.doc(params={"code": "KRW", "ticker": "BTC", "count": 7})
class BestKvalue(Resource):
    @Upbit.response(200, "Success")
    @Upbit.response(500, "Failed")
    def get(self, code, ticker, count):
        msg = successText
        target_price = 0
        ticker = code + pairSeporator + ticker

        try:
            """count 기간중 최고의 성과를 낸 k-value 취득"""
            tmp_ror = 0
            tmp_k = 0
            for k in np.arange(0.1, 1.0, 0.01):
                k = round(k, 2)
                ror = get_ror(k, ticker, count)
                if tmp_ror < ror:
                    tmp_ror = ror
                    tmp_k = k
                time.sleep(0.1)  # 0.1초 딜레이
        except:
            msg = errorText

        return {
            "code": code,
            "ticker": ticker,
            "target_price": target_price,
            "k_value": tmp_k,
            "msg": msg,
        }


def get_ror(k, ticker, count):
    df = pyupbit.get_ohlcv(ticker, count=count)
    df["range"] = (df["high"] - df["low"]) * k
    df["target"] = df["open"] + df["range"].shift(1)
    df["ror"] = np.where(df["high"] > df["target"], df["close"] / df["target"], 1)
    ror = df["ror"].cumprod()[-2]
    return ror


@Upbit.route("/start-time/<string:code>/<string:ticker>")
@Upbit.doc(params={"code": "KRW", "ticker": "BTC"})
class StartTime(Resource):
    @Upbit.response(200, "Success")
    @Upbit.response(500, "Failed")
    def get(self, code, ticker):
        msg = successText
        ticker = code + pairSeporator + ticker

        try:
            """시작 시간 조회"""
            df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
            start_time = str(df.index[0])
        except:
            msg = errorText

        return {"code": code, "ticker": ticker, "start_time": start_time, "msg": msg}


@Upbit.route(
    "/moving-average/<string:code>/<string:ticker>/<string:interval>/<int:count>"
)
@Upbit.doc(params={"code": "KRW", "ticker": "BTC", "interval": "day", "count": 5})
class MovingAverage(Resource):
    @Upbit.response(200, "Success")
    @Upbit.response(500, "Failed")
    def get(self, code, ticker, count, interval):
        msg = successText
        ticker = code + pairSeporator + ticker
        ma5 = 0
        try:
            """5일 이동 평균선 조회"""
            df = pyupbit.get_ohlcv(ticker, interval=interval, count=count)
            ma5 = df["close"].rolling(5).mean().iloc[-1]
        except:
            msg = errorText
        return {
            "ticker": ticker,
            "interval": interval,
            "count": count,
            "price": ma5,
            "msg": msg,
        }

# 원화로 비트코인을 시장가 구매
@Upbit.route("/buy-market-order/<string:code>/<string:ticker>/<float:amount>")
@Upbit.doc(params={"code": "KRW", "ticker": "BTC", "amount": "5500"})
class BuyMarketOrder(Resource):
    @Upbit.response(200, "Success")
    @Upbit.response(500, "Failed")
    def get(self, code, ticker, amount):
        msg = successText
        ticker = code + pairSeporator + ticker
        buy_result = None  
        try:
            """시장가 구매 """
            krw_amount = amount * 0.9995 #수수료 계산으로 인해 5000원으로 구매시 실패 
            print(ticker,krw_amount)
            buy_result= pyupbit.Upbit(
                config.upbit_access_key, config.upbit_secret_key
            ).buy_market_order(ticker, krw_amount)
        except:
            msg = errorText
        return {
            "ticker": ticker,
            "krw": amount,
            "result": buy_result,
            "msg": msg,
        }
    
# 비트코인을 원화로 시장가 판매
@Upbit.route("/sell-market-order/<string:code>/<string:ticker>/<float:amount>")
@Upbit.doc(params={"code": "KRW", "ticker": "BTC", "amount": "5000"})
class BuyMarketOrder(Resource):
    @Upbit.response(200, "Success")
    @Upbit.response(500, "Failed")
    def get(self, code, ticker, amount):
        msg = successText
        ticker = code + pairSeporator + ticker
        sell_result = None  
        try:
            """시장가 판매 """
            btc_amount = amount * 0.9995 #수수료 계산으로 인해 5000원으로 구매시 실패 
            print(ticker,btc_amount)
            sell_result= pyupbit.Upbit(
                config.upbit_access_key, config.upbit_secret_key
            ).sell_market_order(ticker, btc_amount)
        except:
            msg = errorText
        return {
            "ticker": ticker,
            "krw": amount,
            "result": sell_result,
            "msg": msg,
        }


@Upbit.route(
    "/predict-price/<string:code>/<string:ticker>/<string:interval>/<int:count>"
)
@Upbit.doc(
    params={"code": "KRW", "ticker": "BTC", "interval": "minute30", "count": 144}
)
class PredictPrice(Resource):
    @Upbit.response(200, "Success")
    @Upbit.response(500, "Failed")
    def get(self, code, ticker, count, interval):
        msg = successText
        ticker = code + pairSeporator + ticker
        predicted_close_price = 0
        # try:
        """Prophet으로 당일 종가 가격 예측"""
        # 학습데이터는 interval 단위로 count 값만큼 단기 예측이므로 최근 트렌드만 반영되도록 하는게 유리
        # Ex. minute30 -> 30분봉, 144 -> 30분봉 144개 3일치
        df = pyupbit.get_ohlcv(ticker, interval, count)
        df = df.reset_index()
        df["ds"] = df["index"]
        df["y"] = df["close"]
        data = df[["ds", "y"]]
        model = Prophet()
        model.fit(data)
        # 　24시간 뒤 예측
        future = model.make_future_dataframe(periods=24, freq="H")
        forecast = model.predict(future)
        closeDf = forecast[
            forecast["ds"] == forecast.iloc[-1]["ds"].replace(hour=9)
        ]  # 9시 마감이라 9시
        if len(closeDf) == 0:
            closeDf = forecast[
                forecast["ds"] == data.iloc[-1]["ds"].replace(hour=9)
            ]  # 9시 마감이라 9시
        closeValue = closeDf["yhat"].values[0]
        predicted_close_price = closeValue
        # except:
        #     msg = errorText
        return {
            "ticker": ticker,
            "interval": interval,
            "count": count,
            "predicted_close_price": predicted_close_price,
            "msg": msg,
        }


def get_balance(target: str):
    """Get the balance of a specific currency.

    Args:
        target (str): The currency to check the balance of.

    Returns:
        Tuple[float, str]: A tuple containing the balance and an error message.

    Raises:
        ValueError: If the currency is not supported.

    """
    balance = 0
    balances = {}
    msg = successText
    try:
        """Get the current account balance."""
        balances = pyupbit.Upbit(
            config.upbit_access_key, config.upbit_secret_key
        ).get_balances()

        for b in balances:
            if b["currency"] == target:
                if b["balance"] is not None:
                    balance = float(b["balance"])
                else:
                    balance = 0
    except Exception as e:
        msg = f"Error getting balance: {e}"

    return balance, msg


predicted_close_price = 0


def predict_price(ticker):
    """Prophet으로 당일 종가 가격 예측"""
    global predicted_close_price
    # 학습데이터는 3일로 최근 트렌드만 반영되도록
    df = pyupbit.get_ohlcv(ticker, interval="minute30", count=144)
    df = df.reset_index()
    df["ds"] = df["index"]
    df["y"] = df["close"]
    data = df[["ds", "y"]]
    model = Prophet()
    model.fit(data)
    future = model.make_future_dataframe(periods=24, freq="H")
    forecast = model.predict(future)
    closeDf = forecast[forecast["ds"] == forecast.iloc[-1]["ds"].replace(hour=9)]
    if len(closeDf) == 0:
        closeDf = forecast[forecast["ds"] == data.iloc[-1]["ds"].replace(hour=9)]
    closeValue = closeDf["yhat"].values[0]
    predicted_close_price = closeValue
