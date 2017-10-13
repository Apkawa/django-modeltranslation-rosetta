# coding: utf-8
# !/usr/bin/env python
import os
from setuptools import setup, find_packages

__doc__ = """Utils for operating with django-modeltranslation, import and export translation in .po format"""

project_name = 'django-modeltranslation-rosetta'
app_name = 'modeltranslation_rosetta'

version = '0.0.2'

ROOT = os.path.dirname(__file__)

def get_absolute_path(path):
    return os.path.join(ROOT, path)

def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


def read(fname):
    return open(os.path.join(ROOT, fname)).read()


try:
    import pypandoc

    long_description = pypandoc.convert('README.md', 'rst')
except ImportError:
    long_description = read('README.md')

install_requires = [str(ir) for ir in parse_requirements(get_absolute_path('package_requirements.txt'))]

setup(
    name=project_name,
    version=version,
    description=__doc__,
    long_description=long_description,
    url="https://github.com/Apkawa/django-modeltranslation-rosetta",
    author="Apkawa",
    author_email='apkawa@gmail.com',
    packages=[package for package in find_packages() if package.startswith(app_name)],
    install_requires=install_requires,
    zip_safe=False,
    include_package_data=True,
    keywords=['django', 'admin', 'i18n', 'django-modeltranslation'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
