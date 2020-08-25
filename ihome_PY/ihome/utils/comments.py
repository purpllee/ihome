# coding:utf-8
from werkzeug.routing import BaseConverter
from flask import session,jsonify,g
from ihome.utils.response_code import RET
import functools
# 定义正则转化器
class ReConverter(BaseConverter):
    """"""
    def __init__(self,url_map, regex):
        # 调用父类的初始化方法
        super(ReConverter, self).__init__(url_map)
        # 保存正则表达式
        self.regex = regex

# 登录验证装饰器
def login_required(view_function):
    @functools.wraps(view_function)
    def wrapper(*args,**kwargs):
        # 判断用户的登录状态
        user_id = session.get("user_id")
        # 如果用户登陆了，直接执行视图函数
        if user_id is not None:
            # 讲user.id保存到g对象中，在试图函数可以通过g对象保存数据
            g.user_id = user_id
            return view_function(*args, **kwargs)
        else:
            # 如果未登录，返回json数据
            return jsonify(errno=RET.SESSIONERR, errmsg="用户未登陆")

    return wrapper



