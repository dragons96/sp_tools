# SP (Simple Process) 工具 
### 为简化开发而生 (要求Python3.7以上版本)
###
### 本地安裝方法
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
# 需要在引入全局日志之前注入env修改配置
import os
# 设置全局日志名称
# os.environ.setdefault('logging.name', '全局日志')
# 设置全局日志默认级别
# os.environ.setdefault('logging.level', 'INFO')
# 开启控制台日志记录
# os.environ.setdefault('logging.StreamHandler.open', True)
# 设置控制台日志级别
# os.environ.setdefault('logging.StreamHandler.level', 'INFO')
# 设置控制台日志格式
# os.environ.setdefault('logging.StreamHandler.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# 开启文件日志记录
# os.environ.setdefault('logging.FileHandler.open', False)
# 设置文件存储路径(暂仅支持本地文件存储)
# os.environ.setdefault('logging.FileHandler.filename', './global.log')
# 设置文件写入模式(w:覆盖, a:追加)
# os.environ.setdefault('logging.FileHandler.mode', 'a')
# 设置文件编码格式
# os.environ.setdefault('logging.FileHandler.encoding', 'utf-8')
# 设置文件日志级别
# os.environ.setdefault('logging.FileHandler.level', 'INFO')
# 设置文件日志格式
# os.environ.setdefault('logging.FileHandler.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from sp_tools import get_logger
# 直接使用
logger = get_logger()

# -------------------------

# 注解使用
from sp_tools import log
@log
def f():
    pass

f()
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