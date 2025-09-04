# Intellireading CLI Library API Documentation

This document provides comprehensive documentation for the Intellireading CLI library's public API. The library can be used to metaguide EPUB, XHTML, and HTML files to improve reading focus and speed through visual anchoring techniques.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Functions](#core-functions)
  - [EPUB Functions](#epub-functions)
  - [XHTML Functions](#xhtml-functions)
  - [Directory Functions](#directory-functions)
  - [Utility Functions](#utility-functions)
- [Classes](#classes)
- [Examples](#examples)
- [Error Handling](#error-handling)

## Installation

```bash
pip install intellireading-cli
```

## Quick Start

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

## Core Functions

### EPUB Functions

#### `metaguide_epub_file(input_file: str, output_file: str, *, remove_metaguiding: bool = False)`

Metaguides an EPUB file by applying visual anchoring to text content within all XHTML files in the EPUB.

**Parameters:**
- `input_file` (str): Path to the input EPUB file
- `output_file` (str): Path to the output metaguided EPUB file
- `remove_metaguiding` (bool, optional): If True, removes metaguiding from the EPUB file. Defaults to False.

**Raises:**
- `ValueError`: If the input file doesn't exist or has an invalid extension
- `FileNotFoundError`: If the input file cannot be found

**Example:**
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

---

#### `metaguide_epub_stream(input_stream: BytesIO, *, remove_metaguiding: bool = False) -> BytesIO`

Metaguides an EPUB from a byte stream, useful for in-memory processing or web applications.

**Parameters:**
- `input_stream` (BytesIO): Input EPUB file as a byte stream
- `remove_metaguiding` (bool, optional): If True, removes metaguiding from the EPUB. Defaults to False.

**Returns:**
- `BytesIO`: The metaguided EPUB file as a byte stream

**Example:**
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

# Or use in a web application
def process_epub_upload(file_upload):
    input_stream = BytesIO(file_upload.read())
    return metaguide_epub_stream(input_stream)
```

### XHTML Functions

#### `metaguide_xhtml_file(input_file: str, output_file: str, *, remove_metaguiding: bool = False)`

Metaguides an XHTML/HTML file by applying visual anchoring to text content.

**Parameters:**
- `input_file` (str): Path to the input XHTML/HTML file
- `output_file` (str): Path to the output metaguided XHTML/HTML file
- `remove_metaguiding` (bool, optional): If True, removes metaguiding from the file. Defaults to False.

**Raises:**
- `ValueError`: If the input file doesn't exist or has an invalid extension
- `FileNotFoundError`: If the input file cannot be found

**Supported Extensions:**
- `.XHTML`
- `.HTML`
- `.HTM`

**Example:**
```python
from intellireading.client import metaguide_xhtml_file

# Metaguide an HTML file
metaguide_xhtml_file("article.html", "article_metaguided.html")

# Metaguide an XHTML file
metaguide_xhtml_file("document.xhtml", "document_metaguided.xhtml")

# Remove metaguiding
metaguide_xhtml_file(
    "article_metaguided.html", 
    "article_restored.html", 
    remove_metaguiding=True
)
```

---

#### `metaguide_xhtml_stream(input_file_stream: BytesIO, *, remove_metaguiding: bool = False) -> BytesIO`

Metaguides an XHTML/HTML file from a byte stream.

**Parameters:**
- `input_file_stream` (BytesIO): Input XHTML/HTML file as a byte stream
- `remove_metaguiding` (bool, optional): If True, removes metaguiding from the file. Defaults to False.

**Returns:**
- `BytesIO`: The metaguided XHTML/HTML file as a byte stream

**Example:**
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

# Get the metaguided content
metaguided_content = output_stream.read().decode('utf-8')
print(metaguided_content)
# Output will have bold tags: <p><b>Th</b>is <b>i</b>s <b>a</b> <b>sam</b>ple...</p>
```

### Directory Functions

#### `metaguide_dir(input_dir: str, output_dir: str, *, remove_metaguiding: bool = False)`

Metaguides all EPUB and XHTML/HTML files found in a directory recursively.

**Parameters:**
- `input_dir` (str): Path to the input directory
- `output_dir` (str): Path to the output directory (will be created if it doesn't exist)
- `remove_metaguiding` (bool, optional): If True, removes metaguiding from all files. Defaults to False.

**Behavior:**
- Processes files recursively through subdirectories
- Skips files that already exist in the output directory
- Creates the output directory if it doesn't exist
- Processes both EPUB (.epub, .kepub) and XHTML (.xhtml, .html, .htm) files

**Example:**
```python
from intellireading.client import metaguide_dir
import os

# Create directory structure
os.makedirs("books/fiction", exist_ok=True)
os.makedirs("books/non-fiction", exist_ok=True)

# Metaguide all books in the directory
metaguide_dir("books", "books_metaguided")

# This will process:
# books/book1.epub -> books_metaguided/book1.epub
# books/fiction/novel.epub -> books_metaguided/novel.epub
# books/article.html -> books_metaguided/article.html
# etc.

# Remove metaguiding from all files
metaguide_dir("books_metaguided", "books_restored", remove_metaguiding=True)
```

### Utility Functions

#### `is_file_metaguided(filepath: str) -> bool`

Checks if an EPUB file has already been metaguided by looking for the internal flag file.

**Parameters:**
- `filepath` (str): Path to the EPUB file to check

**Returns:**
- `bool`: True if the file has already been metaguided, False otherwise

**Raises:**
- `ValueError`: If the file doesn't exist or is not an EPUB file
- `FileNotFoundError`: If the input file cannot be found

**Example:**
```python
from intellireading.client import is_file_metaguided, metaguide_epub_file

# Check if file is already metaguided
if is_file_metaguided("mybook.epub"):
    print("File is already metaguided")
else:
    print("File needs metaguiding")
    metaguide_epub_file("mybook.epub", "mybook_metaguided.epub")

# Practical use in a batch processing script
import os

def process_epub_directory(input_dir, output_dir):
    for filename in os.listdir(input_dir):
        if filename.endswith('.epub'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            
            if not is_file_metaguided(input_path):
                metaguide_epub_file(input_path, output_path)
                print(f"Metaguided: {filename}")
            else:
                print(f"Skipped (already metaguided): {filename}")
```

## Classes

### `RegExBoldMetaguider`

The core class that handles the metaguiding algorithm. This class is typically not used directly but is available for advanced use cases.

**Constructor:**
```python
RegExBoldMetaguider(fallback_encoding: str = "utf-8")
```

**Key Methods:**
- `metaguide_xhtml_document(xhtml_document: bytes, *, remove_metaguiding: bool = False) -> bytes`

**Example (Advanced Usage):**
```python
from intellireading.client.metaguiding import RegExBoldMetaguider

# Create a custom metaguider
metaguider = RegExBoldMetaguider(fallback_encoding="iso-8859-1")

# Process raw XHTML bytes
html_bytes = b"<html><body><p>Hello world</p></body></html>"
metaguided_bytes = metaguider.metaguide_xhtml_document(html_bytes)
```

## Examples

### Web Application Integration

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

### Batch Processing Script

```python
import os
import logging
from intellireading.client import metaguide_dir, is_file_metaguided

# Set up logging
logging.basicConfig(level=logging.INFO)

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
                else:
                    print(f"✗ Failed to metaguide: {file}")

if __name__ == "__main__":
    batch_process_library("/path/to/my/books")
```

### Command Line Wrapper

```python
import argparse
from intellireading.client import metaguide_epub_file, metaguide_xhtml_file

def main():
    parser = argparse.ArgumentParser(description='Metaguide files')
    parser.add_argument('input', help='Input file')
    parser.add_argument('output', help='Output file')
    parser.add_argument('--remove', action='store_true', 
                       help='Remove metaguiding instead of adding it')
    
    args = parser.parse_args()
    
    if args.input.endswith('.epub'):
        metaguide_epub_file(args.input, args.output, 
                           remove_metaguiding=args.remove)
    else:
        metaguide_xhtml_file(args.input, args.output, 
                            remove_metaguiding=args.remove)

if __name__ == "__main__":
    main()
```

## Error Handling

The library raises standard Python exceptions:

```python
from intellireading.client import metaguide_epub_file

try:
    metaguide_epub_file("nonexistent.epub", "output.epub")
except ValueError as e:
    print(f"Invalid file: {e}")
except FileNotFoundError as e:
    print(f"File not found: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Common Error Scenarios

1. **File doesn't exist**: `ValueError` or `FileNotFoundError`
2. **Invalid file extension**: `ValueError`
3. **Corrupted EPUB/XHTML**: Various exceptions during processing
4. **Permission issues**: `PermissionError`
5. **Disk space issues**: `OSError`

### Best Practices

1. **Always validate input files** before processing:
   ```python
   import os
   
   def safe_metaguide(input_file, output_file):
       if not os.path.exists(input_file):
           raise FileNotFoundError(f"Input file not found: {input_file}")
       
       if not input_file.lower().endswith(('.epub', '.html', '.xhtml', '.htm')):
           raise ValueError(f"Unsupported file type: {input_file}")
       
       metaguide_epub_file(input_file, output_file)
   ```

2. **Use streams for large files** or web applications to avoid memory issues

3. **Check if files are already metaguided** to avoid unnecessary processing

4. **Handle encoding issues** by specifying appropriate fallback encodings

## Technical Notes

### Metaguiding Algorithm

The library uses a regex-based approach to identify and bold the first part of words:
- Words with 1-3 characters: Bold the first character
- Words with 4+ characters: Bold the first half (rounded up)
- Preserves HTML entities and existing formatting
- Skips navigation and table of contents files in EPUBs

### Performance Considerations

- Stream-based processing for memory efficiency
- ZIP compression maintained for EPUB files
- Recursive directory processing with skip logic for existing files
- Encoding detection with multiple fallback methods

### Encoding Support

- Automatic encoding detection using XML headers, BOM, and lxml
- UTF-8 fallback for unknown encodings
- Support for various character encodings in XHTML documents
