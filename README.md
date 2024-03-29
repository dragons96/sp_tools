# SP (Simple Process) 工具 
### 为简化开发而生 (要求Python3.7以上版本)
###
### 安裝方法
#### pip安装:
```
pip install sp_tools
```
#### 源码安装:
##### 1.下载源码
##### 2. 进入源码根目录, 执行命令
```bat
python setup.py sdist bdist_wheel

windows下
pip install dist/sp_tools-{version}.whl

linux下
pip install dist/sp_tools-{version}.tar.gz

```
### 模块导入 
```python
# 注解导入
from sp_tools import *
# 日志模块
from sp_tools.logger import get_logger
log = get_logger()
```
### 当前实现
##### 1.并行注解 @parallel
```python
from sp_tools.annotation import parallel
# 两种方式导入均可 
from sp_tools import parallel
# 异步运行注解(支持 concurrent.futures 包下的ThreadPoolExecutor和ProcessPoolExecutor)
# 默认新创建一个threading.Thread运行
@parallel
def sp_f1():
    print('SP_F1')

sp_f1()    

from concurrent.futures import ThreadPoolExecutor
t = ThreadPoolExecutor(max_workers=10, thread_name_prefix='sp_thread')
@parallel(pool=t)
def sp_f2():
    print('SP_F2')

sp_f2()
# 使用@parallel注解后return获取对象将变为future对象,暂仅支持is_done(), get()方法
```
##### 2.重试注解 @retry
```python
from sp_tools import retry
times = 0
@retry
def sp_f3():
    global times
    times += 1
    if times < 3:
        raise Exception('操作异常')
    print('success')
    
sp_f3()
```
##### 3.日志注解与日志实现 @log
```python
import os
# 开启本地日志文件存储(额外功能)
os.environ.setdefault('logging.FileHandler.open', 'True')
# 设置本地日志文件存储路径(额外功能)
os.environ.setdefault('logging.FileHandler.filename', './global.log')

from sp_tools import log
from sp_tools import get_logger

# 获取日志对象
logger = get_logger()

# 注解打印日志
@log
def sp_f4(p=1):
    logger.info('代码打印日志')
    return 'success'

sp_f4(3)
sp_f4(p=2)
```

##### 4.拓展全局日志(选用)
```python
# 0.0.3 之前的版本需要先设置环境变量配置再引入get_logger依赖, 0.0.3 版本可先引入依赖再设置环境变量配置(0.0.3版本新增延迟初始化)
# 需要在引入全局日志之前注入env修改配置
import os
# 设置全局日志名称
# os.environ.setdefault('logging.name', '全局日志')
# 设置全局日志默认级别
# os.environ.setdefault('logging.level', 'INFO')
# 开启控制台日志记录
# os.environ.setdefault('logging.streamHandler.open', True)
# 设置控制台日志级别
# os.environ.setdefault('logging.streamHandler.level', 'INFO')
# 设置控制台日志格式
# os.environ.setdefault('logging.streamHandler.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# 开启文件日志记录
# os.environ.setdefault('logging.fileHandler.open', False)
# 设置文件存储路径(暂仅支持本地文件存储)
# os.environ.setdefault('logging.fileHandler.filename', './global.log')
# 设置文件写入模式(w:覆盖, a:追加)
# os.environ.setdefault('logging.fileHandler.mode', 'a')
# 设置文件编码格式
# os.environ.setdefault('logging.fileHandler.encoding', 'utf-8')
# 设置文件日志级别
# os.environ.setdefault('logging.fileHandler.level', 'INFO')
# 设置文件日志格式
# os.environ.setdefault('logging.fileHandler.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from sp_tools import get_logger, new_logger
# 直接使用
logger = get_logger()

# 定制化日志对象
myLogger = new_logger('myLogger')

# -------------------------

# 注解使用
from sp_tools import log
@log
def f():
    pass

f()
```
##### 5.自动将当前项目添加至sys.path的autosyspath包 (详细说明见: https://github.com/dragons96/toautosyspath)
```python
# 导入该模块可自建向上检索项目根路径并添加至sys.path中(原理是基于__init__.py文件的向上检索, 请严格规范项目结构, 项目内模块及运行模块应添加__init__.py文件)
import sp_tools.autosyspath
```

### 实战指南
##### 1.注解复用
```python
# 注释事项:
# 1.@parallel注解必须存放在@retry之上, 若@parallel注解放在@retry注解下将无法触发重试(@parallel不会产生异常)
# 2.@parallel注解会导致@log注解耗时统计不准确
from sp_tools import *

logger = get_logger()

@log
@parallel
@retry
def sp_f5(s=2):
    logger.info('SP_F5, s=' + str(s))
    return s + 2

sp_f5(1)
sp_f5(s=4)
```

### 变更说明
##### 2022.06.06 更新
1. 修复内置日志对象bool类型解析问题
2. 内置日志配置参数全部转为驼峰命名
3. 内置日志支持获取新实例(提供new_logger方法, properties参数见以下示例)
```python
from sp_tools import new_logger
logger = new_logger("myLog", {
    'logging': {
        # 全局日志级别
        'level': 'DEBUG',
        'streamHandler': {
            'open': 'True',
            # handler 日志级别
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'fileHandler': {
            'open': 'False',
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'filename': './custom.log',
            'mode': 'a',
            'encoding': 'utf-8',
            'delay': 'False',
        },
        'timedRotatingFileHandler': {
            'open': 'False',
            'level': 'INFO',
            'filename': './timed-rotating.log',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        }
    }
})
# 自定义 handler 或其他 handler 可通过 logger.addHandler方法进行添加
# logger.addHandler(...)
```