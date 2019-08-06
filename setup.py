from setuptools import setup, find_packages

setup(
    name='digikalaCrawler',
    version='1.0',
    packages=find_packages(),
    package_data={
        'digikalaCrawler': ['proxy-list.txt']
    },
    entry_points={
        'scrapy': ['settings = digikalaCrawler.settings']
    },
    zip_safe=False,
)