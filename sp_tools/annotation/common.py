import threading
from concurrent.futures import Executor
from types import FunctionType, MethodType
import logging
import traceback
from ..logger import get_logger
import time
import functools

__log = get_logger()


def annotation(func):
    """
    注解声明, 强制要求可用注解加上注解声明, 以区分普通方法与注解方法
    """
    return func


@annotation
def extended_annotation(func, default_=False):
    """
    优化注解语法糖, 支持 @xxx 或 @xxx() 写法,
    不支持只有一个参数且为function或method且*args方式输入的注解
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        lens = len(args)
        if lens == 1 and (isinstance(args[0], FunctionType) or isinstance(args[0], MethodType)):
            return func(default_)(*args, **kwargs)
        return func(*args, **kwargs)

    return wrapper


@annotation
def extended_classmethod(func):
    """
    拓展@classmethod支持
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if len(args) >= 2 and type(args[1]) == args[0]:
            args = args[1:]
        return func(*args, **kwargs)

    return wrapper


@annotation
def extended_ignore(condition: bool, origin_func):
    """
    拓展忽略注解功能
    :param condition: true 忽略， false 不忽略
    :param origin_func: 实际方法
    :return: function
    """

    def wrapper(func):
        @functools.wraps(origin_func)
        def _execute(*args, **kwargs):
            if not condition:
                return func(*args, **kwargs)
            return origin_func(*args, **kwargs)

        return _execute

    return wrapper


@annotation
@extended_annotation
def log(ignore=False, log_=__log,
        format: str = '\nRecorder: @log\nMethod: {method_}\nParameters: {args_}(*args) {kwargs_}(**kwargs)\nReturn: {return_}\nCost: {cost_}ms',
        level_=logging.INFO,
        err_enable=True,
        err_format: str = '@Recorder: @log\nMethod: {method_}\nParameters: {args_}(*args) {kwargs_}(**kwargs)\nCost: {cost_}ms\nErr: {ex_}',
        err_level=logging.ERROR):
    """
    日志注解 使用方式:
        @log
        def f():
            pass
    :param ignore: 是否忽略该注解
    :param log_: 日志对象(默认使用内置全局日志)
    :param format: 正常信息输出格式
    :param level_: 正常信息日志输出级别
    :param err_enable: 是否开启异常日志记录
    :param err_format: 异常日志输出格式
    :param err_level: 异常日志输出级别
    """

    def wrapper(func):
        @functools.wraps(func)
        @extended_ignore(ignore, func)
        @extended_classmethod
        def _execute(*args, **kwargs):
            start_time = int(time.time() * 1000)
            try:
                result = func(*args, **kwargs)
                log_.log(level_, format.format(method_=func.__name__, args_=args, kwargs_=kwargs, return_=result,
                                               cost_=int(time.time() * 1000) - start_time))
                return result
            except Exception as e:
                if err_enable:
                    log_.log(err_level, err_format.format(method_=func.__name__, args_=args, kwargs_=kwargs,
                                                          ex_=traceback.format_exc(), ex_msg_=str(e),
                                                          cost_=int(time.time() * 1000) - start_time))
                raise e

        return _execute

    return wrapper


@annotation
@extended_annotation
def retry(ignore=False, retry_times=10, ex=Exception, interval=5,
          default_return_value=None,
          err_log_enable: bool = True,
          err_log_=__log,
          err_level=logging.WARNING,
          err_format: str = '\nRecorder: @retry\nMethod: {method_}\nParameters: {args_}(*args) {kwargs_}(**kwargs)\nRemainRetryTimes: {remain_retry_}\nRemainRetryInterval:{remain_retry_interval_}\nErr: {ex_}'):
    """
    重试注解, 使用方式:
        @retry
        def f():
            pass
    :param ignore: 是否忽略该注解
    :param retry_times: 重试次数
    :param ex: 指定异常类型(即仅只对设定的异常进行重试), 支持使用tuple or list方式设定多种异常类型
    :param interval: 重试间隔, 单位: s
    :param default_return_value: 重试后仍然失败返回的默认值，若为None则抛出最后一次重试的异常，否则返回该默认值
    :param err_log_enable: 是否开启重试日志
    :param err_log_: 日志对象(默认使用内置全局日志)
    :param err_level: 重试日志记录等级
    :param err_format: 重试日志格式化格式
    """

    def wrapper(func):

        @functools.wraps(func)
        @extended_ignore(ignore, func)
        @extended_classmethod
        def _execute(*args, **kwargs):
            def ex_retry_check(exc, e_type):
                if isinstance(exc, list) or isinstance(exc, tuple):
                    for e in exc:
                        if issubclass(e_type, e):
                            return True
                    return False
                return issubclass(e_type, exc)

            retry_ts = retry_times
            latest_err = None
            while retry_ts >= 0:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    latest_err = e
                    if ex_retry_check(ex, type(e)):
                        if err_log_enable:
                            err_log_.log(err_level, err_format.format(method_=func.__name__, args_=args, kwargs_=kwargs,
                                                                      ex_=traceback.format_exc(), ex_msg_=str(e),
                                                                      remain_retry_=retry_ts,
                                                                      remain_retry_interval_=interval))
                        retry_ts -= 1
                        time.sleep(interval)
                    else:
                        raise e
            if default_return_value is None:
                raise latest_err
            return default_return_value

        return _execute

    return wrapper


@annotation
@extended_annotation
def parallel(ignore=False, pool: Executor = None):
    """
    并行, 使用方式:
        @parallel
        def f():
            pass
    :param ignore: 是否忽略该注解
    :param pool: 当前仅支持concurrent.futures.ThreadPoolExecutor线程池, 若不传该值默认新建线程运行
    :return
    """

    def wrapper(func):
        @functools.wraps(func)
        @extended_ignore(ignore, func)
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
