from setuptools import setup, find_packages

setup(
    name="b-heaters-control",
    version="1.0.0",
    description="A web application to control B-Heaters using Flask and Paramiko.",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "Flask==2.3.2",
        "paramiko==3.2.0",
    ],
    python_requires=">=3.6",
)