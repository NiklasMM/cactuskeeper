from setuptools import setup, find_packages

setup(
    name='cactuskeeper',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'Click',
        'gitpython'
    ],
    entry_points='''
        [console_scripts]
        ck=cactuskeeper.cli:cli
    '''
)
