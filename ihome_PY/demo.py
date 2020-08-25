# coding:utf-8
import functools



def login_required(func):
    @functools.wraps(func)  # 不去改变装饰器装饰的函数
    def wrapper(*arg, **kwargs):
        """wrapper python"""
        pass
    return wrapper


@login_required
def itcast():
    """itcast python"""
    pass


print(itcast.__name__)  # 加装饰器  变为wrapper.__name__
print(itcast.__doc__)