#!/usr/bin/env python3
"""
Synthetic Log Generator
Generates distinct types of synthetic log data in 6 different formats:
1. Apache Log data
2. JSON formatted log data  
3. CSV formatted log data
4. Pipe delimited log data
5. KV delimited log data
6. Hadoop log data
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

class LogGenerator:
    def __init__(self, output_file: str = None, lines_per_format: int = 5000, pause_seconds: float = 0.0):
        self.lines_per_format = lines_per_format
        self.output_file = output_file or self._choose_output_file()
        self.pause_seconds = pause_seconds
        self.lock = threading.Lock()
        self._ensure_output_directory()
        self._setup_logging()
        
    def _choose_output_file(self) -> str:
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
    
    def _ensure_output_directory(self):
        """Ensure the output directory exists for the output file and status file"""
        # Ensure directory for main output file
        output_dir = os.path.dirname(self.output_file)
        if output_dir:  # Only create directory if there's a directory path
            try:
                os.makedirs(output_dir, exist_ok=True)
                print(f"[*] Ensured output directory exists: {output_dir}")
            except (PermissionError, OSError) as e:
                print(f"[!] Could not create output directory {output_dir}: {e}")
                # Try to use a fallback location
                fallback_path = os.path.expanduser("~/loadgen.log")
                self.output_file = fallback_path
                print(f"[*] Using fallback output file: {fallback_path}")
        
        # Ensure directory for status file
        status_file = f"{self.output_file}.status"
        status_dir = os.path.dirname(status_file)
        if status_dir and status_dir != output_dir:  # Only if different from main output dir
            try:
                os.makedirs(status_dir, exist_ok=True)
                print(f"[*] Ensured status file directory exists: {status_dir}")
            except (PermissionError, OSError) as e:
                print(f"[!] Could not create status file directory {status_dir}: {e}")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(f"{self.output_file}.status", mode='a')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _write_log(self, line: str):
        """Thread-safe log writing"""
        with self.lock:
            with open(self.output_file, 'a') as f:
                f.write(line + '\n')
    
    def _randint(self, low: int, high: int) -> int:
        """Generate random integer between low and high (inclusive)"""
        if low > high:
            low, high = high, low
        return random.randint(low, high)
    
    def _pick(self, *choices) -> str:
        """Pick a random choice from the provided options"""
        return random.choice(choices)
    
    def _randhex(self, length: int = 8) -> str:
        """Generate random hexadecimal string"""
        return ''.join(random.choices('0123456789abcdef', k=length))
    
    def _randb64(self, length: int = 12) -> str:
        """Generate random base64-like string"""
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        return ''.join(random.choices(chars, k=length))
    
    def _rand_rt(self) -> str:
        """Generate random response time as decimal"""
        return f"0.{self._randint(0, 899):03d}"
    
    def _get_random_lines(self) -> int:
        """Generate a random number of lines up to the specified maximum"""
        return self._randint(1, self.lines_per_format)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        return datetime.now(timezone.utc).isoformat()
    
    def _get_apache_timestamp(self) -> str:
        """Get timestamp in Apache log format"""
        return datetime.now().strftime('%d/%b/%Y:%H:%M:%S %z')
    
    
    def run_concurrent(self) -> None:
        """Run all log generators concurrently"""
        self.logger.info(f"[*] Writing logs to: {self.output_file}")
        self.logger.info(f"[*] Concurrent generation: up to {self.lines_per_format} lines per format across 6 formats")
        
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {}
            
            for format_name, generator_class in LOG_GENERATORS.items():
                lines_to_generate = self._get_random_lines()
                generator = generator_class(lines_to_generate, self.output_file, self.lock, self.logger)
                future = executor.submit(generator.generate)
                futures[future] = format_name.upper()
            
            for future in as_completed(futures):
                name = futures[future]
                try:
                    future.result()
                except Exception as e:
                    self.logger.error(f"[!] {name} generator failed: {e}")
        
        self.logger.info(f"[OK] All formats finished. Output file: {self.output_file}")
    
    def run_with_duration(self, duration_seconds: int) -> None:
        """Run log generation for a specified duration, restarting if it finishes early"""
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        self.logger.info(f"[*] Starting time-based execution for {duration_seconds} seconds")
        self.logger.info(f"[*] Will run until: {datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')}")
        
        iteration = 1
        
        while time.time() < end_time:
            remaining_time = end_time - time.time()
            self.logger.info(f"[*] Starting iteration {iteration} (remaining: {remaining_time:.1f}s)")
            
            # Run the concurrent generation
            self.run_concurrent()
            
            # Check if we still have time left
            if time.time() < end_time:
                self.logger.info(f"[*] Iteration {iteration} completed, restarting for remaining time...")
                iteration += 1
                
                # Add pause between iterations if specified
                if self.pause_seconds > 0:
                    self.logger.info(f"[*] Pausing for {self.pause_seconds:.1f} seconds...")
                    time.sleep(self.pause_seconds)
            else:
                self.logger.info(f"[*] Time limit reached after {iteration} iteration(s)")
                break
        
        total_runtime = time.time() - start_time
        self.logger.info(f"[OK] Time-based execution completed. Total runtime: {total_runtime:.1f}s, Iterations: {iteration}")

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
        "apache", "json", "csv", "pipe", "kv", "hadoop", "all"
    ], default=env_config.get('format', 'all'), 
                       help="Log format to generate (default: all)")
    parser.add_argument("--duration", "-d", type=int, 
                       default=int(env_config.get('duration')) if env_config.get('duration') else None,
                       help="Run for specified duration in seconds (restarts if finishes early)")
    parser.add_argument("--pause", "-p", type=float, 
                       default=float(env_config.get('pause')) if env_config.get('pause') else 0.0,
                       help="Pause duration in seconds between iterations (default: 0.0)")
    
    args = parser.parse_args()
    
    generator = LogGenerator(
        output_file=args.output,
        lines_per_format=args.lines,
        pause_seconds=args.pause
    )
    
    # If duration is specified, use time-based execution
    if args.duration:
        if args.format != "all":
            generator.logger.warning("[!] Duration mode only supports 'all' format. Using all formats.")
        generator.run_with_duration(args.duration)
    else:
        # Original execution logic
        if args.format == "all":
            generator.run_concurrent()
        else:
            if args.format not in LOG_GENERATORS:
                generator.logger.error(f"Unknown format: {args.format}")
                return
            
            lines_to_generate = generator._get_random_lines()
            generator.logger.info(f"[*] Starting {args.format.upper()} generation of up to {args.lines} lines")
            
            generator_class = LOG_GENERATORS[args.format]
            format_generator = generator_class(lines_to_generate, generator.output_file, generator.lock, generator.logger)
            format_generator.generate()

if __name__ == "__main__":
    main()

