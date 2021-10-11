import os
import logging


def get_logger():
    return __log


def __get_env(key, default=None):
    return os.environ.get(key, default)


def __log_handle(log_: logging, path, stat, handler_type=logging.StreamHandler, *args):
    if bool(__get_env(path + '.open', stat)):
        handle = handler_type(*args)
        handle.setLevel(eval('logging.' + __get_env(path + '.level', 'INFO').upper()))
        handle.setFormatter(
            logging.Formatter(__get_env(path + '.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')))
        log_.addHandler(handle)


__log = logging.getLogger(__get_env('logging.name', "全局日志"))
__log.setLevel(eval('logging.' + __get_env('logging.level', 'INFO').upper()))
# 控制台
__log_handle(__log, 'logging.StreamHandler', True)
# 文件
__log_handle(__log, 'logging.FileHandler', False, logging.FileHandler,
             __get_env('logging.FileHandler.filename', './global.log'),
             __get_env('logging.FileHandler.mode', 'a'),
             __get_env('logging.FileHandler.encoding', 'utf-8'),
             bool(__get_env('logging.FileHandler.delay', False)))
