import binascii
import hashlib
import hmac
import time
import random
import requests
from flask_babel import _
from flask import current_app

def get_signature(secret_key, sign_str, sign_method):
    """计算公共参数中的signature"""
    # 用utf-8编码
    sign_str = sign_str.encode('utf-8')
    secret_key = secret_key.encode('utf-8')
    # 根据参数中的sign_method来选择加密方式
    if sign_method == 'HmacSHA256':
        digestmod = hashlib.sha256
    elif sign_method == 'HmacSHA1':
        digestmod = hashlib.sha1
    # 完成加密，生成加密后的数据
    hashed = hmac.new(secret_key, sign_str, hashlib.sha256)
    base64 = binascii.b2a_base64(hashed.digest())[:-1].decode()
    return base64

def sort_dict_to_str(dict_data):
    """将字典按照key进行排序并拼接成请求字符串"""
    # 按照key进行排序
    sorted_dict = dict(
        sorted(dict_data.items(), key=lambda dict_data:dict_data[0]))
    # 拼接成请求字符串
    temp_list = []
    for key, value in sorted_dict.items():
        temp_list.append(str(key) + '=' + str(value))
    return '&'.join(temp_list)

def translate(source_text, source, target):
    """
    翻译
    source: 源语言(如‘en’)
    source_text: 待翻译文本(如‘hello’)
    traget: 目标语言(如’cn)
    """
    if 'TC_TRANSLATOR_KEY' not in current_app.config or \
            not current_app.config['TC_TRANSLATOR_KEY']:
        return _('Error: the translation service is not configured.')
    if 'TC_TRANSLATOR_ID' not in current_app.config or \
            not current_app.config['TC_TRANSLATOR_ID']:
        return _('Error: the translation service is not configured.')
    secret_key = current_app.config['TC_TRANSLATOR_KEY']
    secret_id = current_app.config['TC_TRANSLATOR_ID']
    # UNIX时间戳，记录api请求的时间
    time_data = int(time.time())
    # 随机正整数用来与timestap联合起来防止重放攻击
    nonce_data = int(random.random()*10000)
    # 翻译的api接口地址
    request_url = 'tmt.tencentcloudapi.com'
    # 加密方法
    sign_method='HmacSHA256'
    # 默认为get方法
    request_method = 'GET'
    # 公共参数和接口请求参数
    sign_dict = {
        'Action': 'TextTranslate',
        'Nonce': nonce_data,
        'ProjectId': '0',
        'Region': 'ap-guangzhou',
        'SecretId': secret_id,
        'SignatureMethod': sign_method,
        'Source': source[:2],
        'SourceText': source_text,
        'Target': target[:2],
        'Timestamp': time_data,
        'Version': '2018-03-21',
        }
    # 用于生成signature的str。格式为请求方法+请求主机+请求路径(翻译为空)+请求字符串
    request_str = request_method + request_url + '/?' + \
                    sort_dict_to_str(sign_dict)
    # 计算signature
    signature = get_signature(secret_key,request_str,sign_method)
    # 将signature添加到请求参数中
    sign_dict['Signature'] = signature
    # 提交请求
    r = requests.get(url='https://'+request_url, params=sign_dict)
    # print(r.text)
    if r.status_code != 200:
        print(r.status_code)
        return _('Error: the translation service failed.')
    try:
        r = r.json()
        target_text = r['Response']['TargetText']
        return target_text
    except:
        return _('Error: translation failed.')

# print(translate('hello', 'en', 'zh'))
