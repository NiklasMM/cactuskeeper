from setuptools import setup

setup(
    name='cactuskeeper',
    version='0.1',
    py_modules='cactuskeeper',
    install_requires=[
        'Click',
        'gitpython'
    ],
    entry_points='''
        [console_scripts]
        ck=cactuskeeper.cli:cli
    '''
)
