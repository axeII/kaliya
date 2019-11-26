from setuptools import setup, find_packages

setup(
    name="Kaliya",
    version="0.7.0",
    url="https://github.com/axeII/kaliya",
    author="axell",
    author_email="axell@proton.ch",
    description="Website image scrapper",
    packages=find_packages(),    
    install_requires=["requests >= 2.0.0", "click >= 6.0.0", "bs4 >= 0.0.1"],
)
