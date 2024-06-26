import schedule
import threading
import time
import requests
import json

# 전역 변수 정의
predict_response = None


# send_api 함수 정의
def send_api(path, method, body=None):
    API_HOST = "http://127.0.0.1:800"
    url = API_HOST + path
    headers = {"Content-Type": "application/json", "charset": "UTF-8", "Accept": "*/*"}
    response = None
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, data=json.dumps(body))
        print("response status %r" % response.status_code)
        print("response text %r" % response.text)
    except Exception as ex:
        print(ex)
    return response


# 스케줄러를 별도의 스레드에서 실행
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


# 스케줄러 스레드 시작
scheduler_thread = threading.Thread(target=run_schedule, daemon=True)
scheduler_thread.start()


def get_predict_price():
    global predict_response
    get_predict_price_url = "/upbit/moving-average/KRW/BTC/minute30/144"
    predict_response = send_api(get_predict_price_url, "GET")
    print("Predict response:", predict_response)


# 앱 시작 시 1회 바로 실행 --debug
get_predict_price()

# 1시간마다 get_predict_price 함수 실행 예약
schedule.every(7).seconds.do(get_predict_price)
