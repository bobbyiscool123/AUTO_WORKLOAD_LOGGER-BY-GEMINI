from setuptools import setup, find_packages

setup(
    name="gemini-workload-logger",
    version="0.1.0",
    description="A professional GUI application for logging project workloads with AI-enhanced formatting",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/gemini-workload-logger",
    packages=find_packages(),
    install_requires=[
        "google-generativeai>=0.3.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="gemini, logger, tkinter, gui, ai",
    entry_points={
        "console_scripts": [
            "gemini-logger=gemini-logger:main",
        ],
    },
) 