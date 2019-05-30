from setuptools import find_packages, setup

with open("requirements.txt") as requirements:
    install_requires = requirements.read().splitlines()

with open("dev_requirements.txt") as requirements:
    dev_requirements = requirements.read().splitlines()

setup(
    name="cactuskeeper",
    version="0.1",
    packages=find_packages(),
    install_requires=install_requires,
    extras_require={"dev": dev_requirements},
    entry_points="""
        [console_scripts]
        ck=cactuskeeper.cli:cli
    """,
)
