from threading import Thread
from flask import render_template
from flask_mail import Message
from app import mail, app



def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Microblog] Reset Your Password',
               sender=app.config['MAIL_USERNAME'],
               recipients=[user.email],     #邮箱地址
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))

# 异步发送邮件
def send_async_email(app, msg):
    with app.app_context():     #上下文管理器
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    # 创建线程对象(Thread(target=send_async_email, args=(app, msg)));  send_async_email指定要执行的函数,args=(app, msg) =>函数的参数
    Thread(target=send_async_email, args=(app, msg)).start()