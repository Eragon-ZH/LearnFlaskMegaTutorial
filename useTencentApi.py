import binascii
import hashlib
import hmac
import time
import random
import requests

secretId = ""
secretKey = ""
def getSignature(secretKey, signStr, signMethod):
    """计算公共参数中的signature"""
    # 用utf-8编码
    signStr = signStr.encode("utf-8")
    secretKey = secretKey.encode("utf-8")
    # 根据参数中的signMethod来选择加密方式
    if signMethod == 'HmacSHA256':
        digestmod = hashlib.sha256
    elif signMethod == 'HmacSHA1':
        digestmod = hashlib.sha1
    # 完成加密，生成加密后的数据
    hashed = hmac.new(secretKey, signStr, hashlib.sha256)
    base64 = binascii.b2a_base64(hashed.digest())[:-1].decode()
    return base64

def sortDictToStr(dictData):
    """将字典按照key进行排序并拼接成请求字符串"""
    # 按照key进行排序
    sorted_dict = dict(
        sorted(dictData.items(), key=lambda dictData:dictData[0]))
    # 拼接成请求字符串
    tempList = []
    for eveKey, eveValue in sorted_dict.items():
        tempList.append(str(eveKey) + "=" + str(eveValue))
    return "&".join(tempList)

def translate(source, sourceText, target):
    """
    翻译
    source: 源语言(如‘en’)
    sourceText: 待翻译文本(如‘hello’)
    traget: 目标语言(如’cn)
    """
    # UNIX时间戳，记录api请求的时间
    timeData = int(time.time())
    # 随机正整数用来与timestap联合起来防止重放攻击
    nonceData = int(random.random()*10000)
    # 翻译的api接口地址
    requestUrl = "tmt.tencentcloudapi.com"
    # 加密方法
    signMethod="HmacSHA256"
    # 默认为get方法
    requestMethod = "GET"
    # 公共参数和接口请求参数
    signDictData = {
        "Action": "TextTranslate",
        "Nonce": nonceData,
        "ProjectId": "0",
        "Region": "ap-guangzhou",
        "SecretId": secretId,
        "SignatureMethod": signMethod,
        "Source": source,
        "SourceText": sourceText,
        "Target": target,
        "Timestamp": timeData,
        "Version": "2018-03-21",
        }
    # 用于生成signature的str。格式为请求方法+请求主机+请求路径(翻译为空)+请求字符串
    requestStr = requestMethod + requestUrl + '/?' + \
                    sortDictToStr(signDictData)
    # 计算signature
    signature = getSignature(secretKey,requestStr,signMethod)
    # 将signature添加到请求参数中
    signDictData['Signature'] = signature
    # 提交请求
    r = requests.get(url='https://'+requestUrl, params=signDictData)
    print(r.text)
    # r = r.json()
    try:
        target_text = r['Response']['TargetText']
        return target_text
    except:
        return ''

print(translate('en', 'hello', 'cn'))
