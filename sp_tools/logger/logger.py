import os
import logging
from logging import Logger


def get_logger():
    return __log


def _get_env(key, default=None):
    return os.environ.get(key, default)


def _log_handle(log_: logging.Logger, path, default_state, handler_type=logging.StreamHandler, *args):
    if bool(_get_env(path + '.open', default_state)):
        handle = handler_type(*args)
        handle.setLevel(eval('logging.' + _get_env(path + '.level', 'INFO').upper()))
        handle.setFormatter(
            logging.Formatter(_get_env(path + '.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')))
        log_.addHandler(handle)


def _delay_config(func):
    def wrapper(*args, **kwargs):
        get_logger().init_config()
        return func(*args, **kwargs)
    return wrapper


class _DelayedConfigurationLogger(Logger):
    """
    延迟初始化配置的日志对象, 仅用于当前全局日志对象的延迟装载
    """

    def __init__(self, name: str, level=logging.NOTSET):
        super().__init__("_DelayedConfigurationLogger", level)
        self.__delegate = logging.getLogger(_get_env('logging.name', name))
        self.__init = False

    @_delay_config
    def setLevel(self, level):
        self.__delegate.setLevel(level)

    @_delay_config
    def debug(self, msg, *args, **kwargs):
        self.__delegate.debug(msg, *args, **kwargs)

    @_delay_config
    def info(self, msg, *args, **kwargs):
        self.__delegate.info(msg, *args, **kwargs)

    @_delay_config
    def warning(self, msg, *args, **kwargs):
        self.__delegate.warning(msg, *args, **kwargs)

    @_delay_config
    def warn(self, msg, *args, **kwargs):
        import warnings
        warnings.warn("The 'warn' method is deprecated, "
                      "use 'warning' instead", DeprecationWarning, 2)
        self.__delegate.warn(msg, *args, **kwargs)

    @_delay_config
    def error(self, msg, *args, **kwargs):
        self.__delegate.error(msg, *args, **kwargs)

    @_delay_config
    def exception(self, msg, *args, exc_info=True, **kwargs):
        self.__delegate.exception(msg, *args, exc_info=exc_info, **kwargs)

    @_delay_config
    def critical(self, msg, *args, **kwargs):
        self.__delegate.critical(msg, *args, **kwargs)

    fatal = critical

    @_delay_config
    def log(self, level, msg, *args, **kwargs):
        self.__delegate.log(level, msg, *args, **kwargs)

    @_delay_config
    def findCaller(self, stack_info=False):
        return self.__delegate.findCaller(stack_info=stack_info)

    @_delay_config
    def makeRecord(self, name, level, fn, lno, msg, args, exc_info,
                   func=None, extra=None, sinfo=None):
        return self.__delegate.makeRecord(name, level, fn, lno, msg, args, exc_info, func, extra, sinfo)

    @_delay_config
    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False):
        """
         Not used
        """
        pass

    @_delay_config
    def handle(self, record):
        self.__delegate.handle(record)

    @_delay_config
    def addHandler(self, hdlr):
        self.__delegate.addHandler(hdlr)

    @_delay_config
    def removeHandler(self, hdlr):
        self.__delegate.removeHandler(hdlr)

    @_delay_config
    def hasHandlers(self):
        return self.__delegate.hasHandlers()

    @_delay_config
    def callHandlers(self, record):
        self.__delegate.callHandlers(record)

    @_delay_config
    def getEffectiveLevel(self):
        return self.__delegate.getEffectiveLevel()

    @_delay_config
    def isEnabledFor(self, level):
        return self.__delegate.isEnabledFor(level)

    @_delay_config
    def getChild(self, suffix):
        return self.__delegate.getChild(suffix)

    def init_config(self):
        """
        从环境变量中初始化日志配置
        """
        if not self.__init:
            self.__delegate.setLevel(eval('logging.' + _get_env('logging.level', 'INFO').upper()))
            _log_handle(self.__delegate, 'logging.StreamHandler', True)
            _log_handle(self.__delegate, 'logging.FileHandler', False, logging.FileHandler,
                        _get_env('logging.FileHandler.filename', './global.log'),
                        _get_env('logging.FileHandler.mode', 'a'),
                        _get_env('logging.FileHandler.encoding', 'utf-8'),
                        bool(_get_env('logging.FileHandler.delay', False)))
            self.__init = True


__log = _DelayedConfigurationLogger('GlobalLogger')
