"""
Setup for lookatme.contrib.qrcode
"""


from setuptools import setup, find_namespace_packages
import os


setup(
    name="lookatme.contrib.qrcode",
    version="0.0.0",
    description="Adds qrcode rendering",
    author="",
    author_email="",
    python_requires=">=3.6",
    install_requires=["pyqrcode"],
    packages=find_namespace_packages(include=["lookatme.*"]),
)
