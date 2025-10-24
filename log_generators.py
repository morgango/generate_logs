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
    
    def _get_realistic_message(self, service: str, level: str) -> str:
        """Generate realistic log messages based on service and level"""
        messages = {
            "checkout": {
                "DEBUG": [
                    "Processing payment method validation",
                    "Validating cart contents before checkout",
                    "Checking inventory availability for items",
                    "Verifying user authentication token",
                    "Calculating shipping costs for order",
                    "Applying promotional discounts",
                    "Validating coupon code",
                    "Checking user loyalty points"
                ],
                "INFO": [
                    "User initiated checkout process",
                    "Payment processed successfully",
                    "Order confirmed and queued for fulfillment",
                    "Shipping address validated",
                    "Order total calculated: ${amount}",
                    "User completed checkout in {time} seconds",
                    "Order {order_id} created successfully",
                    "Payment method updated successfully",
                    "Checkout process completed without issues",
                    "User added items to cart",
                    "Shipping method selected",
                    "Tax calculation completed",
                    "User profile updated",
                    "Cart contents validated",
                    "Discount applied successfully"
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
                    "Calculating reorder points",
                    "Syncing inventory with warehouse",
                    "Validating product data",
                    "Processing inventory updates"
                ],
                "INFO": [
                    "Product {product_id} stock updated",
                    "Inventory sync completed successfully",
                    "Stock level alert triggered for {product_id}",
                    "New product added to inventory",
                    "Bulk inventory import completed",
                    "Product {product_id} restocked",
                    "Inventory audit completed successfully",
                    "Stock levels synchronized across warehouses",
                    "Product {product_id} availability confirmed",
                    "Inventory report generated",
                    "Stock adjustment processed",
                    "Product catalog updated"
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
                    "Calculating transaction fees",
                    "Validating payment security",
                    "Processing payment authorization"
                ],
                "INFO": [
                    "Payment of ${amount} processed successfully",
                    "Refund issued for transaction {txn_id}",
                    "Payment method updated for user {user_id}",
                    "Transaction {txn_id} completed",
                    "Payment gateway response received",
                    "Payment authorization successful",
                    "Transaction {txn_id} settled",
                    "Payment method verified for user {user_id}",
                    "Refund processed for order {order_id}",
                    "Payment confirmation sent",
                    "Transaction fees calculated",
                    "Payment security check passed"
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
                    "Calculating search relevance scores",
                    "Building search suggestions",
                    "Optimizing search results"
                ],
                "INFO": [
                    "Search index updated successfully",
                    "User searched for: {query}",
                    "Search results returned in {time}ms",
                    "Search cache populated for query: {query}",
                    "Product {product_id} added to search index",
                    "Search analytics updated",
                    "Search performance optimized",
                    "Search suggestions generated",
                    "Search index rebuilt successfully",
                    "Search filters applied",
                    "Search ranking updated",
                    "Search cache hit for popular query"
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
                    "Updating delivery status",
                    "Validating shipping options",
                    "Processing delivery confirmation"
                ],
                "INFO": [
                    "Package {tracking_id} shipped successfully",
                    "Delivery confirmed for order {order_id}",
                    "Shipping label generated for {tracking_id}",
                    "Package {tracking_id} out for delivery",
                    "Order {order_id} delivered successfully",
                    "Shipping address validated",
                    "Package {tracking_id} in transit",
                    "Delivery scheduled for order {order_id}",
                    "Shipping confirmation sent",
                    "Package {tracking_id} arrived at destination",
                    "Delivery route optimized",
                    "Shipping costs calculated"
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
    
    def generate(self) -> None:
        """Abstract method to be implemented by subclasses"""
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
            ip = f"{self._randint(1, 255)}.{self._randint(1, 255)}.{self._randint(1, 255)}.{self._randint(1, 255)}"
            timestamp = self._get_apache_timestamp()
            path = self._pick(
                "/", "/index.html", "/health", "/login", 
                f"/api/items", f"/api/orders?id={self._randint(1, 9999)}"
            )
            method = self._pick("GET", "POST", "PUT", "DELETE")
            status_code = self._pick(200, 201, 204, 301, 302, 400, 401, 403, 404, 429, 500, 502, 503)
            bytes_sent = self._randint(100, 90000)
            user_agent = f"{self._pick('Mozilla', 'Chrome', 'Safari', 'Firefox')}/{self._randint(1, 9)}.{self._randint(0, 9)}"
            response_time = f"{self._randint(0, 9)}.{self._randint(0, 999)}"
            upstream = self._pick("checkout", "inventory", "payments", "search", "shipping")
            
            # Updated to match the working pattern from ELASTICSEARCH_GROK_PATTERNS.md
            log_line = f'fmt=apache {ip} - - [{timestamp}] "{method} {path} HTTP/1.1" {status_code} {bytes_sent} "-" "{user_agent}" {response_time} {upstream}'
            
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
                "duration_ms": duration,
                "msg": self._get_realistic_message(service, level)
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
            user = f"u{self._randint(1000, 9999)}"
            latency = self._randint(5, 2000)
            status_code = self._pick(200, 201, 202, 204, 400, 401, 403, 404, 429, 500, 502)
            
            message = self._get_realistic_message(service, level)
            log_line = f"fmt=csv {timestamp},{level},{service},{user},{latency},{status_code},{message}"
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
                self.logger.info(f"[+] Pipe: {i}/{self.lines}")
        
        self.logger.info(f"[OK] Pipe: complete ({self.lines})")


class KvLogGenerator(BaseLogGenerator):
    """Generates key-value formatted logs"""
    
    def generate(self) -> None:
        """Generate key-value formatted logs"""
        self.logger.info(f"[*] KV: starting ({self.lines} lines)")
        
        for i in range(1, self.lines + 1):
            timestamp = self._get_timestamp()
            level = self._pick("debug", "info", "notice", "warn", "error", "critical")
            service = self._pick("checkout", "inventory", "payments", "search", "shipping")
            request_id = f"req-{self._randhex(6)}"
            duration = self._randint(100, 5000)
            
            message = self._get_realistic_message(service, level)
            log_line = f'fmt=kv ts={timestamp} level={level} service={service} req={request_id} duration_ms={duration} msg={message}'
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
            level = self._pick("INFO", "WARN", "ERROR", "DEBUG")
            component = self._pick("NameNode", "DataNode", "ResourceManager", "NodeManager", "JobTracker", "TaskTracker")
            hostname = f"hadoop-{self._randint(1, 10)}.cluster.local"
            job_id = f"job_{self._randint(100000, 999999)}_{self._randint(1000, 9999)}"
            task_id = f"task_{self._randint(100000, 999999)}_{self._randint(1000, 9999)}_{self._randint(0, 9)}"
            memory_mb = self._randint(1024, 8192)
            cpu_percent = self._randint(10, 100)
            duration = self._randint(1000, 30000)
            
            message = self._get_realistic_message("inventory", level)  # Use inventory service for Hadoop-style logs
            log_line = f"fmt=hadoop {timestamp} {level} {component} {hostname} {job_id} {task_id} memory={memory_mb} cpu={cpu_percent} duration={duration} {message}"
            self._write_log(log_line)
            
            if i % 1000 == 0:
                self.logger.info(f"[+] Hadoop: {i}/{self.lines}")
        
        self.logger.info(f"[OK] Hadoop: complete ({self.lines})")


class LogstashLogGenerator(BaseLogGenerator):
    """Generates Logstash-style structured logs"""
    
    def generate(self) -> None:
        """Generate Logstash-style structured logs"""
        self.logger.info(f"[*] Logstash: starting ({self.lines} lines)")
        
        for i in range(1, self.lines + 1):
            timestamp = self._get_timestamp()
            level = self._pick("DEBUG", "INFO", "WARN", "ERROR", "FATAL")
            service = self._pick("checkout", "inventory", "payments", "search", "shipping")
            request_id = f"req-{self._randhex(8)}"
            session_id = f"sess-{self._randhex(12)}"
            user_id = f"user-{self._randint(1000, 9999)}"
            duration = self._randint(50, 5000)
            status_code = self._pick(200, 201, 202, 204, 400, 401, 403, 404, 429, 500, 502, 503)
            ip_address = f"10.{self._randint(0, 255)}.{self._randint(0, 255)}.{self._randint(1, 254)}"
            user_agent = self._pick("Mozilla/5.0", "curl/8.0", "Go-http-client/1.1", "Python-urllib/3.10")
            
            message = self._get_realistic_message(service, level)
            
            # Logstash format: structured with clear field separators
            log_line = f"fmt=logstash @timestamp={timestamp}; level={level}; service={service}; request_id={request_id}; session_id={session_id}; user_id={user_id}; duration_ms={duration}; status_code={status_code}; ip={ip_address}; user_agent={user_agent}; message={message}"
            self._write_log(log_line)
            
            if i % 1000 == 0:
                self.logger.info(f"[+] Logstash: {i}/{self.lines}")
        
        self.logger.info(f"[OK] Logstash: complete ({self.lines})")


class NginxLogGenerator(BaseLogGenerator):
    """Generates NGINX access logs"""
    
    def _get_nginx_timestamp(self) -> str:
        """Get timestamp in NGINX log format"""
        return datetime.now().strftime('%d/%b/%Y:%H:%M:%S %z')
    
    def generate(self) -> None:
        """Generate NGINX access logs"""
        self.logger.info(f"[*] NGINX: starting ({self.lines} lines)")
        
        for i in range(1, self.lines + 1):
            ip = f"{self._randint(1, 255)}.{self._randint(1, 255)}.{self._randint(1, 255)}.{self._randint(1, 255)}"
            timestamp = self._get_nginx_timestamp()
            method = self._pick("GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS")
            path = self._pick(
                "/", "/api/v1/users", "/api/v1/orders", "/api/v1/products", 
                "/static/css/style.css", "/static/js/app.js", "/health", "/metrics",
                f"/api/v1/orders/{self._randint(1000, 9999)}", f"/api/v1/users/{self._randint(100, 999)}"
            )
            protocol = "HTTP/1.1"
            status_code = self._pick(200, 201, 204, 301, 302, 304, 400, 401, 403, 404, 429, 500, 502, 503, 504)
            bytes_sent = self._randint(100, 50000)
            referer = self._pick("-", "https://example.com", "https://google.com", "https://github.com")
            user_agent = self._pick(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "curl/8.0.1", "Go-http-client/1.1", "Python-urllib/3.10"
            )
            response_time = self._rand_rt()
            upstream = self._pick("checkout", "inventory", "payments", "search", "shipping")
            
            log_line = f'fmt=nginx {ip} - - [{timestamp}] "{method} {path} {protocol}" {status_code} {bytes_sent} "{referer}" "{user_agent}" rt={response_time} upstream={upstream}'
            self._write_log(log_line)
            
            if i % 1000 == 0:
                self.logger.info(f"[+] NGINX: {i}/{self.lines}")
        
        self.logger.info(f"[OK] NGINX: complete ({self.lines})")


class TomcatLogGenerator(BaseLogGenerator):
    """Generates Apache Tomcat logs"""
    
    def generate(self) -> None:
        """Generate Apache Tomcat logs"""
        self.logger.info(f"[*] Tomcat: starting ({self.lines} lines)")
        
        for i in range(1, self.lines + 1):
            timestamp = self._get_timestamp()
            level = self._pick("INFO", "WARN", "ERROR", "DEBUG", "FATAL")
            component = self._pick("org.apache.catalina.core.ContainerBase", "org.apache.catalina.startup.Catalina", 
                                 "org.apache.catalina.session.StandardSession", "org.apache.catalina.connector.CoyoteAdapter")
            thread = f"http-nio-8080-exec-{self._randint(1, 20)}"
            message = self._get_realistic_message("checkout", level)
            
            # Tomcat format: timestamp level component thread message
            log_line = f"fmt=tomcat {timestamp} {level} {component} {thread} {message}"
            self._write_log(log_line)
            
            if i % 1000 == 0:
                self.logger.info(f"[+] Tomcat: {i}/{self.lines}")
        
        self.logger.info(f"[OK] Tomcat: complete ({self.lines})")


class MysqlLogGenerator(BaseLogGenerator):
    """Generates MySQL slow query logs"""
    
    def generate(self) -> None:
        """Generate MySQL slow query logs"""
        self.logger.info(f"[*] MySQL: starting ({self.lines} lines)")
        
        for i in range(1, self.lines + 1):
            timestamp = self._get_timestamp()
            user = f"user_{self._randint(100, 999)}"
            host = f"10.{self._randint(0, 255)}.{self._randint(0, 255)}.{self._randint(1, 254)}"
            query_time = f"{self._randint(1, 10)}.{self._randint(0, 999):03d}"
            lock_time = f"0.{self._randint(0, 99):03d}"
            rows_sent = self._randint(0, 1000)
            rows_examined = self._randint(100, 10000)
            database = self._pick("ecommerce", "inventory", "payments", "users", "analytics")
            
            # Common SQL queries
            queries = [
                f"SELECT * FROM {database}.orders WHERE user_id = {self._randint(1000, 9999)}",
                f"SELECT COUNT(*) FROM {database}.products WHERE category = '{self._pick('electronics', 'clothing', 'books')}'",
                f"UPDATE {database}.inventory SET stock = stock - {self._randint(1, 10)} WHERE product_id = {self._randint(1000, 9999)}",
                f"INSERT INTO {database}.logs (message, timestamp) VALUES ('{self._get_realistic_message('inventory', 'INFO')}', NOW())",
                f"DELETE FROM {database}.sessions WHERE created_at < DATE_SUB(NOW(), INTERVAL 7 DAY)"
            ]
            
            query = self._pick(*queries)
            
            log_line = f"fmt=mysql {timestamp} {user}[{user}] @ {host} [{timestamp}] {query_time} {lock_time} {rows_sent} {rows_examined} {database} {query}"
            self._write_log(log_line)
            
            if i % 1000 == 0:
                self.logger.info(f"[+] MySQL: {i}/{self.lines}")
        
        self.logger.info(f"[OK] MySQL: complete ({self.lines})")


class RedisLogGenerator(BaseLogGenerator):
    """Generates Redis logs"""
    
    def generate(self) -> None:
        """Generate Redis logs"""
        self.logger.info(f"[*] Redis: starting ({self.lines} lines)")
        
        for i in range(1, self.lines + 1):
            timestamp = self._get_timestamp()
            level = self._pick("INFO", "WARN", "ERROR", "DEBUG")
            pid = self._randint(1000, 9999)
            role = self._pick("master", "slave", "sentinel")
            message = self._get_realistic_message("inventory", level)
            
            # Redis format: timestamp level pid role message
            log_line = f"fmt=redis {timestamp} {level} {pid}:C {role} {message}"
            self._write_log(log_line)
            
            if i % 1000 == 0:
                self.logger.info(f"[+] Redis: {i}/{self.lines}")
        
        self.logger.info(f"[OK] Redis: complete ({self.lines})")


class SyslogLogGenerator(BaseLogGenerator):
    """Generates custom syslog-formatted logs with structured data"""
    
    def __init__(self, lines: int, output_file: str, lock: threading.Lock, logger: logging.Logger, 
                 syslog_file: str = None):
        super().__init__(lines, output_file, lock, logger)
        # Only create separate syslog file if explicitly requested
        self.syslog_file = syslog_file
        self.write_to_separate_file = syslog_file is not None
    
    def _get_syslog_priority(self, level: str) -> str:
        """Map log levels to syslog priority codes"""
        priority_map = {
            "DEBUG": "7",    # LOG_DEBUG
            "INFO": "6",     # LOG_INFO  
            "NOTICE": "5",   # LOG_NOTICE
            "WARN": "4",     # LOG_WARNING
            "ERROR": "3",    # LOG_ERR
            "CRITICAL": "2", # LOG_CRIT
            "ALERT": "1",    # LOG_ALERT
            "EMERG": "0"     # LOG_EMERG
        }
        return priority_map.get(level, "6")
    
    def _get_syslog_facility(self, service: str) -> str:
        """Map services to syslog facility codes"""
        facility_map = {
            "checkout": "16",    # LOG_LOCAL0
            "inventory": "17",   # LOG_LOCAL1
            "payments": "18",    # LOG_LOCAL2
            "search": "19",      # LOG_LOCAL3
            "shipping": "20",    # LOG_LOCAL4
            "auth": "4",         # LOG_AUTH
            "mail": "2",         # LOG_MAIL
            "daemon": "3",       # LOG_DAEMON
            "kern": "0"          # LOG_KERN
        }
        return facility_map.get(service, "16")
    
    def _generate_structured_data(self, service: str, level: str) -> str:
        """Generate RFC 5424 structured data"""
        request_id = f"req-{self._randhex(8)}"
        session_id = f"sess-{self._randhex(12)}"
        user_id = f"user-{self._randint(1000, 9999)}"
        duration = self._randint(10, 5000)
        status_code = self._pick(200, 201, 204, 400, 401, 403, 404, 429, 500, 502, 503)
        ip_address = f"10.{self._randint(0, 255)}.{self._randint(0, 255)}.{self._randint(1, 254)}"
        # RFC 5424 structured data format
        structured_data = f'[app@12345 service="{service}" request_id="{request_id}" session_id="{session_id}" user_id="{user_id}" duration_ms="{duration}" status_code="{status_code}" client_ip="{ip_address}"]'
        
        return structured_data
    
    def _write_syslog_file(self, line: str):
        """Write to separate syslog file if specified"""
        if self.write_to_separate_file and self.syslog_file:
            with self.lock:
                with open(self.syslog_file, 'a') as f:
                    f.write(line + '\n')
    
    def generate(self) -> None:
        """Generate custom syslog-formatted logs"""
        self.logger.info(f"[*] Syslog: starting ({self.lines} lines)")
        
        for i in range(1, self.lines + 1):
            timestamp = self._get_timestamp()
            level = self._pick("DEBUG", "INFO", "NOTICE", "WARN", "ERROR", "CRITICAL", "ALERT", "EMERG")
            service = self._pick("checkout", "inventory", "payments", "search", "shipping", "auth", "mail", "daemon")
            hostname = f"app-{self._randint(1, 10)}.cluster.local"
            app_name = f"loggen-{service}"
            process_id = self._randint(1000, 9999)
            
            # Generate structured data
            structured_data = self._generate_structured_data(service, level)
            
            # Generate message
            message = self._get_realistic_message(service, level)
            
            # Get syslog priority and facility
            priority = self._get_syslog_priority(level)
            facility = self._get_syslog_facility(service)
            
            # Custom syslog format: RFC 5424 with custom structured data
            # Format: <PRI>VERSION TIMESTAMP HOSTNAME APP-NAME PROCID MSGID STRUCTURED-DATA MSG
            # Add syslog identifier for easy filtering
            log_line = f'SYSLOG_RFC5424 <{facility}{priority}>1 {timestamp} {hostname} {app_name} {process_id} - {structured_data} {message}'
            
            # Write to main file (always)
            self._write_log(log_line)
            
            # Write to separate syslog file (only if specified)
            self._write_syslog_file(log_line)
            
            if i % 1000 == 0:
                self.logger.info(f"[+] Syslog: {i}/{self.lines}")
        
        self.logger.info(f"[OK] Syslog: complete ({self.lines})")


# Registry of all available log generators
LOG_GENERATORS = {
    "apache": ApacheLogGenerator,
    "csv": CsvLogGenerator,
    "pipe": PipeLogGenerator,
    "kv": KvLogGenerator,
    "hadoop": HadoopLogGenerator,
    "logstash": LogstashLogGenerator,
    "nginx": NginxLogGenerator,
    "tomcat": TomcatLogGenerator,
    "mysql": MysqlLogGenerator,
    "redis": RedisLogGenerator,
    "syslog": SyslogLogGenerator,
}