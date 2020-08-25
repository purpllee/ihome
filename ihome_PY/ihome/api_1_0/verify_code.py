# coding:utf-8

from . import api
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store
from ihome import constant
from flask import current_app, jsonify, make_response, request
from ihome.utils.response_code import RET
from ihome.models import User
from ihome.libs.yuntongxun.sms import CCP
# from ihome.tasks.tasks_sms import send_sms
from ihome.tasks.sms.tasks import send_sms
import random

# GET 127.0.0.1/api/v1.0/image_code/<image_code_id>>
@api.route("/image_codes/<image_code_id>")
def get_image_code(image_code_id):
    """
    获取图片验证码
    image_code_id:图片验证码编号
    :return: 正常：验证码图片  异常：返回json
    """
    # 1.提取参数，已经提取出来
    # 2.检验参数， 不传参数无法进入网页，相当于已经检验
    # 3.业务逻辑处理
    # 生成验证码图片
    # 名字  真实文本  图片数据
    name, text, image_data = captcha.generate_captcha()
    # 讲验证码真实值和id保存到redis,并设置有效期，使用hash类型时只能整体设置
    # redis数据类型  字符串 列表 哈希 set
    # redis_store.set("image_code_%s"%image_coed_id,text)
    # redis_store.expire("image_code%s"%image_coed_id, constant.IMAGE_CODE_REDIS_EXPIRES)
    # 上面两句可整合为一句
    try:
        redis_store.setex("image_code_%s"%image_code_id, constant.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        # 记录日志
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="save image code failed")
    # 4.返回值
    resp = make_response(image_data)
    resp.headers["Content-type"] = "image/jpg"
    return resp

# 操作数据库，联网操作和操作第三方库时都需要用try
# 没有使用celery时发送短信的代码
# GET /api/v1.0/sms_codes/<mobile>?image_code=xxx&image_code_id=xxx
# @api.route("/sms_codes/<re(r'1[34578]\d{9}'):mobile>")
# def get_sms_code(mobile):
#     # 获取参数
#     image_code = request.args.get("image_code")
#     image_code_id = request.args.get("image_code_id")
#     # 校验参数
#     if not all([image_code, image_code_id]):
#         #表示参数不完整
#         return jsonify(errno=RET.PARAMERR, errmsg="paramas lost")
#     # 业务逻辑处理
#     # 从redis去除真是的图片验证码，与用户填写的进行对比
#     try:
#         real_image_code = redis_store.get("image_code_%s"%image_code_id)
#     except Exception as e:
#         current_app.logger.error(e)
#         return jsonify(errno="RET.DBERR", errmsg="redis database failed")
#     # 判断图片验证码是不是已经过期
#     if real_image_code is None:
#         # 已经过期了
#         return jsonify(errno=RET.NODATA, errmsg="图片验证码失效")
#     # 删除redis图片验证码，防止一个验证码可以重复验证，
#     try:
#         redis_store.delete("image_code_%s" %image_code_id)
#     except Exception as e:
#         current_app.logger.error(e)
#     # 与用户填写的验证码进行比较
#     if real_image_code.lower() != image_code.lower():
#         # 验证码错误时
#         return jsonify(errno=RET.DATAERR, errmsg="图片验证码错误")
#
#     # 判断对于这个手机号在60s内有无之前的记录，有的话则不接受处理
#     try:
#         send_flag = redis_store.get("send_sms_code_%s"%mobile)
#     except Exception as e:
#         current_app.logger.error(e)
#     else:
#         if send_flag is not None:
#             #表示60s内有过发送记录
#             return jsonify(errno=RET.REQERR, errmsg="请求过于频繁")
#
#     # 并且判断手机号是否已注册
#     try:
#         user = User.query.filter_by(mobile=mobile).first()
#     except Exception as e:
#         current_app.logger.error(e)
#     else:
#         # 如果user不是None，表示手机号已经注册
#         if user is not None:
#             return jsonify(errno=RET.DATAEXIST, errmsg="手机号已经存在")
#     # 如果没有注册，生成六位短信验证码，并将其保存到redis中
#     sms_code = "%06d"%random.randint(0,999999)
#     # 保存真实的验证码
#     try:
#         redis_store.setex("sms_code_%s"%mobile, constant.SMS_CODE_REDIS_EXPIRES, sms_code)
#         # 保存发给这个手机的记录，避免60s内重复请求发短信验证码
#         redis_store.setex("send_sms_code_%s"%mobile, constant.SEND_SMS_CODE_REDIS_EXPIRES, 1)
#     except Exception as e:
#         current_app.logger.error(e)
#         return jsonify(errno=RET.DBERR, errmsg="保存短信验证码异常")
#     # 发送短信
#     try:
#         ccp = CCP()
#         result = ccp.send_template_sms(mobile, [sms_code, int(constant.SMS_CODE_REDIS_EXPIRES/60)], 1)
#     except Exception as e:
#         current_app.logger.error(e)
#         return jsonify(errno=RET.THIRDERR, errmsg="发送异常")
#     if result == 0:
#         # 发送成功
#         return jsonify(errno=RET.OK, errmsg="发送成功")
#     else:
#         return jsonify(errno=RET.THIRDERR, errmsg="发送失败")
#     # 返回值



