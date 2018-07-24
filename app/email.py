from threading import Thread
from flask import current_app
from flask_mail import Message
from app import mail

def send_async_email(app, msg):
    """发送异步邮件"""
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    """发送邮件"""
    # 主题， 发送者， 接受者
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    # current_app._get_current_object()从代理对象中提取实际的应用实例
    # 将实例作为参数传递给线程
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()
