from flask import request
from flask_restx import Resource, Api, Namespace, fields
import config
import requests

errorText = "오류 발생"
successText = "정상 동작"


Slack = Namespace(
    name="Slack API",
    description="Slack을 사용하기 위해 사용하는 API.",
)

slack_fields = Slack.model('Slack Message', {  # Model 객체 생성
    # 'data': fields.String(description='a Todo', required=True, example="what to do")
    'channel': fields.String(description='slack channel id', required=False, example="코이노리-upbit id"),
    'message': fields.String(description='slack message', required=True, example="input message")
})

# slack_fields_with_id = Slack.inherit('slack_fields With ID', slack_fields, {
#     'todo_id': fields.Integer(description='a Todo ID')
# })

@Slack.route('/send-msg')
# @Slack.doc(params={'channel_name': '코이노리-upbit'})
class SendMsg(Resource):
    @Slack.expect(slack_fields) # 주입
    # @Slack.response(200, 'Success', slack_fields_with_id)
    @Slack.response(500, 'Failed')
    def post(self):
        # channel_id가 비어있다면 config 값 사용
        if(request.json.get('channel') != None):
            channel_id = request.json.get('channel')
        else:
            channel_id = config.slack_channel_id

        # param에서 메시지 가져오기
        msg = request.json.get('message')
        # print("msg is : "+msg)
        token = config.slack_token
        # 메시지 전송
        response = self.post_message(token, channel_id, msg)
        if(response.status_code == 200) : 
            result = successText
        else:
            result = errorText

        return {
            'sendText': msg,
            'result': result
        }

    def post_message(self, token, channel, text):
        '''slack 메시지 전송 함수'''
        response = requests.post("https://slack.com/api/chat.postMessage",
            headers={"Authorization": "Bearer "+token},
            data={"channel": channel,"text": text}
        )
        return response