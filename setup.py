import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

try:
    README = open(os.path.join(here, 'README.md'), encoding='utf-8').read()
except:
    README = ""

setup(
    name="aliyun-ddns-client",
    version="0.4",
    description="DDNS client for aliyun",
    install_requires=[
        "requests",
    ],
    long_description_content_type="text/markdown",
    long_description=README,
    packages=find_packages(),
    platforms='any',
    zip_safe=True,
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'aliyun-ddns=aliyun_ddns.ddns:main',
        ],
    },
)
