from setuptools import setup, find_packages

setup(
    name="persian-ocr",
    version="0.1.0",
    description="PDF/Img to text tool for PDF/Img files those contains Persian contents",
    author="Mostafa Motahari",
    author_email="mostafamotahari2004@gmail.com",
    license="Apache",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["seleniumbase>=4.38.0"],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache License",
        "Operating System :: OS Independent",
    ],
)

