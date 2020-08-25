# coding:utf-8

import redis


class Config(object):
    """配置信息"""
    DEBUG = True
    SECRET_KEY = "dkasl;djoj38askl"
    # 创建数据库
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@127.0.0.1:3306/ihome_python04'
    SQLALCHEMY_TRACK_MODIFICATIONS= True
    # redis
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    # flask-session配置
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_USE_SINGER = True  # 在cookie利用session时，也会有个session_Id存在cookiez中，这里对cookie中的session_id进行隐藏处理
    PERMANENT_SESSION_LIFETIME = 86400  # session数据的有效期

class DevelopmentConfig(Config):
    """开发模式下的配置信息"""
    DEBUG = True  # 调试模式下log日志信息无论你调到那个等级，对会在debug这个等级

class ProductConfig(Config):
    """生产环境下的配置信息"""
    pass


config_map = {
    "develop":DevelopmentConfig,
    "product": ProductConfig,
}