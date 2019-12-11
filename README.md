# lookatme.contrib.qrcode

Adds qrcode rendering

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

With the extension installed and declared in the YAML header, use it in your
markdown like so:

~~~markdown
```qrcode

```
~~~
