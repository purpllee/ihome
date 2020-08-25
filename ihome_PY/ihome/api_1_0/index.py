#coding:utf-8

from . import api
# 放在这里导致循环导包
# from ihome import db
from ihome import models
import logging
from flask_migrate import current_app


@api.route("/index")
def index():
    current_app.logger.error("error msg")
    current_app.logger.warn("warn msg")
    current_app.logger.info("info msg")
    current_app.logger.debug("debug msg")
    return "index page"
