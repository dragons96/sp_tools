# SP 工具 
### 为简化开发而生 (要求Python3.7以上版本)
###
### 本地安裝方法
##### 1.下载源码
##### 2.python setup.py sdist bdist_wheel
##### 3.windows下pip install dist/sp_tools-{version}.whl, linux下pip install dist/sp_tools-{version}.tar.gz
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
### 实战指南
##### 1.注解复用
```python
# 注释事项:
# 1.@parallel注解必须存放在@retry之上, 若@parallel注解放在@retry注解下将无法触发重试(@parallel不会产生异常)
# 2.@parallel注解会导致@log注解耗时统计不准确
# 3.方法之上的非第一个注解均需要加上func_name参数,否则会导致这些注解日志名称记录异常(具体示例如下图所示)
from sp_tools import *

logger = get_logger()

@parallel(func_name='sp_f5')
@retry(func_name='sp_f5')
@log
def sp_f5(s=2):
    logger.info('SP_F5, s=' + str(s))
    return s + 2

sp_f5(1)
sp_f5(s=4)
```