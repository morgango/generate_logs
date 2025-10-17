"""
Log Generator Classes

This module contains individual log generator classes for different log formats.
Each class is responsible for generating logs in a specific format.
"""

import random
import json
import threading
from datetime import datetime, timezone
from typing import List, Dict, Any
import logging


class BaseLogGenerator:
    """Base class for all log generators"""
    
    def __init__(self, lines: int, output_file: str, lock: threading.Lock, logger: logging.Logger):
        self.lines = lines
        self.output_file = output_file
        self.lock = lock
        self.logger = logger
    
    def _randint(self, min_val: int, max_val: int) -> int:
        """Generate random integer between min and max (inclusive)"""
        return random.randint(min_val, max_val)
    
    def _pick(self, *choices):
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
    
    def _write_log(self, line: str):
        """Thread-safe log writing"""
        with self.lock:
            with open(self.output_file, 'a') as f:
                f.write(line + '\n')
    
    def generate(self) -> None:
        """Generate logs - to be implemented by subclasses"""
        raise NotImplementedError


class ApacheLogGenerator(BaseLogGenerator):
    """Generates Apache-style access logs"""
    
    def _get_apache_timestamp(self) -> str:
        """Get timestamp in Apache log format"""
        return datetime.now().strftime('%d/%b/%Y:%H:%M:%S %z')
    
    def generate(self) -> None:
        """Generate Apache-style access logs"""
        self.logger.info(f"[*] Apache: starting ({self.lines} lines)")
        
        for i in range(1, self.lines + 1):
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
                self.logger.info(f"[+] Apache: {i}/{self.lines}")
        
        self.logger.info(f"[OK] Apache: complete ({self.lines})")


class JsonLogGenerator(BaseLogGenerator):
    """Generates JSON formatted logs"""
    
    def generate(self) -> None:
        """Generate JSON formatted logs"""
        self.logger.info(f"[*] JSON: starting ({self.lines} lines)")
        
        for i in range(1, self.lines + 1):
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
                "duration": duration,
                "msg": f"Processing {self._pick('order', 'payment', 'inventory', 'search')} request",
                "req_id": self._randhex(16),
                "ip": f"10.{self._randint(0, 255)}.{self._randint(0, 255)}.{self._randint(0, 255)}"
            }
            
            log_line = json.dumps(log_data)
            self._write_log(log_line)
            
            if i % 1000 == 0:
                self.logger.info(f"[+] JSON: {i}/{self.lines}")
        
        self.logger.info(f"[OK] JSON: complete ({self.lines})")


class CsvLogGenerator(BaseLogGenerator):
    """Generates CSV formatted logs"""
    
    def generate(self) -> None:
        """Generate CSV formatted logs"""
        self.logger.info(f"[*] CSV: starting ({self.lines} lines)")
        
        for i in range(1, self.lines + 1):
            timestamp = self._get_timestamp()
            level = self._pick("DEBUG", "INFO", "WARN", "ERROR")
            service = self._pick("checkout", "inventory", "payments", "search", "shipping")
            user_id = self._randint(1000, 9999)
            session_id = self._randhex(12)
            duration = self._randint(50, 2000)
            status = self._pick("success", "error", "timeout")
            
            log_line = f"{timestamp},{level},{service},{user_id},{session_id},{duration},{status}"
            self._write_log(log_line)
            
            if i % 1000 == 0:
                self.logger.info(f"[+] CSV: {i}/{self.lines}")
        
        self.logger.info(f"[OK] CSV: complete ({self.lines})")


class PipeLogGenerator(BaseLogGenerator):
    """Generates pipe-delimited logs"""
    
    def generate(self) -> None:
        """Generate pipe-delimited logs"""
        self.logger.info(f"[*] Pipe: starting ({self.lines} lines)")
        
        for i in range(1, self.lines + 1):
            timestamp = self._get_timestamp()
            level = self._pick("INFO", "WARN", "ERROR")
            component = self._pick("auth", "db", "cache", "api", "worker")
            message = f"User {self._randint(1000, 9999)} performed {self._pick('login', 'logout', 'purchase', 'search')}"
            duration = self._randint(10, 1000)
            
            log_line = f"{timestamp}|{level}|{component}|{message}|{duration}ms"
            self._write_log(log_line)
            
            if i % 1000 == 0:
                self.logger.info(f"[+] Pipe: {i}/{self.lines}")
        
        self.logger.info(f"[OK] Pipe: complete ({self.lines})")


class KvLogGenerator(BaseLogGenerator):
    """Generates key-value formatted logs"""
    
    def generate(self) -> None:
        """Generate key-value formatted logs"""
        self.logger.info(f"[*] KV: starting ({self.lines} lines)")
        
        for i in range(1, self.lines + 1):
            timestamp = self._get_timestamp()
            level = self._pick("INFO", "WARN", "ERROR")
            service = self._pick("checkout", "inventory", "payments", "search", "shipping")
            user = f"u{self._randint(1000, 9999)}"
            action = self._pick("create", "update", "delete", "read")
            duration = self._randint(20, 1500)
            
            log_line = f"timestamp={timestamp} level={level} service={service} user={user} action={action} duration={duration}ms"
            self._write_log(log_line)
            
            if i % 1000 == 0:
                self.logger.info(f"[+] KV: {i}/{self.lines}")
        
        self.logger.info(f"[OK] KV: complete ({self.lines})")


class HadoopLogGenerator(BaseLogGenerator):
    """Generates Hadoop-style logs"""
    
    def generate(self) -> None:
        """Generate Hadoop-style logs"""
        self.logger.info(f"[*] Hadoop: starting ({self.lines} lines)")
        
        for i in range(1, self.lines + 1):
            timestamp = self._get_timestamp()
            level = self._pick("INFO", "WARN", "ERROR")
            component = self._pick("namenode", "datanode", "jobtracker", "tasktracker")
            message = f"Block {self._randhex(8)} replicated to {self._randint(1, 3)} nodes"
            duration = self._randint(100, 5000)
            
            log_line = f"{timestamp} {level} {component}: {message} (took {duration}ms)"
            self._write_log(log_line)
            
            if i % 1000 == 0:
                self.logger.info(f"[+] Hadoop: {i}/{self.lines}")
        
        self.logger.info(f"[OK] Hadoop: complete ({self.lines})")


# Registry of available log generators
LOG_GENERATORS = {
    'apache': ApacheLogGenerator,
    'json': JsonLogGenerator,
    'csv': CsvLogGenerator,
    'pipe': PipeLogGenerator,
    'kv': KvLogGenerator,
    'hadoop': HadoopLogGenerator
}
