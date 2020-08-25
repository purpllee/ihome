# coding:utf-8

from flask import Blueprint, current_app, make_response
from flask_wtf import csrf  # 创建出来一个csrf的值

# 提供静态文件的视图
html = Blueprint("web_html", __name__)


#这里主要是想要在访问时不需要127.0.0.1:5000/static/html/index.html,而是用以下的代替
#127.0.0.1:5000/(index.html)
#127.0.0.1:5000/(register.html)
#127.0.0.1:5000/()
#127.0.0.1:5000/favicon.ico  网页标签栏里面的小图片

# 当用户输入127.0.0.1:5000/(index.html)时，下面这个函数会提取出index.html然后从static/html这个目录中找到同名的文件并返回
# 用以实现上面的代替
@html.route("/<re(r'.*'):html_file_name>")
def get_html(html_file_name):
    """提供html文件"""
    # 如果提取出来的为空，表示访问主页index
    if not html_file_name:
        html_file_name = "index.html"
    # favicon.ico不在html文件中,就直接返回
    if html_file_name  != "favicon.ico":
        html_file_name = "html/"+ html_file_name

    # cookie中创建csrf值
    csrf_token = csrf.generate_csrf()

    # flask提供的返回静态文件的方法,这个方法会从static这个目录开始找, make_response可以返回内容或者是页面，这里返回的是页面
    resp = make_response(current_app.send_static_file(html_file_name))

    # 设置cookie
    resp.set_cookie("csrf_token", csrf_token)

    return resp