# GET /api/v1.0/sms_codes/<mobile>?image_code=xxx&image_code_id=xxx



# 利用celery异步发送短信代码
@api.route("/sms_codes/<re(r'1[34578]\d{9}'):mobile>")
def get_sms_code(mobile):
    # 获取参数
    image_code = request.args.get("image_code")
    image_code_id = request.args.get("image_code_id")
    # 校验参数
    if not all([image_code, image_code_id]):
        #表示参数不完整
        return jsonify(errno=RET.PARAMERR, errmsg="paramas lost")
    # 业务逻辑处理
    # 从redis去除真是的图片验证码，与用户填写的进行对比
    try:
        real_image_code = redis_store.get("image_code_%s"%image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno="RET.DBERR", errmsg="redis database failed")
    # 判断图片验证码是不是已经过期
    if real_image_code is None:
        # 已经过期了
        return jsonify(errno=RET.NODATA, errmsg="图片验证码失效")
    # 删除redis图片验证码，防止一个验证码可以重复验证，
    try:
        redis_store.delete("image_code_%s" %image_code_id)
    except Exception as e:
        current_app.logger.error(e)
    # 与用户填写的验证码进行比较
    if real_image_code.lower() != image_code.lower():
        # 验证码错误时
        return jsonify(errno=RET.DATAERR, errmsg="图片验证码错误")

    # 判断对于这个手机号在60s内有无之前的记录，有的话则不接受处理
    try:
        send_flag = redis_store.get("send_sms_code_%s"%mobile)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if send_flag is not None:
            #表示60s内有过发送记录
            return jsonify(errno=RET.REQERR, errmsg="请求过于频繁")

    # 并且判断手机号是否已注册
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
    else:
        # 如果user不是None，表示手机号已经注册
        if user is not None:
            return jsonify(errno=RET.DATAEXIST, errmsg="手机号已经存在")
    # 如果没有注册，生成六位短信验证码，并将其保存到redis中
    sms_code = "%06d"%random.randint(0,999999)
    # 保存真实的验证码
    try:
        redis_store.setex("sms_code_%s"%mobile, constant.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 保存发给这个手机的记录，避免60s内重复请求发短信验证码
        redis_store.setex("send_sms_code_%s"%mobile, constant.SEND_SMS_CODE_REDIS_EXPIRES, 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存短信验证码异常")
    # 发送短信
    # celery异步发送短信
    result = send_sms.delay(mobile, [sms_code, int(constant.SMS_CODE_REDIS_EXPIRES/60)], 1)  # delay（）调用后立即返回，相当于将任务放入了celery任务队列
    # 返回的是异步执行结果对象,就是存在redis2号数据库中的BACKEND的一个对象
    print(result.id)
    # 通过这个get方法来获取redis中的结果,默认是阻塞的，会等到celery有了执行结果后再返回
    # get方法也接收参数timeout，即超时时间，超过这个时间celery还拿不到结果则直接返回
    ret = result.get()
    print(ret)
    # 发送成功
    return jsonify(errno=RET.OK, errmsg="发送成功")
