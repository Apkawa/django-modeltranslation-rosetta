[![PyPi](https://img.shields.io/pypi/v/django-modeltranslation-rosetta.svg)](https://pypi.python.org/pypi/django-modeltranslation-rosetta)
[![Build Status](https://travis-ci.org/Apkawa/django-modeltranslation-rosetta.svg?branch=master)](https://travis-ci.org/Apkawa/django-modeltranslation-rosetta)
[![codecov](https://codecov.io/gh/Apkawa/django-modeltranslation-rosetta/branch/master/graph/badge.svg)](https://codecov.io/gh/Apkawa/django-modeltranslation-rosetta)
[![Requirements Status](https://requires.io/github/Apkawa/django-modeltranslation-rosetta/requirements.svg?branch=master)](https://requires.io/github/Apkawa/django-modeltranslation-rosetta/requirements/?branch=master)
[![PyUP](https://pyup.io/repos/github/Apkawa/django-modeltranslation-rosetta/shield.svg)](https://pyup.io/repos/github/Apkawa/django-modeltranslation-rosetta)
[![PyPI](https://img.shields.io/pypi/pyversions/django-modeltranslation-rosetta.svg)](https://pypi.python.org/pypi/django-modeltranslation-rosetta)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Project for interface translate fields like django-rosetta

# Installation

```bash
pip install django-modeltranslation-rosetta

```

or from git

```bash
pip install -e git+https://githib.com/Apkawa/django-modeltranslation-rosetta.git#egg=django-modeltranslation-rosetta
```

## Django and python version

| Python<br/>Django |        3.5         |      3.6           |      3.7           |       3.8          |
|:-----------------:|--------------------|--------------------|--------------------|--------------------|
| 1.8               |       :x:          |      :x:           |       :x:          |      :x:           |
| 1.11              | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |      :x:           |
| 2.2               | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| 3.0               |       :x:          | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |


# Usage
Add `modeltranslation_rosetta` into `INSTALLED_APPS` after `modeltranslation`
settings.py
```python
INSTALLED_APPS = [
    # ...
    'modeltranslation',
    'modeltranslation_rosetta',
    # ...
]
```
Open `/admin/modeltranslation_rosetta/trans/`

![](docs/source/images/import_export_all_models.png)

![](docs/source/images/import_export_model.png)

# Contributing

## run example app

```bash
pip install -r requirements-dev.txt
./test/manage.py migrate
./test/manage.py runserver
```

## run tests

```bash
pip install -r requirements-dev.txt
pytest
tox
```

## Update version

```bash
python setup.py bumpversion
```

## publish pypi

```bash
python setup.py publish
```






