[![Build Status](https://travis-ci.org/Apkawa/django-modeltranslation-rosetta.svg?branch=master)](https://travis-ci.org/Apkawa/django-modeltranslation-rosetta)
[![codecov](https://codecov.io/gh/Apkawa/django-modeltranslation-rosetta/branch/master/graph/badge.svg)](https://codecov.io/gh/Apkawa/django-modeltranslation-rosetta)

[![PyPi](https://img.shields.io/pypi/v/django-modeltranslation-rosetta.svg)](https://pypi.python.org/pypi/django-modeltranslation-rosetta)
[![PyPI Python versions](https://img.shields.io/pypi/pyversions/django-modeltranslation-rosetta.svg)](https://pypi.python.org/pypi/django-modeltranslation-rosetta)
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

| Python<br/>Django | 3.8 | 3.9 | 3.10 | 3.11 | 3.12 | 3.13 |
|:-----------------:|-----|----|------|------|------|------|
|        4.2        | ✅   | ✅  | ✅    | ✅    | ✅    | ✅    |
|        5.0        | ❌   | ❌   | ✅    | ✅    | ✅    | ✅    |
|        5.1        | ❌   | ❌   | ✅    | ✅    | ✅    | ✅    |
|        5.2        | ❌   | ❌   | ✅    | ✅    | ✅    | ✅    |


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
