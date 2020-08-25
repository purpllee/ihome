# coding:utf-8

from . import api
from flask import request,jsonify, current_app, session
from ihome.utils.response_code import RET
from ihome import redis_store, db
from ihome.models import User
from sqlalchemy.exc import IntegrityError  # 唯一值重复异常
from werkzeug.security import generate_password_hash, check_password_hash
from ihome import constant
import re

@api.route("/users", methods=["post"])
def register():
    """注册
    请求的参数：手机号，短信验证码，密码，确认密码
    参数格式：json数据
    """
    # 获取请求的json数据
    req_dict = request.get_json()
    mobile = req_dict.get("mobile")
    sms_code = req_dict.get("sms_code")
    password = req_dict.get("password")
    password2 = req_dict.get("password2")
    # 校验参数
    if not all([mobile, sms_code, password, password2]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 判断手机号格式是否正确
    if not re.match(r"1[34578]\d{9}",mobile):
        # 表示格式不对
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")

    if password != password2:
        return jsonify(errno=RET.PARAMERR, errmsg="两次密码不一致")

    # 从redis中取出短信验证码，判断短信验证码是否过期
    try:
        real_sms_code = redis_store.get("sms_code_%s"%mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="读取真是短信验证码异常")
    # 删除redis中的短信验证码，防止重复使用校验
    try:
        redis_store.delete("sms_code_%s"%mobile)
    except Exception as e:
        current_app.logger.error(e)

    # 判断用户输入的短信验证码是否正确
    if real_sms_code is None:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码失效")
    # 判断用户的手机号是否注册
    # try:
    #     user = User.query.filter_by(mobile=mobile).first()
    # except Exception as e:
    #     current_app.logger.error(e)
    #
    #     return jsonify(errno=RET.DBERR, errmsg="数据库异常")
    #
    # else:
    #     # 如果user不是None，表示手机号已经注册
    #     if user is not None:
    #         return jsonify(errno=RET.DATAEXIST, errmsg="手机号已经存在")

    # 保存用户的数据到数据库中,可以与判断手机号是否注册写在一起，减少请求数据库的次数
    user = User(name=mobile, mobile=mobile)
    # 不需要再用方法，直接调用属性
    # user.generate_password_hash(password)

    user.password = password  # 设置属性
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        # 出现错误回滚操作
        db.session.rollback()
        # 手机号出现了重复，即已经注册
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg="手机号已经存在")
    except Exception as e:
        # 出现错误回滚操作，回滚到commit之前的状态
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")
    # 不能对用户密码直接进行sha1加密，而是需要加上盐值salt

    # 保存登录状态到session中，即注册后就直接算是登陆了
    session["name"] = user.name
    session["mobile"] = user.mobile
    session["user_id"] = user.id

    return jsonify(errno=RET.OK, errmsg="注册成功")

@api.route("/sessions", methods=["POST"])
def login():
    """用户登录
    参数： 手机号，密码 json
    """
    # 获取参数
    req_dict = request.get_json()
    mobile = req_dict.get("mobile")
    password = req_dict.get("password")
    # 校验参数
    # 参数是否完整
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    # 手机号格式
    if not re.match(r"1[34578]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号各市错误")
    # 判断错误次数是否超过限制，超过限制则返回
    # redis中记录错误次数  “access_nums_请求的ip地址”：次数
    user_ip = request.remote_addr   # 用户的ip地址
    # 试图拿去access_nums这个数据，但是没有，需要等后面incr这个函数创建
    try:
        access_nums = redis_store.get("access_nums_%s"%user_ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if access_nums is not None and int(access_nums)>=constant.LOGIN_ERROR_MAX_TIMES:
            return jsonify(errno=RET.REQERR, errmsg="密码错误次数过多，请稍后重试")
    # 根据手机号查询数据库中的数据
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户信息失败")


    # 用数据库中的密码与用户输入的密码对比
    if user is None or not user.check_password(password):
        # 如果验证失败，记录错误次数，并返回
        try:
            # 这里表示若没有则创建access_nums这个key，若有的话则自动加1
            redis_store.incr("access_nums_%s"%user_ip)
            redis_store.expire("access_nums_%s"%user_ip)
        except Exception as e:
            current_app.logger.error(e)

        return jsonify(errno=RET.DATAERR, errmsg="用户名或密码错误")

    # 验证成功，在session中保存登录状态
    session["name"] = user.name
    session["mobile"] = user.mobile
    session["user_id"] = user.id
    return jsonify(errno=RET.OK, errmsg="登录成功")



@api.route("/session", methods=["GET"])
def check_login():
    """检查登陆状态"""
    # 尝试从session中获取用户的名字
    name = session.get("name")

    # 如果session中数据name名字存在，则表示用户已登录，否则未登录
    if name is not None:
        return jsonify(errno=RET.OK, errmsg="true", data={"name": name})
    else:
        return jsonify(errno=RET.SESSIONERR, errmsg="false")


@api.route("/session", methods=["DELETE"])
def logout():
    """登出"""
    # 清除session数据
    session.clear()
    return jsonify(errno=RET.OK, errmsg="OK")