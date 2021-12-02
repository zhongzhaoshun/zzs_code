# -*- coding: utf-8 -*-

# pip install pycryptodome

from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode
from urllib.parse import quote_plus
from urllib.parse import urlparse, parse_qs
from urllib.request import urlopen
from base64 import decodebytes, encodebytes
from MxShop2 import settings

import os

import json


class AliPay(object):
    """
    支付宝支付接口
    """

    def __init__(self, appid, app_notify_url, app_private_key_path,
                 alipay_public_key_path, return_url, debug=False):
        # 支付宝沙箱环境的appid
        self.appid = appid
        self.app_notify_url = app_notify_url
        # 私钥文件路径
        self.app_private_key_path = app_private_key_path
        self.app_private_key = None
        self.return_url = return_url
        # 读取这个文件之后直接加密,验证支付宝返回的消息的时候，这个是最主要的一个key
        with open(self.app_private_key_path) as fp:
            self.app_private_key = RSA.importKey(fp.read())

        self.alipay_public_key_path = alipay_public_key_path
        with open(self.alipay_public_key_path) as fp:
            self.alipay_public_key = RSA.import_key(fp.read())

        if debug is True:
            self.__gateway = "https://openapi.alipaydev.com/gateway.do"
        else:
            self.__gateway = "https://openapi.alipay.com/gateway.do"

    def direct_pay(self, subject, out_trade_no, total_amount, return_url=None, **kwargs):
        biz_content = {
            "subject": subject,
            "out_trade_no": out_trade_no,
            "total_amount": total_amount,
            "product_code": "FAST_INSTANT_TRADE_PAY",
            # "qr_pay_mode":4
        }
        # 传一些可变的参数就放到里面来
        biz_content.update(kwargs)
        data = self.build_body("alipay.trade.page.pay", biz_content, self.return_url)
        return self.sign_data(data)

    # 这里面的字段和官方文档的公共请求参数的字段是对应上的
    def build_body(self, method, biz_content, return_url=None):
        data = {
            "app_id": self.appid,
            "method": method,
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": biz_content
        }
        if return_url is not None:
            data["notify_url"] = self.app_notify_url
            data["return_url"] = self.return_url

        return data

    # 对请求消息进行签名，重要！！！
    def sign_data(self, data):
        # 进行签名的时候，data里面不能有sign字段的，所以要删除一下
        data.pop("sign", None)
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)
        # 用字符串链接起来，生成签名的时候不要用quote_plus，要用原本的字符串进行生成
        unsigned_string = "&".join("{0}={1}".format(k, v) for k, v in unsigned_items)
        # 进行签名
        sign = self.sign(unsigned_string.encode("utf-8"))
        ordered_items = self.ordered_data(data)
        quoted_string = "&".join("{0}={1}".format(k, quote_plus(v)) for k, v in ordered_items)

        # 获得最终的订单信息字符串
        signed_string = quoted_string + "&sign=" + quote_plus(sign)
        return signed_string

    # 进行排序，不排序会出错的，最后返回一个字典
    def ordered_data(self, data):
        complex_keys = []
        for key, value in data.items():
            if isinstance(value, dict):
                complex_keys.append(key)

        # 将字典类型的数据dump出来
        for key in complex_keys:
            data[key] = json.dumps(data[key], separators=(',', ':'))

        return sorted([(k, v) for k, v in data.items()])

    def sign(self, unsigned_string):
        # 开始计算签名
        key = self.app_private_key
        signer = PKCS1_v1_5.new(key)
        # 使用SHA256进行签名
        signature = signer.sign(SHA256.new(unsigned_string))
        # base64 编码，转换为unicode表示并移除回车
        sign = encodebytes(signature).decode("utf8").replace("\n", "")
        return sign

    def _verify(self, raw_content, signature):
        # 开始计算签名
        key = self.alipay_public_key
        signer = PKCS1_v1_5.new(key)
        digest = SHA256.new()
        digest.update(raw_content.encode("utf8"))
        # 进行验证
        if signer.verify(digest, decodebytes(signature.encode("utf8"))):
            return True
        return False

    def verify(self, data, signature):
        if "sign_type" in data:
            sign_type = data.pop("sign_type")
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)
        message = "&".join(u"{}={}".format(k, v) for k, v in unsigned_items)
        return self._verify(message, signature)


if __name__ == "__main__":
    return_url = 'http://47.92.87.172:8000/?total_amount=0.01&timestamp=2017-08-15+17%3A15%3A13&sign=jnnA1dGO2iu2ltMpxrF4MBKE20Akyn%2FLdYrFDkQ6ckY3Qz24P3DTxIvt%2BBTnR6nRk%2BPAiLjdS4sa%2BC9JomsdNGlrc2Flg6v6qtNzTWI%2FEM5WL0Ver9OqIJSTwamxT6dW9uYF5sc2Ivk1fHYvPuMfysd90lOAP%2FdwnCA12VoiHnflsLBAsdhJazbvquFP%2Bs1QWts29C2%2BXEtIlHxNgIgt3gHXpnYgsidHqfUYwZkasiDGAJt0EgkJ17Dzcljhzccb1oYPSbt%2FS5lnf9IMi%2BN0ZYo9%2FDa2HfvR6HG3WW1K%2FlJfdbLMBk4owomyu0sMY1l%2Fj0iTJniW%2BH4ftIfMOtADHA%3D%3D&trade_no=2017081521001004340200204114&sign_type=RSA2&auth_app_id=2016080600180695&charset=utf-8&seller_id=2088102170208070&method=alipay.trade.page.pay.return&app_id=2016080600180695&out_trade_no=201702021222&version=1.0'

    o = urlparse(return_url)
    query = parse_qs(o.query)
    processed_query = {}
    # 一定要调用pop
    ali_sign = query.pop("sign")[0]

    # 报错ValueError: RSA key format is not supported，就把文件读取出来再创建
    app_private_key_path_string = open(os.path.join(settings.BASE_DIR, r"apps/trade/keys/private_2048.txt")).read()
    alipay_public_key_path_string = open(os.path.join(settings.BASE_DIR, "apps/trade/keys/alipay_key_2048.txt")).read()
    alipay = AliPay(
        # 首先要传一个appid，在沙箱里可以找到
        appid="2016101800713825",
        # 默认的就行
        # app_notify_url是用于用户扫码后没有支付，关闭了页面，然后用户到手机账单里面支付，也就是不是在浏览器页面上支付的，支付宝会发送一个异步的接口，返回支付结果
        app_notify_url="http://127.0.0.1:8000/alipay/return",
        # 自己私钥的路径，也可以写相对路径
        app_private_key_path="../trade/keys/private_2048.txt",
        # 支付宝的公钥，验证支付宝回传消息使用，不是自己的公钥,
        alipay_public_key_path="../trade/keys/alipay_key_2048.txt",
        # app_private_key_path=app_private_key_path_string,
        # alipay_public_key_path=alipay_public_key_path_string,
        debug=True,  # 默认False,
        # 支付成功后跳转的页面，但是如果用户不是在页面 支付的话，这个return_url就没有用了，就要用到app_notify_url了
        return_url="http://127.0.0.1:8000/alipay/return"
    )

    # 反验证
    for key, value in query.items():
        processed_query[key] = value[0]
    # print(alipay.verify(processed_query, ali_sign))

    url = alipay.direct_pay(
        subject="测试订单",
        out_trade_no="202112010009",
        total_amount=1,
        return_url="http://127.0.0.1:8000/alipay/return"
    )
    re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)
    print(re_url)
