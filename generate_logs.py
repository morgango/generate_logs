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
    
    def _get_random_lines(self) -> int:
        """Generate a random number of lines up to the specified maximum"""
        return self._randint(1, self.lines_per_format)
    
    def _get_realistic_message(self, service: str, level: str) -> str:
        """Generate realistic log messages based on service and level"""
        messages = {
            "checkout": {
                "DEBUG": [
                    "Processing payment method validation",
                    "Validating cart contents before checkout",
                    "Checking inventory availability for items",
                    "Verifying user authentication token",
                    "Calculating shipping costs for order"
                ],
                "INFO": [
                    "User initiated checkout process",
                    "Payment processed successfully",
                    "Order confirmed and queued for fulfillment",
                    "Shipping address validated",
                    "Order total calculated: ${amount}"
                ],
                "WARN": [
                    "Payment method declined, retrying with backup",
                    "Inventory low for item {item_id}",
                    "Shipping address requires verification",
                    "Tax calculation failed, using default rate",
                    "User session expired during checkout"
                ],
                "ERROR": [
                    "Payment gateway timeout - retrying",
                    "Inventory check failed for item {item_id}",
                    "Address validation service unavailable",
                    "Credit card processing failed",
                    "Order creation failed due to system error"
                ],
                "CRITICAL": [
                    "Payment system completely down",
                    "Database connection lost during checkout",
                    "Critical security breach detected",
                    "Order processing system failure",
                    "Financial transaction system unavailable"
                ]
            },
            "inventory": {
                "DEBUG": [
                    "Checking stock levels for product {product_id}",
                    "Updating inventory counts after sale",
                    "Validating product availability",
                    "Processing stock adjustment request",
                    "Calculating reorder points"
                ],
                "INFO": [
                    "Product {product_id} stock updated",
                    "Inventory sync completed successfully",
                    "Stock level alert triggered for {product_id}",
                    "New product added to inventory",
                    "Bulk inventory import completed"
                ],
                "WARN": [
                    "Stock level below threshold for {product_id}",
                    "Inventory sync delayed due to network issues",
                    "Product {product_id} marked as discontinued",
                    "Warehouse capacity approaching limit",
                    "Stock discrepancy detected during audit"
                ],
                "ERROR": [
                    "Failed to update inventory for {product_id}",
                    "Database connection lost during stock check",
                    "Inventory sync service unavailable",
                    "Stock calculation error for product {product_id}",
                    "Warehouse system integration failed"
                ],
                "CRITICAL": [
                    "Inventory system completely down",
                    "Critical stock data corruption detected",
                    "Warehouse management system failure",
                    "Product database inaccessible",
                    "Inventory tracking system offline"
                ]
            },
            "payments": {
                "DEBUG": [
                    "Validating payment card details",
                    "Processing refund for transaction {txn_id}",
                    "Checking payment method eligibility",
                    "Verifying merchant account status",
                    "Calculating transaction fees"
                ],
                "INFO": [
                    "Payment of ${amount} processed successfully",
                    "Refund issued for transaction {txn_id}",
                    "Payment method updated for user {user_id}",
                    "Transaction {txn_id} completed",
                    "Payment gateway response received"
                ],
                "WARN": [
                    "Payment processing delayed due to high volume",
                    "Fraud detection triggered for transaction {txn_id}",
                    "Payment method expired for user {user_id}",
                    "Transaction fee calculation failed",
                    "Payment gateway rate limit exceeded"
                ],
                "ERROR": [
                    "Payment processing failed for transaction {txn_id}",
                    "Credit card declined for user {user_id}",
                    "Payment gateway timeout occurred",
                    "Transaction {txn_id} failed validation",
                    "Refund processing error for {txn_id}"
                ],
                "CRITICAL": [
                    "Payment system security breach detected",
                    "Financial data corruption in transaction {txn_id}",
                    "Payment gateway completely unavailable",
                    "Critical payment processing failure",
                    "Financial system integrity compromised"
                ]
            },
            "search": {
                "DEBUG": [
                    "Indexing new product {product_id}",
                    "Processing search query: {query}",
                    "Updating search index for category {category}",
                    "Validating search filters",
                    "Calculating search relevance scores"
                ],
                "INFO": [
                    "Search index updated successfully",
                    "User searched for: {query}",
                    "Search results returned in {time}ms",
                    "Search cache populated for query: {query}",
                    "Product {product_id} added to search index"
                ],
                "WARN": [
                    "Search index update delayed",
                    "Search query timeout for: {query}",
                    "Search cache miss for popular query",
                    "Search performance degraded",
                    "Index optimization required"
                ],
                "ERROR": [
                    "Search index corruption detected",
                    "Search service unavailable for query: {query}",
                    "Failed to update search index",
                    "Search database connection lost",
                    "Search query processing failed"
                ],
                "CRITICAL": [
                    "Search system completely down",
                    "Search index data corruption",
                    "Search database inaccessible",
                    "Critical search system failure",
                    "Search infrastructure offline"
                ]
            },
            "shipping": {
                "DEBUG": [
                    "Calculating shipping costs for order {order_id}",
                    "Validating shipping address",
                    "Processing shipping label request",
                    "Tracking package {tracking_id}",
                    "Updating delivery status"
                ],
                "INFO": [
                    "Package {tracking_id} shipped successfully",
                    "Delivery confirmed for order {order_id}",
                    "Shipping label generated for {tracking_id}",
                    "Package {tracking_id} out for delivery",
                    "Order {order_id} delivered successfully"
                ],
                "WARN": [
                    "Shipping address validation failed",
                    "Package {tracking_id} delivery delayed",
                    "Shipping cost calculation error",
                    "Tracking information unavailable for {tracking_id}",
                    "Delivery attempt failed for {tracking_id}"
                ],
                "ERROR": [
                    "Failed to generate shipping label",
                    "Package {tracking_id} lost in transit",
                    "Shipping service unavailable",
                    "Delivery confirmation failed",
                    "Tracking system integration error"
                ],
                "CRITICAL": [
                    "Shipping system completely down",
                    "Package tracking system offline",
                    "Critical delivery system failure",
                    "Shipping database inaccessible",
                    "Logistics system infrastructure down"
                ]
            }
        }
        
        # Get messages for the service, fallback to generic messages
        service_messages = messages.get(service, {
            "DEBUG": ["System debug information", "Processing request", "Validating input"],
            "INFO": ["Operation completed successfully", "User action processed", "System status update"],
            "WARN": ["Warning condition detected", "Performance degradation", "Resource usage high"],
            "ERROR": ["Operation failed", "System error occurred", "Request processing failed"],
            "CRITICAL": ["Critical system failure", "Service unavailable", "Data integrity issue"]
        })
        
        # Get messages for the level, fallback to generic
        level_messages = service_messages.get(level, ["System message", "Log entry", "Event occurred"])
        
        # Pick a random message and replace placeholders
        message = self._pick(*level_messages)
        
        # Replace placeholders with realistic values
        message = message.replace("{amount}", f"${self._randint(10, 999)}.{self._randint(0, 99):02d}")
        message = message.replace("{item_id}", f"item_{self._randint(1000, 9999)}")
        message = message.replace("{product_id}", f"prod_{self._randint(10000, 99999)}")
        message = message.replace("{user_id}", f"user_{self._randint(1000, 9999)}")
        message = message.replace("{txn_id}", f"txn_{self._randhex(8)}")
        message = message.replace("{order_id}", f"order_{self._randint(100000, 999999)}")
        message = message.replace("{tracking_id}", f"TRK{self._randhex(10).upper()}")
        message = message.replace("{query}", self._pick("laptop", "phone", "shoes", "book", "headphones", "watch", "camera"))
        message = message.replace("{category}", self._pick("electronics", "clothing", "books", "home", "sports"))
        message = message.replace("{time}", str(self._randint(50, 2000)))
        
        return message
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        return datetime.now(timezone.utc).isoformat()
    
    def _get_apache_timestamp(self) -> str:
        """Get timestamp in Apache log format"""
        return datetime.now().strftime('%d/%b/%Y:%H:%M:%S %z')
    
    def generate_apache_logs(self) -> None:
        """Generate Apache-style access logs"""
        lines_to_generate = self._get_random_lines()
        self.logger.info(f"[*] Apache: starting ({lines_to_generate} lines)")
        
        for i in range(1, lines_to_generate + 1):
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
            
            log_line = f'fmt=apache {ip} - - [{timestamp}] "{method} {path} HTTP/1.1" {status_code} {bytes_sent} "-" "{user_agent}" rt={response_time} upstream={upstream}'
            
            self._write_log(log_line)
            
            if i % 1000 == 0:
                self.logger.info(f"[+] Apache: {i}/{lines_to_generate}")
        
        self.logger.info(f"[OK] Apache: complete ({lines_to_generate})")
    
    def generate_json_logs(self) -> None:
        """Generate JSON formatted logs"""
        lines_to_generate = self._get_random_lines()
        self.logger.info(f"[*] JSON: starting ({lines_to_generate} lines)")
        
        for i in range(1, lines_to_generate + 1):
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
                "msg": self._get_realistic_message(service, level)
            }
            
            log_line = json.dumps(log_data)
            self._write_log(log_line)
            
            if i % 1000 == 0:
                self.logger.info(f"[+] JSON: {i}/{lines_to_generate}")
        
        self.logger.info(f"[OK] JSON: complete ({lines_to_generate})")
    
    def generate_csv_logs(self) -> None:
        """Generate CSV formatted logs"""
        lines_to_generate = self._get_random_lines()
        self.logger.info(f"[*] CSV: starting ({lines_to_generate} lines)")
        
        for i in range(1, lines_to_generate + 1):
            timestamp = self._get_timestamp()
            level = self._pick("DEBUG", "INFO", "WARN", "ERROR")
            service = self._pick("checkout", "inventory", "payments", "search", "shipping")
            user = f"u{self._randint(1000, 9999)}"
            latency = self._randint(5, 2000)
            status_code = self._pick(200, 201, 202, 204, 400, 401, 403, 404, 429, 500, 502)
            
            message = self._get_realistic_message(service, level)
            log_line = f"fmt=csv {timestamp},{level},{service},{user},{latency},{status_code},{message}"
            self._write_log(log_line)
            
            if i % 1000 == 0:
                self.logger.info(f"[+] CSV: {i}/{lines_to_generate}")
        
        self.logger.info(f"[OK] CSV: complete ({lines_to_generate})")
    
    def generate_pipe_logs(self) -> None:
        """Generate pipe-delimited logs"""
        lines_to_generate = self._get_random_lines()
        self.logger.info(f"[*] Pipe: starting ({lines_to_generate} lines)")
        
        for i in range(1, lines_to_generate + 1):
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
                self.logger.info(f"[+] Pipe: {i}/{lines_to_generate}")
        
        self.logger.info(f"[OK] Pipe: complete ({lines_to_generate})")
    
    def generate_kv_logs(self) -> None:
        """Generate key-value formatted logs"""
        lines_to_generate = self._get_random_lines()
        self.logger.info(f"[*] KV: starting ({lines_to_generate} lines)")
        
        for i in range(1, lines_to_generate + 1):
            timestamp = self._get_timestamp()
            level = self._pick("debug", "info", "notice", "warn", "error", "critical")
            service = self._pick("checkout", "inventory", "payments", "search", "shipping")
            request_id = f"req-{self._randhex(6)}"
            duration = self._randint(100, 5000)
            
            message = self._get_realistic_message(service, level)
            log_line = f'fmt=kv ts="{timestamp}" level={level} service={service} req={request_id} duration_ms={duration} msg="{message}"'
            self._write_log(log_line)
            
            if i % 1000 == 0:
                self.logger.info(f"[+] KV: {i}/{lines_to_generate}")
        
        self.logger.info(f"[OK] KV: complete ({lines_to_generate})")
    
    def generate_hadoop_logs(self) -> None:
        """Generate Hadoop-style logs"""
        lines_to_generate = self._get_random_lines()
        self.logger.info(f"[*] Hadoop: starting ({lines_to_generate} lines)")
        
        for i in range(1, lines_to_generate + 1):
            timestamp = self._get_timestamp()
            level = self._pick("INFO", "WARN", "ERROR", "DEBUG")
            component = self._pick("NameNode", "DataNode", "ResourceManager", "NodeManager", "JobTracker", "TaskTracker")
            hostname = f"hadoop-{self._randint(1, 10)}.cluster.local"
            job_id = f"job_{self._randint(100000, 999999)}_{self._randint(1000, 9999)}"
            task_id = f"task_{self._randint(100000, 999999)}_{self._randint(1000, 9999)}_{self._randint(0, 9)}"
            memory_mb = self._randint(1024, 8192)
            cpu_percent = self._randint(10, 100)
            duration = self._randint(1000, 30000)
            
            message = self._get_realistic_message("inventory", level)  # Use inventory service for Hadoop-style logs
            log_line = f"fmt=hadoop {timestamp} {level} {component}: {hostname} {job_id} {task_id} memory={memory_mb}MB cpu={cpu_percent}% duration={duration}ms {message}"
            self._write_log(log_line)
            
            if i % 1000 == 0:
                self.logger.info(f"[+] Hadoop: {i}/{lines_to_generate}")
        
        self.logger.info(f"[OK] Hadoop: complete ({lines_to_generate})")
    
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
        self.logger.info(f"[*] Concurrent generation: up to {self.lines_per_format} lines per format across 6 formats")
        
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {executor.submit(generator): name for name, generator in generators}
            
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

