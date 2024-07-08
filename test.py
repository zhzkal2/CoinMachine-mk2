import datetime
import requests
import time
import schedule
import threading

day_max_price = 0


# debug
# print("----------------------------------")


def get_start_time():
    res = requests.get("http://127.0.0.1:800/upbit/start-time/KRW/BTC")
    if res.status_code == 200:
        data = res.json()
        start_time = datetime.datetime.fromisoformat(data["start_time"])
        end_time = start_time + datetime.timedelta(days=1)
        # print("start time : ", start_time)
        # print("end time : ", end_time)
    return start_time


def get_target_price(k):
    # 변동성 돌파 전략으로 매수 목표가 조회
    target_price = None  # target_price 초기화
    res = requests.get(f"http://127.0.0.1:800/upbit/target-price/KRW/BTC/{k}")

    if res.status_code == 200:
        data = res.json()
        target_price = data["target_price"]
        # print("변동성 돌파 전략 매수가 (target_price) : ", target_price)
    return target_price


def get_kvalue():
    # k 밸류 구하기
    res = requests.get("http://127.0.0.1:800/upbit/best-kvalue/KRW/BTC/7")
    if res.status_code == 200:
        data = res.json()
        k_value = data["k_value"]
        # print("k 밸류 (k value) : ", k_value)
    return k_value


def get_ma5():
    # 5일 이동 평균선 조회
    res = requests.get("http://127.0.0.1:800/upbit/moving-average/KRW/BTC/day/5")
    if res.status_code == 200:
        data = res.json()
        ma5 = data["price"]
        # print("5일 평균선(ma5) :", ma5)
    return ma5


def get_current_price():
    # 현재 가격을 가져옵니다.
    res = requests.get("http://127.0.0.1:800/upbit/price-start/KRW/BTC")
    if res.status_code == 200:
        data = res.json()
        current_price = data["ask_price"]
        # print("현재가격(current_price) : ", current_price)
    return current_price


def get_predicted_close_price():
    # Prophet으로 당일 종가 가격 예측
    res = requests.get("http://127.0.0.1:800/upbit/predict-price/KRW/BTC/minute30/144")
    if res.status_code == 200:
        data = res.json()
        predicted_close_price = data["predicted_close_price"]
        # print(
        #     "Prophet으로 당일 종가 가격 예측(predicted_close_price) : ",
        #     predicted_close_price,
        # )
    return predicted_close_price


# 비트코인 잔고조회
def get_balance_BTC():
    res = requests.get("http://127.0.0.1:800/upbit/balance/BTC")
    if res.status_code == 200:
        data = res.json()
        balance = data["balance"]
        # print(
        #     "BTC 잔고(balance) : ",
        #     balance,
        # )
    return balance


def get_balance_KRW():
    res = requests.get("http://127.0.0.1:800/upbit/balance/KRW")
    if res.status_code == 200:
        data = res.json()
        krw = data["balance"]
        # print(
        #     "KRW 잔고(balance) : ",
        #     krw,
        # )
    return krw


def get_buy_market(amount):
    # 구매요청 - 구매한 가격을 리턴
    res = requests.get(f"http://127.0.0.1:800/upbit/buy-market-order/KRW/BTC/{amount}")

    if res.status_code == 200:
        data = res.json()
        print(data)
        price = data["result"]["price"]
        print(amount, "가격만큼 구매시도 : ", price, "구매완료")
    return price


def get_sell_market(amount):
    # 판매요청 - 판매한 가격을 리턴
    res = requests.get(f"http://127.0.0.1:800/upbit/sell-market-order/KRW/BTC/{amount}")

    if res.status_code == 200:
        data = res.json()
        print(data)
        volume = data["result"]["volume"]
        print(amount, "가격만큼 판매시도 : ", volume, "판매완료")
    return volume


# ---------------------------------------
# 스케쥴러 코드


# 스케줄러를 별도의 스레드에서 실행
# def run_schedule():
#     while True:
#         schedule.run_pending()
#         time.sleep(1)


# # 스케줄러 스레드 시작
# scheduler_thread = threading.Thread(target=run_schedule, daemon=True)
# scheduler_thread.start()


# ---------------------------------------


def check_market():
    day_max_price = 0
    print("체크 마켓 실행중!")
    kvalue = get_kvalue()
    start_time = get_start_time()
    end_time = start_time + datetime.timedelta(days=1)

    while True:

        try:
            now = datetime.datetime.now()
            print(start_time, now, end_time, "실행중입니당", kvalue)
            if start_time < now < end_time - datetime.timedelta(seconds=10):
                # print(now)
                current_price = get_current_price()

                if day_max_price < current_price:
                    day_max_price = current_price
                    # print(day_max_price)
                btc = get_balance_BTC()

                # loss cut
                if btc > 0.00008 and (day_max_price / 100 * 90) > current_price:
                    get_buy_market(krw)

                # 3개의 조건이 성립할 때 구매하도록 설정
                target_price = get_target_price(kvalue)  # 수정필요
                ma5 = get_ma5()
                predicted_close_price = get_predicted_close_price()

                # 조건 체크
                if (
                    target_price < current_price
                    and ma5 < current_price
                    and current_price < predicted_close_price
                ):

                    # 구매가 가능한지 비용체크
                    krw = get_balance_KRW()
                    if krw > 5500:
                        get_buy_market(krw)

            else:
                # 일봉 마감시 판매
                print("일봉마감")
                day_max_price = 0
                btc = get_balance_BTC()
                if btc > 0.00008:
                    get_sell_market(btc)

                kvalue = get_kvalue()
                start_time = get_start_time()
                end_time = start_time + datetime.timedelta(days=1)

            time.sleep(3600)

        except Exception as e:
            print(e)
            time.sleep(10)


# # schedule.every(1).days.do(check_market)
# schedule.every(5).seconds.do(check_market)
# while True:
#     schedule.run_pending()
#     time.sleep(2)
check_market()
