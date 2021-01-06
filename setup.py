from distutils.core import setup

import setuptools

from golem_ci import VERSION

setup(
    name='golem_ci',
    version=VERSION,
    description='Golem CI',
    author='hhio618',
    install_requires=["click>=7.0",
                      "appdirs",
                      "retrying",
                      "pyOpenSSL",
                      "requests[security]",
                      "requests-toolbelt",
                      "beautifultable==0.8.0",
                      "pytz",
                      "tzlocal",
                      "pyyaml>=3.13se",
                      "websocket-client"],
    author_email='hhio618@gmail.com',
    url='https://github.com/hhio618/golem-ci',
    keywords=['Golem', 'CI'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "License :: OSI Approved :: GPLv3 License",
    ],
    entry_points='''
        [console_scripts]
        golem_ci=golem_ci.cli:base
    ''',

)