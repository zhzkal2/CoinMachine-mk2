from flask import Flask, request, jsonify, make_response
from flask_restx import Api, Resource  # Api 구현을 위한 Api 객체 import

from upbit import Upbit
from todo import Todo
from slack import Slack

import schedule
import threading
import time
import requests
import json


app = Flask(__name__)
api = Api(
    app,
    version="0.0.1",
    title="coinori chan's API Server",
    description="coinori chan's API Server",
    terms_url="/",
)  # Flask 객체에 Api 객체 등록


@api.route("/hello")  # 데코레이터 이용, '/hello' 경로에 클래스 등록
class HelloWorld(Resource):
    def get(self):  # GET 요청시 리턴 값에 해당 하는 dict를 JSON 형태로 반환
        response = make_response(jsonify({"hello": "world!"}), 200)
        return response


# @api.route('/hello/<string:name>')  # url pattern으로 name 설정
# class Hello(Resource):
#     def get(self, name):  # 멤버 함수의 파라미터로 name 설정
#         data = {'message' : 'Welcome!'}
#         return jsonify(data), 200

# @app.route('/hello/<string:name>', methods=['GET'])
# def login(name):
#     data = {'name': 'nabin khadka and ' + name}
#     return jsonify(data), 200

# 가져오기
# api.add_resource(CurrentPrice, '/current_price/<string:ticker>')


# -----------------------

# # 전역 변수 정의
# predict_response = None


# # send_api 함수 정의
# def send_api(path, method, body=None):
#     API_HOST = "http://127.0.0.1:800"
#     url = API_HOST + path
#     headers = {"Content-Type": "application/json", "charset": "UTF-8", "Accept": "*/*"}
#     response = None
#     try:
#         if method == "GET":
#             response = requests.get(url, headers=headers)
#         elif method == "POST":
#             response = requests.post(url, headers=headers, data=json.dumps(body))
#         print("response status %r" % response.status_code)
#         print("response text %r" % response.text)
#     except Exception as ex:
#         print(ex)
#     return response


# def get_predict_price():
#     get_predict_price_url = "/upbit/moving-average/KRW/BTC/minute30/144"
#     predict_response = send_api(get_predict_price_url, "GET")
#     print("Predict response:", predict_response)


# -----------------------

api.add_namespace(Todo, "/todos")
api.add_namespace(Upbit, "/upbit")
api.add_namespace(Slack, "/slack")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=800)
