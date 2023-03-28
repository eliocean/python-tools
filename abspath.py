import sys
import os
from functools import wraps


class ABSPath(object):
    """路径处理工具类"""

    @classmethod
    def project_asbpath(self):
        """获取当前项目目录"""
        project_asbpath = sys.path[1].replace("\\", "/")  # 获取当前项目目录,替换斜杠
        return project_asbpath

    @classmethod
    def dir_asbpath(self):
        """获取当前文件所在目录"""
        dir_asbpath = os.getcwd().replace("\\", "/")  # 获取当前文件所在目录,替换斜杠
        # dir_asbpath = sys.path[0].replace("\\", "/") # 获取当前文件所在目录,替换斜杠
        return dir_asbpath

    @classmethod
    def get_file_abspath(self, filepath):
        """使用相对路径拼接绝对路径"""
        return os.path.abspath(os.path.join(os.getcwd(), filepath)).replace("\\", "/")


# 当作装饰器函数来使用
def abspath(func):
    """装饰器函数,替换第一个参数[相对文件路径]为绝对文件路径"""

    @wraps(func)
    def decorate(*args, **kwargs):
        new_args = list(args)
        new_args[0] = ABSPath.get_file_abspath(new_args[0])
        new_args = tuple(new_args)
        return func(*new_args, **kwargs)

    return decorate


@abspath
def read_file_with_decorator(filename='./main.py', num=1):
    print('decorator:', filename, num)


def read_file_no_decorator(filename='./main.py', num=1):
    print('no decorator:', filename, num)


if __name__ == '__main__':
    """测试"""
    print(ABSPath.get_file_abspath(''))
    read_file_with_decorator('./main.py', 10)
    read_file_no_decorator('./main.py', 10)
