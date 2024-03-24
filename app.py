from flask import Flask, request, jsonify
from flask_restx import Api, Resource  # Api 구현을 위한 Api 객체 import
from upbit import Upbit
from todo import Todo
from slack import Slack

app = Flask(__name__)
api = Api(app,
    version='0.0.1',
    title="coinori chan's API Server",
    description="coinori chan's API Server",
    terms_url="/"
)  # Flask 객체에 Api 객체 등록

# @api.route('/hello')  # 데코레이터 이용, '/hello' 경로에 클래스 등록
# class HelloWorld(Resource):
#     def get(self):  # GET 요청시 리턴 값에 해당 하는 dict를 JSON 형태로 반환
#         return jsonify({"hello": "world!"}), 200

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

api.add_namespace(Todo, '/todos')
api.add_namespace(Upbit, '/upbit')
api.add_namespace(Slack, '/slack')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=800)