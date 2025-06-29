from setuptools import setup, find_packages

setup(
    name="telegram-qr-bot",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pyTelegramBotAPI==4.14.0",
        "pyzbar==0.1.9",
        "opencv-python-headless==4.8.0.74",
        "Pillow==9.5.0",
        "numpy==1.24.3",
        "requests==2.31.0",
        "python-dotenv==1.0.0",
        "google-generativeai==0.3.2",
    ],
    python_requires=">=3.8,<3.12",
) 