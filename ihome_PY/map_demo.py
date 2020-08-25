# coding:utf-8

li1 = [1, 2, 3, 4]
li2 = [2, 3, 4, 5]
# 在python2中若不对应，少的数的格式则为None
# python3中不对应，则只处理对应的，多出来的数不管
# li2 = [2, 3]


def add(num1, num2):
    return num1+num2


ret = map(add, li1, li2)


def add_self(num):
    return num+2


ret1 = map(add_self, li1)


# python2中直接返回列表
# python3返回的是一个对象，需要print(list(ret1))才能返回列表

print(ret1)
