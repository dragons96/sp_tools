import os
import logging
import logging.handlers
from logging import Logger

_STREAM_HANDLE = 'logging.streamHandler'
_FILE_HANDLE = 'logging.fileHandler'
_ROTATING_FILE_HANDLE = 'logging.rotatingFileHandler'
_TIME_ROTATING_FILE_HANDLE = 'logging.timedRotatingFileHandler'


def get_logger():
    return __log


def new_logger(name, properties: dict = None):
    return _DelayedConfigurationLogger(name, properties=properties)


def _get_env(key, default=None):
    return os.environ.get(key, default)


def _get_properties(properties: dict, key, default=None):
    keys = key.split('.')
    p = properties
    for k in keys:
        if k in p:
            p = p[k]
        else:
            return default
    return p


def _log_handle_env(log_: logging.Logger, path, default_state, handler_type=logging.StreamHandler, *args, **kwargs):
    if eval(_get_env(path + '.open', default_state)):
        handle = handler_type(*args, **kwargs)
        handle.setLevel(eval('logging.' + _get_env(path + '.level', 'INFO').upper()))
        handle.setFormatter(
            logging.Formatter(_get_env(path + '.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')))
        log_.addHandler(handle)


def _log_handle_properties(log_: logging.Logger, properties: dict, path, default_state,
                           handler_type=logging.StreamHandler, *args, **kwargs):
    if eval(_get_properties(properties, path + '.open', default_state)):
        handle = handler_type(*args, **kwargs)
        handle.setLevel(eval('logging.' + _get_properties(properties, path + '.level', 'INFO').upper()))
        handle.setFormatter(
            logging.Formatter(
                _get_properties(properties, path + '.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')))
        log_.addHandler(handle)


def _delay_config(func):
    def wrapper(*args, **kwargs):
        args[0].init_config()
        return func(*args, **kwargs)

    return wrapper


