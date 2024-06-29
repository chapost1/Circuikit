from setuptools import setup, find_packages

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements_raw = fh.read()
    requirements = requirements_raw.split("\n")

setup(
    name="circuikit",
    version="0.1.0",
    description="A versatile tool for Arduino serial monitoring and interaction",
    author="Shachar Tal",
    author_email="stalmail10@gmail.com",
    packages=find_packages(exclude=["./examples"]),
    install_requires=requirements,
)
