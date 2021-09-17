import threading
from concurrent.futures import Executor
from types import FunctionType, MethodType
import logging
import traceback
from ..logger import get_logger
import time

__log = get_logger()


def annotation(func):
    """
    注解声明, 强制要求可用注解加上注解声明, 以区分普通方法与注解方法
    """
    return func


@annotation
def extended_annotation(func):
    """
    优化注解语法糖, 支持 @xxx 或 @xxx() 写法, 不支持第一个参数为function或method类型的注解
    """

    def wrapper(*args, **kwargs):
        lens = len(args)
        if lens == 1 and (isinstance(args[0], FunctionType) or isinstance(args[0], MethodType)):
            return func(None)(*args, **kwargs)
        return func(*args, **kwargs)

    return wrapper


@annotation
def extended_classmethod(func):
    """
    拓展@classmethod支持
    """

    def wrapper(*args, **kwargs):
        if len(args) >= 2 and type(args[1]) == args[0]:
            args = args[1:]
        return func(*args, **kwargs)

    return wrapper


@annotation
@extended_annotation
def log(func_name=None, log_=__log, level_=logging.INFO):
    """
    日志注解
    """

    def wrapper(func):
        @extended_classmethod
        def _execute(*args, **kwargs):
            start_time = int(time.time() * 1000)
            result = func(*args, **kwargs)
            log_.log(level_, '方法名:{}, 参数: {}(*args) {}(**kwargs), 返回值: {}, 耗时: {}ms'
                     .format(func_name if type(func_name) == str else func.__name__, args, kwargs, result,
                             int(time.time() * 1000) - start_time))
            return result

        return _execute

    return wrapper


@annotation
@extended_annotation
def retry(func_name=None, retry_times=10, wait=5, default_return_value={}):
    """
    可重试
    """

    def wrapper(func):
        @extended_classmethod
        def _execute(*args, **kwargs):
            retry_ts = retry_times
            while retry_ts > 0:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    __log.warning(
                        f"方法名:{func_name if type(func_name) == str else func.__name__}, 参数: {args}(*args) {kwargs}(**kwargs), 发生异常: {traceback.format_exc()}, 当前剩余重试次数:{retry_ts}" + f", 等待:{wait}秒后重试" if retry_ts > 0 else "")
                    retry_ts -= 1
                    time.sleep(wait)
            return default_return_value

        return _execute

    return wrapper


@annotation
@extended_annotation
def parallel(func_name=None, pool: Executor = None):
    """
    并行, 使用方式: @parallel
    """

    def wrapper(func):
        @extended_classmethod
        def _execute(*args, **kwargs) -> SimpleFuture:
            if pool is None:
                t = SimpleThread(func, *args, **kwargs)
                t.start()
                return SimpleFuture(thread=t)
            return SimpleFuture(future=pool.submit(func, *args, **kwargs))

        return _execute

    return wrapper


class SimpleThread(threading.Thread):
    """
    简单线程池(可获取返回结果)
    """

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.result = None
        self.exception = None
        self.finish = 0

    def run(self):
        try:
            self.result = self.func(*self.args, **self.kwargs)
        except Exception as e:
            self.exception = e
        finally:
            self.finish = 1

    def is_done(self):
        return self.finish == 1

    def get(self):
        if self.exception is not None:
            raise self.exception
        return self.result


class SimpleFuture:
    """
    简单future
    """
    __default_wait_interval = 0.001

    def __init__(self, thread=None, future=None):
        self.__thread = thread
        self.__future = future

    def is_done(self):
        if self.__thread is not None:
            return self.__thread.is_done()
        return self.__future.done()

    def get(self, timeout=None):
        if self.__thread is not None:
            if timeout is not None:
                begin_time = int(time.time())
                cur_time = int(time.time())
            while not self.is_done():
                time.sleep(self.__default_wait_interval)
                if timeout is not None:
                    cur_time += self.__default_wait_interval
                    if cur_time - begin_time >= timeout:
                        raise Exception(f'SimpleFuture: {self} 获取数据等待时间超出限制时间: {timeout} s')
            return self.__thread.get()
        return self.__future.result(timeout=timeout)