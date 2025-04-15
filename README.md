# Domain Availability Checker

A multi-threaded tool that checks the availability of domains from a text file and outputs available domains to a timestamped file.

## Features

- Processes a list of domains from a file (default: `domains.txt`)
- Uses 8 worker threads by default (configurable)
- Configurable timeout up to 25 seconds (default: 5 seconds)
- Outputs available domains to a timestamped file (format: `available_YYYYMMDD_HHMMSS.txt`)
- Skips invalid domains and empty lines
- Shows progress information during execution
- Validates domains with a regular expression before checking

## Installation

This tool requires Python 3.6 or higher and has no external dependencies.

### Quick Setup

1. Clone this repository:
```bash
git clone https://github.com/jaeinseo/domain-checker.git
cd domain-checker
```

2. Make the script executable (Linux/Mac):
```bash
chmod +x domain_checker.py
```

### Usage

Run the domain checker with default settings:
```bash
python domain_checker.py
```

Alternatively, use command-line options to customize behavior:
```bash
python domain_checker.py -f your_domains.txt -t 12 -o 10
```

### Command-line Options

- `-f, --file TEXT` - Input file containing domains (default: `domains.txt`)
- `-t, --threads INTEGER` - Number of worker threads (default: 8)
- `-o, --timeout INTEGER` - Timeout in seconds for each request (default: 5, max: 25)
- `-h, --help` - Show help message and exit

## Input File Format

The input file should contain one domain name per line. 
Lines that do not contain valid domain names will be skipped.

Example `domains.txt`:
```
example.com
test.org
mydomain.net
invalid..domain
another-domain.com
```

## Output

The tool generates a timestamped output file with available domains:
```
available_20250414_123045.txt
```

The output file contains header information and one available domain per line.

## How It Works

This tool checks domain availability by attempting to resolve domain names. If a domain doesn't resolve (socket.gaierror), it's considered potentially available. This is a simple heuristic and not a definitive check of domain registration status.

## Example

1. Create a file named `domains.txt` with domains to check:
```
example.com
potential-domain.com
my-new-site.org
```

2. Run the domain checker:
```bash
python domain_checker.py
```

3. Check the results in the generated output file.

## License

MIT License

Copyright (c) 2025 Jaein Seo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
