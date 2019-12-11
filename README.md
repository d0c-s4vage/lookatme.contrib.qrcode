[![Master Build Status](https://travis-ci.org/d0c-s4vage/lookatme.contrib.qrcode.svg?branch=master)](https://travis-ci.org/d0c-s4vage/lookatme.contrib.qrcode)
[![Coverage Status](https://coveralls.io/repos/github/d0c-s4vage/lookatme.contrib.qrcode/badge.svg?branch=master)](https://coveralls.io/github/d0c-s4vage/lookatme.contrib.qrcode?branch=master)
[![PyPI Statistics](https://img.shields.io/pypi/dm/lookatme.contrib.qrcode)](https://pypistats.org/packages/lookatme.contrib.qrcode)
[![Latest Release](https://img.shields.io/pypi/v/lookatme.contrib.qrcode)](https://pypi.python.org/pypi/lookatme.contrib.qrcode/)
[![Documentation Status](https://readthedocs.org/projects/lookatmecontribqrcode/badge/?version=latest)](https://lookatmecontribqrcode.readthedocs.io/en/latest/?badge=latest)

[![Twitter Follow](https://img.shields.io/twitter/follow/d0c_s4vage?style=plastic)](https://twitter.com/d0c_s4vage)

# lookatme.contrib.qrcode

This [lookatme](https://github.com/d0c-s4vage/lookatme) extension adds
QR code rendering capabilities to the code blocks.

## Installation

If this project has been pushed up to pypi:

```bash
pip install lookatme.contrib.qrcode
```

otherwise:

```bash
pip install ./path/to/lookatme.contrib.qrcode
```

## Usage

Add the qrcode into the extensions array in the
slide YAML header:

```markdown
---
title: A title
author: Me
date: 2019-12-04
extensions:
  - qrcode
---
```

### Basic Usage

With the extension installed and declared in the YAML header, use it in your
markdown like so:

~~~md
# A Slide

```qrcode
https://github.com/d0c-s4vage/lookatme.contrib.qrcode
```
~~~

![QR code single rendering](docs/source/_static/qrcode_single.png)

### Extended Usage

An [extended mode](https://lookatmecontribqrcode.readthedocs.io/en/latest/#qrcode-ex-codeblocks)
is also available that lets multiple columns of QR codes be rendered side-by-side:

~~~md
# A Slide

```qrcode-ex
columns:
  - data: https://github.com/d0c-s4vage/lookatme
    caption: "**lookatme** project"
  - data: https://github.com/d0c-s4vage/lookatme.contrib.qrcode
    caption: Text `lookatme.contrib.qrcode`
```
~~~

![QR code single rendering](docs/source/_static/qrcode_double.png)

### Details

[Read the documentation](https://lookatmecontribqrcode.readthedocs.io/en/latest/)
