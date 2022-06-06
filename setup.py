try:
    from setuptools import setup
except:
    from distutils.core import setup
import setuptools

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='sp_tools',
    author='dragons',
    version='0.0.4',
    description='为简化Python开发而生',
    long_description=long_description,
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