class _DelayedConfigurationLogger(Logger):
    """
    延迟初始化配置的日志对象, 仅用于当前全局日志对象的延迟装载
    """

    def __init__(self, name: str, level=logging.INFO, properties=None):
        super().__init__("_DelayedConfigurationLogger." + name, level)
        self.__delegate = logging.getLogger(name)
        self.__init = False
        self.__properties = properties

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

    @_delay_config
    def handlers_(self):
        return self.__delegate.handlers

    @_delay_config
    def root_(self):
        return self.__delegate.root

    @_delay_config
    def filters_(self):
        return self.__delegate.filters

    @_delay_config
    def disabled_(self):
        return self.__delegate.disabled

    @_delay_config
    def manager_(self):
        return self.__delegate.manager

    @_delay_config
    def parent_(self):
        return self.__delegate.parent

    @_delay_config
    def propagate_(self):
        return self.__delegate.propagate

    @_delay_config
    def level_(self):
        return self.__delegate.level

    def init_config(self):
        """
        从环境变量中初始化日志配置
        """
        if not self.__init:
            if not self.__properties:
                self.__delegate.setLevel(eval('logging.' + _get_env('logging.level', 'INFO').upper()))
                _log_handle_env(self.__delegate, _STREAM_HANDLE, 'True')
                _log_handle_env(self.__delegate, _FILE_HANDLE, 'False', logging.FileHandler,
                                _get_env(_FILE_HANDLE + '.filename', './global.log'),
                                _get_env(_FILE_HANDLE + '.mode', 'a'),
                                _get_env(_FILE_HANDLE + '.encoding', 'utf-8'),
                                eval(_get_env(_FILE_HANDLE + '.delay', 'False')))
                _log_handle_env(self.__delegate, _ROTATING_FILE_HANDLE, 'False', logging.handlers.RotatingFileHandler,
                                _get_env(_ROTATING_FILE_HANDLE + '.filename', './rotating.log'),
                                _get_env(_ROTATING_FILE_HANDLE + '.mode', 'a'),
                                int(_get_env(_ROTATING_FILE_HANDLE + '.maxBytes', 0)),
                                int(_get_env(_ROTATING_FILE_HANDLE + '.backupCount', 0)),
                                _get_env(_ROTATING_FILE_HANDLE + '.encoding', 'utf-8'),
                                eval(_get_env(_ROTATING_FILE_HANDLE + '.delay', 'False')))
                _log_handle_env(self.__delegate, _TIME_ROTATING_FILE_HANDLE, 'False',
                                logging.handlers.TimedRotatingFileHandler,
                                _get_env(_TIME_ROTATING_FILE_HANDLE + '.filename', './rotating.log'),
                                _get_env(_TIME_ROTATING_FILE_HANDLE + '.when', 'h'),
                                int(_get_env(_TIME_ROTATING_FILE_HANDLE + '.interval', 1)),
                                int(_get_env(_TIME_ROTATING_FILE_HANDLE + '.backupCount', 0)),
                                _get_env(_TIME_ROTATING_FILE_HANDLE + '.encoding', 'utf-8'),
                                eval(_get_env(_TIME_ROTATING_FILE_HANDLE + '.delay', 'False')),
                                eval(_get_env(_TIME_ROTATING_FILE_HANDLE + '.utc', 'False')),
                                _get_env(_TIME_ROTATING_FILE_HANDLE + '.atTime')
                                )
            else:
                self.__delegate.setLevel(
                    eval('logging.' + _get_properties(self.__properties, 'logging.level', 'INFO').upper()))
                _log_handle_properties(self.__delegate, self.__properties, _STREAM_HANDLE, 'True')
                _log_handle_properties(self.__delegate, self.__properties, _FILE_HANDLE, 'False',
                                       logging.FileHandler,
                                       _get_properties(self.__properties, _FILE_HANDLE + '.filename',
                                                       './custom.log'),
                                       _get_properties(self.__properties, _FILE_HANDLE + '.mode', 'a'),
                                       _get_properties(self.__properties, _FILE_HANDLE + '.encoding', 'utf-8'),
                                       eval(_get_properties(self.__properties, _FILE_HANDLE + '.delay', 'False')))
                _log_handle_properties(self.__delegate, self.__properties, _ROTATING_FILE_HANDLE, 'False',
                                       logging.handlers.RotatingFileHandler,
                                       _get_properties(self.__properties, _ROTATING_FILE_HANDLE + '.filename',
                                                       './rotating.log'),
                                       _get_properties(self.__properties, _ROTATING_FILE_HANDLE + '.mode', 'a'),
                                       int(_get_properties(self.__properties, _ROTATING_FILE_HANDLE + '.maxBytes', 0)),
                                       int(_get_properties(self.__properties, _ROTATING_FILE_HANDLE + 'backupCount',
                                                           0)),
                                       _get_properties(self.__properties, _ROTATING_FILE_HANDLE + '.encoding', 'utf-8'),
                                       eval(_get_properties(self.__properties, _ROTATING_FILE_HANDLE + '.delay',
                                                            'False')))
                _log_handle_properties(self.__delegate, self.__properties, _TIME_ROTATING_FILE_HANDLE, 'False',
                                       logging.handlers.TimedRotatingFileHandler,
                                       _get_properties(self.__properties, _TIME_ROTATING_FILE_HANDLE + '.filename',
                                                       './timed-rotating.log'),
                                       _get_properties(self.__properties, _TIME_ROTATING_FILE_HANDLE + '.when', 'h'),
                                       int(_get_properties(self.__properties, _TIME_ROTATING_FILE_HANDLE + '.interval',
                                                           1)),
                                       int(_get_properties(self.__properties,
                                                           _TIME_ROTATING_FILE_HANDLE + '.backupCount', 0)),
                                       _get_properties(self.__properties, _TIME_ROTATING_FILE_HANDLE + '.encoding',
                                                       'utf-8'),
                                       eval(_get_properties(self.__properties, _TIME_ROTATING_FILE_HANDLE + '.delay',
                                                            'False')),
                                       eval(_get_properties(self.__properties, _TIME_ROTATING_FILE_HANDLE + '.utc',
                                                            'False')),
                                       _get_properties(self.__properties, _TIME_ROTATING_FILE_HANDLE + '.atTime')
                                       )
            self.__init = True


__log = _DelayedConfigurationLogger('GlobalLogger')
