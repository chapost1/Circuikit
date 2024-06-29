from setuptools import setup, find_packages

setup(
    name="circuikit",
    version="0.1.0",
    description="A versatile tool for Arduino serial monitoring and interaction",
    author="Shachar Tal",
    author_email="stalmail10@gmail.com",
    packages=find_packages(include=['kit', 'services', 'serial_monitor_interface']),
    install_requires=[
        "anyio==4.4.0",
        "attrs==23.2.0",
        "black==24.4.2",
        "certifi==2024.6.2",
        "charset-normalizer==3.3.2",
        "click==8.1.7",
        "h11==0.14.0",
        "httpcore==1.0.5",
        "idna==3.7",
        "mypy-extensions==1.0.0",
        "outcome==1.3.0.post0",
        "packaging==24.1",
        "pathspec==0.12.1",
        "platformdirs==4.2.2",
        "PySocks==1.7.1",
        "requests==2.32.3",
        "selenium==4.21.0",
        "sniffio==1.3.1",
        "sortedcontainers==2.4.0",
        "trio==0.25.1",
        "trio-websocket==0.11.1",
        "typing_extensions==4.12.2",
        "urllib3==2.2.2",
        "wsproto==1.2.0"
    ],
    entry_points={
        'console_scripts': [],
    },
)
