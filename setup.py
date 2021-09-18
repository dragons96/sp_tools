try:
    from setuptools import setup
except:
    from distutils.core import setup
import setuptools

setup(
    name='sp_tools',
    author='dragons',
    version='0.0.1',
    description='为简化Python开发而生',
    long_description='Python基础开发工具包',
    author_email='521274311@qq.com',
    url='https://gitee.com/kingons/sp_tools',
    packages=setuptools.find_packages(),
    install_requires=[
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries',
    ],
    zip_safe=True,
)
