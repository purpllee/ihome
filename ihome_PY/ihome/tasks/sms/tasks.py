# coding:utf-8


from ihome.tasks.main import celery_app
from ihome.libs.yuntongxun.sms import CCP


# 再启动celery时，要在运行flask服务器同一路径下，使用celery -A ihome.tasks.tasks_sms worker -l info，不需要精确到函数，只需要精确到函数所在的py文件
@celery_app.task
def send_sms(to, datas, temp_id):
    """发送短信的异步任务"""
    ccp = CCP()
    # 可以返回状态值
    return ccp.send_template_sms(to, datas, temp_id)

    # 分出来ihome后就可以将原来的代码注释掉，因为celery直接执行分出来的ihome中的函数
    # pass

