#!/usr/bin/env python3
"""
Synthetic Log Generator
Generates distinct types of synthetic log data in 10 different formats:
1. Apache HTTP access logs
2. JSON formatted log data  
3. CSV formatted log data
4. Pipe delimited log data
5. KV delimited log data
6. Hadoop system logs
7. Logstash structured logs
8. NGINX access logs
9. Apache Tomcat logs
10. MySQL slow query logs
11. Redis logs
"""

import json
import random
import time
import threading
import argparse
import sys
import os
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import logging
from dotenv import load_dotenv
from log_generators import LOG_GENERATORS


def choose_output_file() -> str:
    """Choose output file location, trying /var/log first, falling back to home directory"""
    default_path = "/var/log/loadgen/loadgen.log"
    fallback_path = os.path.expanduser("~/loadgen.log")
    
    try:
        os.makedirs(os.path.dirname(default_path), exist_ok=True)
        with open(default_path, 'a') as f:
            f.write("probe\n")
        return default_path
    except (PermissionError, OSError):
        with open(fallback_path, 'a') as f:
            f.write("probe\n")
        return fallback_path


def ensure_output_directory(output_file: str):
    """Ensure the output directory exists for the output file and status file"""
    # Ensure directory for main output file (and all individual format files)
    output_dir = os.path.dirname(output_file)
    if output_dir:  # Only create directory if there's a directory path
        try:
            os.makedirs(output_dir, exist_ok=True)
            print(f"[*] Ensured output directory exists: {output_dir}")
            print(f"[*] Individual format files will be created in this directory")
        except (PermissionError, OSError) as e:
            print(f"[!] Could not create output directory {output_dir}: {e}")
            # Try to use a fallback location
            fallback_path = os.path.expanduser("~/loadgen.log")
            print(f"[*] Using fallback output file: {fallback_path}")
            return fallback_path
    
    # Ensure directory for status file
    status_file = f"{output_file}.status"
    status_dir = os.path.dirname(status_file)
    if status_dir and status_dir != output_dir:  # Only if different from main output dir
        try:
            os.makedirs(status_dir, exist_ok=True)
            print(f"[*] Ensured status file directory exists: {status_dir}")
        except (PermissionError, OSError) as e:
            print(f"[!] Could not create status file directory {status_dir}: {e}")
    
    return output_file


