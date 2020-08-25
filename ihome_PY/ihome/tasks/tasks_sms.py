# coding:utf-8


from celery import Celery
from ihome.libs.yuntongxun.sms import CCP

# 定义celery对象,指明redis为中间数据库，发布的任务先存在这里面
celery_app = Celery("ihome", broker="redis://127.0.0.1:6379/1")

# 再启动celery时，要在运行flask服务器同一路径下，使用celery -A ihome.tasks.tasks_sms worker -l info，不需要精确到函数，只需要精确到函数所在的py文件
@celery_app.task
def send_sms(to, datas, temp_id):
    """发送短信的异步任务"""
    ccp =CCP()
    ccp.send_template_sms(to, datas, temp_id)

