![Intellireading.com](https://go.hugobatista.com/ghraw/intellireading-www/main/src/img/intellireading.png)
# Standalone tool and library

[![PyPI - Version](https://img.shields.io/pypi/v/intellireading-cli.svg)](https://pypi.org/project/intellireading-cli)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/intellireading-cli.svg)](https://pypi.org/project/intellireading-cli)
[![Deploy to ghcr.io](https://go.hugobatista.com/gh/intellireading-cli/actions/workflows/build-and-publish-to-ghcr.yml/badge.svg)](https://go.hugobatista.com/gh/intellireading-cli/actions/workflows/build-and-publish-to-ghcr.yml)
[![Lint](https://go.hugobatista.com/gh/intellireading-cli/actions/workflows/lint.yml/badge.svg)](https://go.hugobatista.com/gh/intellireading-cli/actions/workflows/lint.yml)
[![Test](https://go.hugobatista.com/gh/intellireading-cli/actions/workflows/test.yml/badge.svg)](https://go.hugobatista.com/gh/intellireading-cli/actions/workflows/test.yml)
[![GitMCP](https://img.shields.io/endpoint?url=https://gitmcp.io/badge/0x6f677548/intellireading-cli)](https://gitmcp.io/0x6f677548/intellireading-cli)

Intellireading is a CLI tool with commands to accelerate your reading experience. It can also be used as a Python library.
Currently, it supports metaguiding an EPUB, KEPUB, XHTML, or HTML file (more features coming):
```console
> intellireading metaguide-epub --input_file mybook.epub --output_file mybook_metaguided.epub
```
Example of a text converted to a metaguided text:
![Intellireading.com](https://go.hugobatista.com/ghraw/intellireading-www/main/src/img/sample.png) 


This repo is part of the [Intellireading](https://intellireading.com/) project, which aims to help people with dyslexia, ADHD, or anyone who wants to improve their reading focus and speed. 

## [Other Intellireading Code Repositories](https://go.hugobatista.com/ghstars/lists/intellireading)
- [Intellireading website](https://go.hugobatista.com/gh/intellireading-www), which allows anyone to convert an Epub to the metaguided version.
- [API Server](https://go.hugobatista.com/gh/intellireading-api_server), that support the Intellireading website.
- [CLI Tool](https://go.hugobatista.com/gh/intellireading-cli). A standalone tool and library that can be used to metaguide epub files.
- [Calibre Plugins](https://go.hugobatista.com/gh/intellireading-calibre-plugins). A set of plugins that can be used to metaguide epub files using Calibre.


## What is EPUB Metaguiding?
**Metagu**iding **i**s **a** **techn**ique **th**at **ca**n **b**e **us**ed **t**o **impr**ove **yo**ur **read**ing **foc**us **an**d **spe**ed **(some**times **cal**led **Bio**nic **Readi**ng). **I**t **i**s **bas**ed **o**n **th**e **id**ea **th**at **yo**u **ca**n **us**e **a** **vis**ual **gui**de **t**o **he**lp **yo**ur **ey**es **foc**us **o**n **th**e **te**xt **yo**u **ar**e **read**ing. **I**n **th**is **cas**e, **th**e **vis**ual **gui**de **i**s **do**ne **b**y **bold**ing **a** **pa**rt **o**f **th**e **tex**t, **crea**ting **vis**ual **anch**ors **th**at **yo**ur **ey**es **ca**n **us**e **t**o **foc**us **o**n **th**e **tex**t. **Th**is **i**s **simi**lar **t**o **th**e **wa**y **a** **fin**ger **ca**n **b**e **us**ed **t**o **gui**de **yo**ur **ey**es **alo**ng **a** **li**ne **o**f **tex**t, **whi**ch **ha**s **be**en **sho**wn **t**o **impr**ove **read**ing **spe**ed **an**d **foc**us. ([**stu**dy: **"Do**es **finger-t**racking **poi**nt **t**o **chi**ld **read**ing **strate**gies"](https://ceur-ws.org/Vol-2769/paper_60.pdf))

**Howe**ver, **unl**ike **a** **fing**er, **th**e **vis**ual **gui**de **i**s **no**t **distra**cting, **an**d **i**t **ca**n **b**e **us**ed **t**o **gui**de **yo**ur **ey**es **alo**ng **mult**iple **lin**es **o**f **te**xt **a**t **onc**e. **Th**is **all**ows **yo**u **t**o **re**ad **fast**er, **an**d **wi**th **le**ss **effo**rt.

**Metagu**iding **i**s **partic**ulary **use**ful **fo**r **peo**ple **wi**th **dysl**exia **o**r **ADH**D, **bu**t **i**t **ca**n **b**e **us**ed **b**y **any**one **wh**o **wan**ts **t**o **impr**ove **the**ir **read**ing **foc**us **an**d **spe**ed. **Fo**r **mo**re **inform**ation, **vis**it **th**e [**Intelli**reading **webs**ite.](https://intellireading.com/)

## Features

Intellireading commands can be used to:
- **Metaguide an EPUB file**: Metaguide an EPUB file, transforming it into a metaguided EPUB file, by transforming all XHTML files in the EPUB file into metaguided XHTML files.
- **Metaguide an XHTML file**: Metaguide an XHTML file, transforming it into a metaguided XHTML file.
- **Metaguide a directory**: Metaguide all files in a directory, transforming all EPUB, XHTML, and HTML files into metaguided files.

## Installation

Intellireading is a command line tool that can be used in Windows, Linux, and MacOS. It is written in Python and can be used as a module or as a standalone tool, as long as you have Python >3.7 installed (or Docker).

### pip
To install it, you can use pip:
```console
> pip install intellireading-cli
> intellireading --help
```

### From source code
You can also install it from the source code:
```console
> git clone https://go.hugobatista.com/gh/intellireading-cli.git
> cd intellireading-cli
> pip install .
> intellireading --help
```

### Docker
Alternatively, you can use the Docker image:

#### Help command
```console
> docker pull ghcr.io/0x6f677548/intellireading-cli:latest
> docker run -it --rm ghcr.io/0x6f677548/intellireading-cli --help
```

#### Metaguide an EPUB file
##### Linux/MacOS
```console
> docker run -it --rm -v $(pwd)/tests:/tests ghcr.io/0x6f677548/intellireading-cli metaguide-epub --input_file '/tests/test_files/input.epub' --output_file '/tests/test_files/output.epub'
```
##### Windows
```powershell
> docker run -it --rm -v ${pwd}/tests:/tests ghcr.io/0x6f677548/intellireading-cli metaguide-epub --input_file '/tests/test_files/input.epub' --output_file '/tests/test_files/output.epub'
```

## CLI Usage

All available commands and options can be seen by using the `--help` option.
```console
> intellireading --help
```

To get help on a specific command, use the `--help` option with the command name. For example, to get help on the `metaguide-epub` command, use the following command:
```console
> intellireading metaguide-epub --help
```

Intellireading is based on [Click](https://github.com/pallets/click/), taking advantage of its features, such as chaining commands and options. 

### CLI Examples

#### Metaguide an EPUB file
To metaguide an EPUB file, use the `metaguide-epub` command. The command requires the path to the EPUB file and the output file. The output file will be a metaguided epub file. 

```console
> intellireading metaguide-epub --input_file mybook.epub --output_file mybook_metaguided.epub
```

#### Metaguide a XHTML file
To metaguide an XHTML file, use the `metaguide-xhtml` command. The command requires the path to the XHTML file and the output file. The output file will be a metaguided xhtml file. 

```console
> intellireading metaguide-xhtml --input_file mybook.xhtml --output_file mybook_metaguided.xhtml
```

#### Metaguide all files in a directory
To metaguide all files in a directory, use the `metaguide-dir` command. The command requires the path to the directory and the output directory. The output directory will contain all metaguided files, including epub, xhtml and html files. 

```console
> intellireading metaguide-dir --input_dir mydir --output_dir mydir_metaguided
```

## Experimental Features
Some features are still experimental and may not work as expected. Use them with caution.

### Remove metaguiding
The remove metaguiding feature allows you to remove metaguiding from previous metaguided files. This implementation is still experimental and may not work as expected, since it is not possible to recover the original text. The current implementation tries to remove the metaguiding by removing the bold tags from the text, but that may imply in some original text format loss.

#### Remove metaguiding from an EPUB file
To remove metaguiding from an EPUB file, use the --remove_metaguiding flag. The command requires the path to the EPUB file and the output file. The output file will be an epub file without metaguiding. 

```console
> intellireading metaguide-epub --remove_metaguiding --input_file mybook_metaguided.epub --output_file mybook.epub
```

#### Remove metaguiding from a XHTML file
To remove metaguiding from a XHTML file, use the --remove_metaguiding flag. The command requires the path to the XHTML file and the output file. The output file will be an xhtml file without metaguiding. 

```console
> intellireading metaguide-xhtml --remove_metaguiding --input_file mybook_metaguided.xhtml --output_file mybook.xhtml
```

#### Remove metaguiding from all files in a directory
To remove metaguiding from all files in a directory, use the --remove_metaguiding flag. The command requires the path to the directory and the output directory. The output directory will contain all files without metaguiding, including epub, xhtml and html files. 

```console
> intellireading metaguide-dir --remove_metaguiding --input_dir mydir_metaguided --output_dir mydir
```

## Python Library API

The intellireading-cli package can be used as a Python library for programmatic access to metaguiding functionality. This is useful for integrating metaguiding into web applications, batch processing scripts, or other Python projects.

### Quick Start

```python
from intellireading.client import (
    metaguide_epub_file,
    metaguide_xhtml_file,
    metaguide_epub_stream,
    metaguide_xhtml_stream,
    metaguide_dir,
    is_file_metaguided
)

# Metaguide an EPUB file
metaguide_epub_file("input.epub", "output.epub")

# Metaguide an XHTML file
metaguide_xhtml_file("input.html", "output.html")
```

### Core Functions

#### EPUB Functions

**`metaguide_epub_file(input_file: str, output_file: str, *, remove_metaguiding: bool = False)`**

Metaguides an EPUB file by applying visual anchoring to text content within all XHTML files in the EPUB.

```python
from intellireading.client import metaguide_epub_file

# Basic metaguiding
metaguide_epub_file("mybook.epub", "mybook_metaguided.epub")

# Remove metaguiding (experimental)
metaguide_epub_file(
    "mybook_metaguided.epub", 
    "mybook_original.epub", 
    remove_metaguiding=True
)
```

**`metaguide_epub_stream(input_stream: BytesIO, *, remove_metaguiding: bool = False) -> BytesIO`**

Metaguides an EPUB from a byte stream, useful for in-memory processing or web applications.

```python
from io import BytesIO
from intellireading.client import metaguide_epub_stream

# Read EPUB into memory
with open("input.epub", "rb") as f:
    input_stream = BytesIO(f.read())

# Metaguide the stream
output_stream = metaguide_epub_stream(input_stream)

# Write to file
with open("output.epub", "wb") as f:
    f.write(output_stream.read())
```

#### XHTML Functions

**`metaguide_xhtml_file(input_file: str, output_file: str, *, remove_metaguiding: bool = False)`**

Metaguides an XHTML/HTML file by applying visual anchoring to text content. Supports `.xhtml`, `.html`, and `.htm` files.

```python
from intellireading.client import metaguide_xhtml_file

# Metaguide an HTML file
metaguide_xhtml_file("article.html", "article_metaguided.html")

# Remove metaguiding
metaguide_xhtml_file(
    "article_metaguided.html", 
    "article_restored.html", 
    remove_metaguiding=True
)
```

**`metaguide_xhtml_stream(input_file_stream: BytesIO, *, remove_metaguiding: bool = False) -> BytesIO`**

Metaguides an XHTML/HTML file from a byte stream.

```python
from io import BytesIO
from intellireading.client import metaguide_xhtml_stream

# Process HTML content from string
html_content = """
<!DOCTYPE html>
<html>
<body>
    <p>This is a sample paragraph that will be metaguided.</p>
</body>
</html>
"""

input_stream = BytesIO(html_content.encode('utf-8'))
output_stream = metaguide_xhtml_stream(input_stream)
metaguided_content = output_stream.read().decode('utf-8')
```

#### Directory Functions

**`metaguide_dir(input_dir: str, output_dir: str, *, remove_metaguiding: bool = False)`**

Metaguides all EPUB and XHTML/HTML files found in a directory recursively.

```python
from intellireading.client import metaguide_dir

# Metaguide all books in the directory
metaguide_dir("books", "books_metaguided")

# Remove metaguiding from all files
metaguide_dir("books_metaguided", "books_restored", remove_metaguiding=True)
```

#### Utility Functions

**`is_file_metaguided(filepath: str) -> bool`**

Checks if an EPUB file has already been metaguided.

```python
from intellireading.client import is_file_metaguided, metaguide_epub_file

# Check if file is already metaguided
if not is_file_metaguided("mybook.epub"):
    metaguide_epub_file("mybook.epub", "mybook_metaguided.epub")
    print("File metaguided successfully")
else:
    print("File is already metaguided")
```

### Integration Examples

#### Web Application (Flask)

```python
from flask import Flask, request, send_file
from io import BytesIO
from intellireading.client import metaguide_epub_stream

app = Flask(__name__)

@app.route('/metaguide', methods=['POST'])
def metaguide_upload():
    file = request.files['epub']
    if file and file.filename.endswith('.epub'):
        input_stream = BytesIO(file.read())
        output_stream = metaguide_epub_stream(input_stream)
        
        return send_file(
            output_stream,
            as_attachment=True,
            download_name=f"metaguided_{file.filename}",
            mimetype='application/epub+zip'
        )
    return "Invalid file", 400
```

#### Batch Processing

```python
import os
from intellireading.client import metaguide_dir, is_file_metaguided

def batch_process_library(library_path):
    """Process an entire library of EPUB files"""
    processed_path = os.path.join(library_path, "metaguided")
    
    # Process all files
    metaguide_dir(library_path, processed_path)
    
    # Verify results
    for root, dirs, files in os.walk(processed_path):
        for file in files:
            if file.endswith('.epub'):
                filepath = os.path.join(root, file)
                if is_file_metaguided(filepath):
                    print(f"✓ Successfully metaguided: {file}")

batch_process_library("/path/to/my/books")
```

### Error Handling

```python
from intellireading.client import metaguide_epub_file

try:
    metaguide_epub_file("mybook.epub", "output.epub")
except ValueError as e:
    print(f"Invalid file: {e}")
except FileNotFoundError as e:
    print(f"File not found: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```
