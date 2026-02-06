# Synthetic Log Generator

A Python application that generates synthetic log data in multiple formats for testing and development purposes.

## Features

- **12 Log Formats**: Apache, CSV, NVIDIA nvidia-smi, Pipe-delimited, Key-Value, Hadoop, Logstash, NGINX, Tomcat, MySQL, Redis, Syslog
- **Concurrent Generation**: All formats generated simultaneously for efficiency
- **Time-Based Execution**: Run for specified duration with automatic restart
- **Environment Configuration**: Load settings from `.env` file
- **Pause Control**: Configurable pause between iterations
- **Single Format Support**: Generate specific formats only
- **Configurable Output**: Automatic output file selection with fallback
- **Progress Tracking**: Real-time progress updates every 1000 lines
- **Thread-Safe**: Safe concurrent writing to output files

## Usage

### Basic Usage
```bash
# Generate all formats (5000 lines each by default)
python3 generate_logs.py

# Generate specific number of lines per format
python3 generate_logs.py --lines 10000

# Generate specific format only
python3 generate_logs.py --format apache --lines 1000

# Specify output file
python3 generate_logs.py --output /path/to/output.log
```

### Command Line Options

- `--lines, -l`: Maximum number of lines to generate per format (default: 5000, generates 1 to this number randomly)
- `--output, -o`: Output file path (default: auto-detect)
- `--format, -f`: Log format to generate (apache, csv, nvidia, pipe, kv, hadoop, logstash, nginx, tomcat, mysql, redis, syslog, all)
- `--duration, -d`: Run for specified duration in seconds (restarts if finishes early)
- `--pause, -p`: Pause duration in seconds between iterations (default: 0.0)

### Available Formats

1. **Apache Logs**: Standard Apache access log format with IP, timestamp, method, path, status codes, etc.
2. **CSV Logs**: Comma-separated values with timestamp, level, service, user, latency, status
3. **NVIDIA nvidia-smi Logs**: CSV output with common GPU telemetry fields
4. **Pipe Logs**: Pipe-delimited format with transaction data, amounts, countries, sessions
5. **KV Logs**: Key-value format with timestamp, level, service, request ID, duration
6. **Hadoop Logs**: Hadoop-style logs with job/task IDs, memory usage, CPU metrics
7. **Logstash Logs**: Structured logs with key/value pairs
8. **NGINX Logs**: Standard NGINX access log format
9. **Tomcat Logs**: Apache Tomcat log format with component and thread info
10. **MySQL Logs**: Slow query style entries with query metrics
11. **Redis Logs**: Redis server-style log lines
12. **Syslog Logs**: RFC 5424 style logs with structured data

## Output

The application will:
- Try to write to `/var/log/loadgen/loadgen.log` (requires appropriate permissions)
- Fall back to `~/loadgen.log` if system directory is not accessible
- Generate a status log file (`{output_file}.status`) with progress information
- Display real-time progress to console

## Examples

```bash
# Generate up to 1000 lines of each format (random amount per format)
python3 generate_logs.py --lines 1000

# Generate only NVIDIA nvidia-smi logs
python3 generate_logs.py --format nvidia --lines 5000

# Generate to specific file
python3 generate_logs.py --output /tmp/test_logs.log --lines 2000

# Run for 60 seconds with pause between iterations
python3 generate_logs.py --duration 60 --pause 0.5

# Generate only Apache logs for 30 seconds
python3 generate_logs.py --format apache --duration 30 --lines 1000
```

## Environment Configuration

Create a `.env` file to set default values:

```bash
# .env file example
LOG_LINES=1000
LOG_OUTPUT=/var/log/loadgen/loadgen.log
LOG_FORMAT=all
LOG_DURATION=60
LOG_PAUSE=0.3
```

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd generate_logs

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the script
python3 generate_logs.py --help
```

## Requirements

- Python 3.6+
- python-dotenv (for .env file support)

## Dependencies

```bash
pip install python-dotenv
```

Or install from requirements.txt:

```bash
pip install -r requirements.txt
```

