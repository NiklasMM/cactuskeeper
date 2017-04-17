from setuptools import find_packages, setup

with open('requirements.txt') as requirements:
    install_requires = requirements.read().splitlines()

with open('test_requirements.txt') as requirements:
    test_requires = requirements.read().splitlines()

setup(
    name='cactuskeeper',
    version='0.1',
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=test_requires,
    entry_points='''
        [console_scripts]
        ck=cactuskeeper.cli:cli
    '''
)
