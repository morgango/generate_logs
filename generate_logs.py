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
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        return datetime.now(timezone.utc).isoformat()
    
    def _get_apache_timestamp(self) -> str:
        """Get timestamp in Apache log format"""
        return datetime.now().strftime('%d/%b/%Y:%H:%M:%S %z')
    
    def generate_apache_logs(self) -> None:
        """Generate Apache-style access logs"""
        self.logger.info(f"[*] Apache: starting ({self.lines_per_format} lines)")
        
        for i in range(1, self.lines_per_format + 1):
            ip = f"192.168.{self._randint(0, 1)}.{self._randint(10, 250)}"
            timestamp = self._get_apache_timestamp()
            path = self._pick(
                "/", "/index.html", "/health", "/login", 
                f"/api/items", f"/api/orders?id={self._randint(1, 9999)}"
            )
            method = self._pick("GET", "POST", "PUT", "DELETE")
            status_code = self._pick(200, 201, 204, 301, 302, 400, 401, 403, 404, 429, 500, 502, 503)
            bytes_sent = self._randint(100, 90000)
            user_agent = self._pick(
                "curl/8.0", "Mozilla/5.0", "Go-http-client/1.1", "Python-urllib/3.10"
            )
            response_time = self._rand_rt()
            upstream = self._pick("checkout", "inventory", "payments", "search", "shipping")
            
            log_line = f'{ip} - - [{timestamp}] "{method} {path} HTTP/1.1" {status_code} {bytes_sent} "-" "{user_agent}" rt={response_time} upstream={upstream}'
            
            self._write_log(log_line)
            
            if i % 1000 == 0:
                self.logger.info(f"[+] Apache: {i}/{self.lines_per_format}")
        
        self.logger.info(f"[OK] Apache: complete ({self.lines_per_format})")
    
    def generate_json_logs(self) -> None:
        """Generate JSON formatted logs"""
        self.logger.info(f"[*] JSON: starting ({self.lines_per_format} lines)")
        
        for i in range(1, self.lines_per_format + 1):
            timestamp = self._get_timestamp()
            level = self._pick("DEBUG", "INFO", "NOTICE", "WARN", "ERROR", "CRITICAL")
            service = self._pick("checkout", "inventory", "payments", "search", "shipping")
            duration = self._randint(10, 5000)
            user = f"u{self._randint(1000, 9999)}"
            
            log_data = {
                "fmt": "json",
                "ts": timestamp,
                "level": level,
                "service": service,
                "user": user,
                "duration_ms": duration,
                "msg": "json synthetic event"
            }
            
            log_line = json.dumps(log_data)
            self._write_log(log_line)
            
            if i % 1000 == 0:
                self.logger.info(f"[+] JSON: {i}/{self.lines_per_format}")
        
        self.logger.info(f"[OK] JSON: complete ({self.lines_per_format})")
    
    def generate_csv_logs(self) -> None:
        """Generate CSV formatted logs"""
        self.logger.info(f"[*] CSV: starting ({self.lines_per_format} lines)")
        
        for i in range(1, self.lines_per_format + 1):
            timestamp = self._get_timestamp()
            level = self._pick("DEBUG", "INFO", "WARN", "ERROR")
            service = self._pick("checkout", "inventory", "payments", "search", "shipping")
            user = f"u{self._randint(1000, 9999)}"
            latency = self._randint(5, 2000)
            status_code = self._pick(200, 201, 202, 204, 400, 401, 403, 404, 429, 500, 502)
            
            log_line = f"fmt=csv {timestamp},{level},{service},{user},{latency},{status_code}"
            self._write_log(log_line)
            
            if i % 1000 == 0:
                self.logger.info(f"[+] CSV: {i}/{self.lines_per_format}")
        
        self.logger.info(f"[OK] CSV: complete ({self.lines_per_format})")
    
    def generate_pipe_logs(self) -> None:
        """Generate pipe-delimited logs"""
        self.logger.info(f"[*] Pipe: starting ({self.lines_per_format} lines)")
        
        for i in range(1, self.lines_per_format + 1):
            timestamp = self._get_timestamp()
            level = self._pick("DEBUG", "INFO", "WARN", "ERROR")
            service = self._pick("checkout", "inventory", "payments", "search", "shipping")
            transaction = f"tx-{self._randhex(10)}"
            cents = self._randint(0, 99999)
            amount = f"{cents // 100}.{cents % 100:02d}"
            country = self._pick("US", "CA", "GB", "DE", "FR", "IN", "BR", "AU", "JP", "SE", "NL")
            session = self._randb64(12)
            
            log_line = f"fmt=pipe {timestamp}|{level}|{service}|txn={transaction}|amount={amount}|country={country}|session={session}"
            self._write_log(log_line)
            
            if i % 1000 == 0:
                self.logger.info(f"[+] Pipe: {i}/{self.lines_per_format}")
        
        self.logger.info(f"[OK] Pipe: complete ({self.lines_per_format})")
    
    def generate_kv_logs(self) -> None:
        """Generate key-value formatted logs"""
        self.logger.info(f"[*] KV: starting ({self.lines_per_format} lines)")
        
        for i in range(1, self.lines_per_format + 1):
            timestamp = self._get_timestamp()
            level = self._pick("debug", "info", "notice", "warn", "error", "critical")
            service = self._pick("checkout", "inventory", "payments", "search", "shipping")
            request_id = f"req-{self._randhex(6)}"
            duration = self._randint(100, 5000)
            
            log_line = f'fmt=kv ts="{timestamp}" level={level} service={service} req={request_id} duration_ms={duration} msg="keyvalue synthetic event"'
            self._write_log(log_line)
            
            if i % 1000 == 0:
                self.logger.info(f"[+] KV: {i}/{self.lines_per_format}")
        
        self.logger.info(f"[OK] KV: complete ({self.lines_per_format})")
    
    def generate_hadoop_logs(self) -> None:
        """Generate Hadoop-style logs"""
        self.logger.info(f"[*] Hadoop: starting ({self.lines_per_format} lines)")
        
        for i in range(1, self.lines_per_format + 1):
            timestamp = self._get_timestamp()
            level = self._pick("INFO", "WARN", "ERROR", "DEBUG")
            component = self._pick("NameNode", "DataNode", "ResourceManager", "NodeManager", "JobTracker", "TaskTracker")
            hostname = f"hadoop-{self._randint(1, 10)}.cluster.local"
            job_id = f"job_{self._randint(100000, 999999)}_{self._randint(1000, 9999)}"
            task_id = f"task_{self._randint(100000, 999999)}_{self._randint(1000, 9999)}_{self._randint(0, 9)}"
            memory_mb = self._randint(1024, 8192)
            cpu_percent = self._randint(10, 100)
            duration = self._randint(1000, 30000)
            
            log_line = f"{timestamp} {level} {component}: {hostname} {job_id} {task_id} memory={memory_mb}MB cpu={cpu_percent}% duration={duration}ms hadoop synthetic event"
            self._write_log(log_line)
            
            if i % 1000 == 0:
                self.logger.info(f"[+] Hadoop: {i}/{self.lines_per_format}")
        
        self.logger.info(f"[OK] Hadoop: complete ({self.lines_per_format})")
    
    def run_concurrent(self) -> None:
        """Run all log generators concurrently"""
        generators = [
            ("Apache", self.generate_apache_logs),
            ("JSON", self.generate_json_logs),
            ("CSV", self.generate_csv_logs),
            ("Pipe", self.generate_pipe_logs),
            ("KV", self.generate_kv_logs),
            ("Hadoop", self.generate_hadoop_logs)
        ]
        
        self.logger.info(f"[*] Writing logs to: {self.output_file}")
        self.logger.info(f"[*] Concurrent generation: {self.lines_per_format * 6} total lines across 6 formats")
        
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {executor.submit(generator): name for name, generator in generators}
            
            for future in as_completed(futures):
                name = futures[future]
                try:
                    future.result()
                except Exception as e:
                    self.logger.error(f"[!] {name} generator failed: {e}")
        
        self.logger.info(f"[OK] All formats finished. Total lines: {self.lines_per_format * 6}. Output file: {self.output_file}")
    
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
            format_map = {
                "apache": generator.generate_apache_logs,
                "json": generator.generate_json_logs,
                "csv": generator.generate_csv_logs,
                "pipe": generator.generate_pipe_logs,
                "kv": generator.generate_kv_logs,
                "hadoop": generator.generate_hadoop_logs
            }
            format_map[args.format]()

if __name__ == "__main__":
    main()

