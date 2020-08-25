# -*- coding: utf-8 -*-
# flake8: noqa
from qiniu import Auth, put_data, etag
import qiniu.config
#需要填写你的 Access Key 和 Secret Key
access_key = 'bR5NIA68JXHSiy3RagQw1GstYQ6yR1Q9zuhgMWNb'
secret_key = 'ZP4-OjkJ3ipdC1P7NVNFGqOwBSH0hhTx5bBYIQmF'


def storage(file_data):
    """
    上传图片到七牛
    :param file_data: 要上传的图片二进制数据
    :return:
    """
    #构建鉴权对象
    q = Auth(access_key, secret_key)
    #要上传的空间
    bucket_name = 'lhyipython'
    #上传后保存的文件名
    # key = 'my-python-logo.png'
    #生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)
    #要上传文件的本地路径
    # localfile = './sync/bbb.jpg'
    # 这里直接使用put_data上传图片二进制数据
    ret, info = put_data(token, None, file_data)
    if info.status_code ==200:
        #表示上传成功,返回文件名
        return ret.get("key")
    else:
        # 上传失败
        raise Exception("上传七牛失败")


if __name__ == "__main__":
    with open("./1.png", "rb") as f:
        file_data = f.read()
        storage(file_data)