def setup_logging(output_file: str) -> logging.Logger:
    """Setup logging configuration"""
    logger = logging.getLogger('log_generator')
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler for status file
    status_file = f"{output_file}.status"
    file_handler = logging.FileHandler(status_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


def get_random_lines(lines_per_format: int) -> int:
    """Generate a random number of lines up to the specified maximum"""
    return random.randint(1, lines_per_format)


def run_concurrent(output_file: str, lines_per_format: int, logger: logging.Logger) -> None:
    """Run all log generators concurrently"""
    # Generate individual file paths for each format
    base_dir = os.path.dirname(output_file)
    base_name = os.path.basename(output_file).replace('.log', '')
    
    logger.info(f"[*] Writing logs to individual files in: {base_dir}")
    logger.info(f"[*] Concurrent generation: up to {lines_per_format} lines per format across {len(LOG_GENERATORS)} formats")
    
    lock = threading.Lock()
    output_files = []
    
    with ThreadPoolExecutor(max_workers=len(LOG_GENERATORS)) as executor:
        futures = {}
        
        for format_name, generator_class in LOG_GENERATORS.items():
            lines_to_generate = get_random_lines(lines_per_format)
            format_file = os.path.join(base_dir, f"{base_name}_{format_name}.log")
            output_files.append(format_file)
            
            generator = generator_class(lines_to_generate, format_file, lock, logger)
            future = executor.submit(generator.generate)
            futures[future] = format_name.upper()
        
        for future in as_completed(futures):
            name = futures[future]
            try:
                future.result()
            except Exception as e:
                logger.error(f"[!] {name} generator failed: {e}")
    
    logger.info(f"[OK] All formats finished. Output files:")
    for output_file in output_files:
        logger.info(f"    - {output_file}")


def run_single_format(format_name: str, output_file: str, lines_per_format: int, logger: logging.Logger) -> None:
    """Run a single log format generator"""
    if format_name not in LOG_GENERATORS:
        logger.error(f"Unknown format: {format_name}")
        return
    
    lines_to_generate = get_random_lines(lines_per_format)
    
    # Generate format-specific file path
    base_dir = os.path.dirname(output_file)
    base_name = os.path.basename(output_file).replace('.log', '')
    format_file = os.path.join(base_dir, f"{base_name}_{format_name}.log")
    
    logger.info(f"[*] Starting {format_name.upper()} generation of up to {lines_per_format} lines")
    logger.info(f"[*] Writing to: {format_file}")
    
    lock = threading.Lock()
    generator_class = LOG_GENERATORS[format_name]
    format_generator = generator_class(lines_to_generate, format_file, lock, logger)
    format_generator.generate()


def run_with_duration(duration_seconds: int, output_file: str, lines_per_format: int, pause_seconds: float, logger: logging.Logger) -> None:
    """Run log generation for a specified duration, restarting if it finishes early"""
    start_time = time.time()
    end_time = start_time + duration_seconds
    
    logger.info(f"[*] Starting time-based execution for {duration_seconds} seconds")
    logger.info(f"[*] Will run until: {datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"[*] Each iteration will create individual files per format")
    
    iteration = 1
    
    while time.time() < end_time:
        remaining_time = end_time - time.time()
        logger.info(f"[*] Starting iteration {iteration} (remaining: {remaining_time:.1f}s)")
        
        # Run the concurrent generation (now creates individual files)
        run_concurrent(output_file, lines_per_format, logger)
        
        # Check if we still have time left
        if time.time() < end_time:
            logger.info(f"[*] Iteration {iteration} completed, restarting for remaining time...")
            iteration += 1
            
            # Add pause between iterations if specified
            if pause_seconds > 0:
                logger.info(f"[*] Pausing for {pause_seconds} seconds...")
                time.sleep(pause_seconds)
        else:
            logger.info(f"[*] Time limit reached after {iteration} iteration(s)")
            break
    
    total_runtime = time.time() - start_time
    logger.info(f"[OK] Time-based execution completed. Total runtime: {total_runtime:.1f}s, Iterations: {iteration}")


def load_env_config():
    """Load configuration from .env file if it exists"""
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        load_dotenv(env_file)
        return {
            'lines': os.getenv('LOG_LINES'),
            'output': os.getenv('LOG_OUTPUT'),
            'format': os.getenv('LOG_FORMAT'),
            'duration': os.getenv('LOG_DURATION'),
            'pause': os.getenv('LOG_PAUSE')
        }
    return {}


def main():
    # Load environment configuration first
    env_config = load_env_config()
    
    parser = argparse.ArgumentParser(description="Generate synthetic log data in multiple formats")
    parser.add_argument("--lines", "-l", type=int, 
                       default=int(env_config.get('lines', 5000)),
                       help="Number of lines to generate per format (default: 5000)")
    parser.add_argument("--output", "-o", type=str, 
                       default=env_config.get('output'),
                       help="Output file path (default: auto-detect)")
    parser.add_argument("--format", "-f", choices=[
        "apache", "csv", "pipe", "kv", "hadoop", "logstash", "nginx", "tomcat", "mysql", "redis", "syslog", "all"
    ], default=env_config.get('format', 'all'), 
                       help="Log format to generate (default: all)")
    parser.add_argument("--duration", "-d", type=int, 
                       default=int(env_config.get('duration')) if env_config.get('duration') else None,
                       help="Run for specified duration in seconds (restarts if finishes early)")
    parser.add_argument("--pause", "-p", type=float, 
                       default=float(env_config.get('pause')) if env_config.get('pause') else 0.0,
                       help="Pause duration in seconds between iterations (default: 0.0)")
    
    args = parser.parse_args()
    
    # Setup output file and logging
    output_file = args.output or choose_output_file()
    output_file = ensure_output_directory(output_file)
    logger = setup_logging(output_file)
    
    # If duration is specified, use time-based execution
    if args.duration:
        if args.format != "all":
            logger.warning("[!] Duration mode only supports 'all' format. Using all formats.")
        run_with_duration(args.duration, output_file, args.lines, args.pause, logger)
    else:
        # Original execution logic
        if args.format == "all":
            run_concurrent(output_file, args.lines, logger)
        else:
            run_single_format(args.format, output_file, args.lines, logger)


if __name__ == "__main__":
    main()