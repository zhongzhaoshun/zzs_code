import requests
import json

class Yunpian(object):
    def __init__(self, api_key):
        """
            api为自己申请的api
        """
        self.api_key = api_key
        # 云片网短信发送接口
        self.single_send_url = "https://sms.yunpian.com/v2/sms/single_send.json"

    def send_sms(self, code, mobile):
        """
        code：验证码
        mobile：发送到指定手机号
        """
        # 接口所需的参数
        params = {
            "apikey": self.api_key,
            "mobile": mobile,
            "text": "【生鲜系统】您的验证码是{}，如非本人操作，请忽略本短信".format(code),
        }
        # 发送post请求
        response = requests.post(self.single_send_url, data=params)
        # 解析返回数据
        re_dict = json.loads(response.text)
        return re_dict