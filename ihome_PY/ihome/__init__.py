#coding:utf-8
from flask import Flask
from config import config_map
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf import CSRFProtect
from logging.handlers import RotatingFileHandler
import redis
import logging  # 日志标准库
from ihome.utils.comments import ReConverter
# 数据库,这里不能用db=SQLAlchemy(app)是因为app爱没有创建出来,但是又不能放在函数里面
# 因为别的程序也需要数据库
db = SQLAlchemy()

# 创建redis链接对象,这里也是因为别的程序需要调用这个
redis_store = None

# logging.error("")  # 错误等级
# logging.warn("") # 警告级别
# logging.info("") #信息提示级别
# logging.debug("")  #记录调试信息

# 配置日志信息
# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG)  # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小 100M、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日记录器
logging.getLogger().addHandler(file_log_handler)



# 工厂模式
def create_app(config_name):
    """
    创建flask的应用对象
    :param config_name: str 配置模式的名字（‘develop’或者"product"）
    :return:
    """

    app = Flask(__name__)
    # 根据配置模式的名字获取配置参数的类
    config_class = config_map.get(config_name)
    # 导入配置
    app.config.from_object(config_class)
    # 使用app初始化db
    db.init_app(app)
    # 初始化redis
    global redis_store
    # config_class存放着生产模式和测试模式两个类
    redis_store = redis.StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT)
    # flask中session_id默认保存到浏览器cookie中，这里需要将其保存回redis，利用flask-session工具
    # 只是需要初始化一次，后面就不需要再用，后面要用的仍然是flask中的session对象,因此放在函数里
    Session(app)
    # 为flask补充csrf防护,原理是在post请求前挂钩子,后面别的程序用的也不是这个对象
    # 这里的函数只是验证cookie和请求体中的csrf_token是否一样，并不提供这个值
    # 开启了csrf时，当用户访问网站时，网站会在cookie中添加csrf的值，等用户向网站发请求时，网站会把这个值带到请求的信息中
    # 与用户cookie中的作对比，相等才能成功发送请求
    CSRFProtect(app)
    # 为flask添加自定义转换器
    app.url_map.converters["re"] = ReConverter
    # 注册蓝图
    from ihome import api_1_0
    app.register_blueprint(api_1_0.api, url_prefix="/api/v1.0")
    # 注册提供静态文件的蓝图
    from ihome import web_html
    app.register_blueprint(web_html.html)
    return app