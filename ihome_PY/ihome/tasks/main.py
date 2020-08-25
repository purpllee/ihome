# coding:utf-8
# 相比较于直接在tasks创建tasks_sms,用创建目录的形势更加通用
from celery import Celery
from ihome.tasks import config
# 定义celery对象
celery_app = Celery("ihome")

# 引入配置信息
celery_app.config_from_object(config)

# 自动搜寻异步任务,任务的名字需要固定位tasks才能找到
celery_app.autodiscover_tasks(["ihome.tasks.sms"])


