"""
Example Implementation: Event Generation for Elastic Observability

This demonstrates how to generate logs with intentional patterns/events
that can be detected by Elastic Observability.

This is a conceptual example - it shows the approach without modifying
the existing codebase.
"""

import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class EventType(Enum):
    """Types of events that can be generated"""
    CROSS_FORMAT_ATTACK = "cross_format_attack"
    ERROR_BURST = "error_burst"
    SCANNING_PATTERN = "scanning_pattern"
    BRUTE_FORCE = "brute_force"
    SERVICE_DEGRADATION = "service_degradation"


@dataclass
class EventConfig:
    """Configuration for a single event"""
    id: str
    name: str
    type: EventType
    start_time: str  # "HH:MM:SS" or "+5m" for relative
    duration_seconds: int
    ip: str
    affected_formats: List[str]  # ["apache", "nginx"]
    
    # Format-specific configs
    apache_config: Optional[Dict] = None
    nginx_config: Optional[Dict] = None
    
    # Generic event parameters
    error_rate: float = 0.7  # 0.0 to 1.0
    error_codes: List[int] = None
    
    def __post_init__(self):
        if self.error_codes is None:
            self.error_codes = [403, 404, 500]


class EventCoordinator:
    """Manages event state and coordinates event generation across formats"""
    
    def __init__(self, events: List[EventConfig], start_time: datetime = None):
        """
        Initialize event coordinator
        
        Args:
            events: List of event configurations
            start_time: When log generation started (for relative timing)
        """
        self.events = events
        self.start_time = start_time or datetime.now()
        self.active_events: Dict[str, EventConfig] = {}
        self.event_state: Dict[str, Dict] = {}  # Track event progress
        
        # Initialize event states
        for event in events:
            self.event_state[event.id] = {
                "apache_logs_generated": 0,
                "nginx_logs_generated": 0,
                "started": False,
                "ended": False
            }
    
    def get_active_event(self, format_type: str, current_time: datetime) -> Optional[EventConfig]:
        """
        Check if there's an active event for the given format at current time
        
        Returns:
            EventConfig if event is active, None otherwise
        """
        for event in self.events:
            event_start = self._parse_start_time(event.start_time)
            event_end = event_start + timedelta(seconds=event.duration_seconds)
            
            # Check if event is active
            if event_start <= current_time <= event_end:
                # Check if format is affected
                if format_type in event.affected_formats:
                    # Check if event hasn't exceeded its limits
                    state = self.event_state[event.id]
                    format_key = f"{format_type}_logs_generated"
                    
                    config = getattr(event, f"{format_type}_config", None)
                    if config and config.get("total_logs"):
                        max_logs = config["total_logs"]
                        if state[format_key] >= max_logs:
                            continue  # Event limit reached for this format
                    
                    return event
        
        return None
    
    def should_generate_error(self, event: EventConfig, format_type: str) -> bool:
        """Determine if this log line should be an error for the event"""
        config = getattr(event, f"{format_type}_config", None)
        error_rate = config.get("error_rate", event.error_rate) if config else event.error_rate
        return random.random() < error_rate
    
    def get_error_code(self, event: EventConfig, format_type: str) -> int:
        """Get error code for event log"""
        config = getattr(event, f"{format_type}_config", None)
        error_codes = config.get("error_codes", event.error_codes) if config else event.error_codes
        return random.choice(error_codes)
    
    def record_log_generated(self, event_id: str, format_type: str):
        """Record that a log was generated for an event"""
        state = self.event_state[event_id]
        state[f"{format_type}_logs_generated"] += 1
    
    def _parse_start_time(self, start_time_str: str) -> datetime:
        """Parse start time string to datetime"""
        if start_time_str.startswith("+"):
            # Relative time (e.g., "+5m" = 5 minutes from start)
            minutes = int(start_time_str[1:-1])
            return self.start_time + timedelta(minutes=minutes)
        else:
            # Absolute time (e.g., "10:00:00")
            hour, minute, second = map(int, start_time_str.split(":"))
            today = self.start_time.date()
            return datetime.combine(today, datetime.min.time().replace(
                hour=hour, minute=minute, second=second
            ))


class EventAwareApacheGenerator:
    """Example Apache generator with event awareness"""
    
    def __init__(self, coordinator: EventCoordinator):
        self.coordinator = coordinator
    
    def generate_log_line(self, line_number: int, current_time: datetime) -> str:
        """Generate a single Apache log line, checking for events"""
        
        # Check for active event
        event = self.coordinator.get_active_event("apache", current_time)
        
        if event:
            # Generate event log
            ip = event.ip
            should_error = self.coordinator.should_generate_error(event, "apache")
            
            if should_error:
                status_code = self.coordinator.get_error_code(event, "apache")
            else:
                status_code = random.choice([200, 201, 204])  # Success codes
            
            # Record log generation
            self.coordinator.record_log_generated(event.id, "apache")
        else:
            # Normal generation
            ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
            status_code = random.choice([200, 201, 204, 301, 302, 400, 401, 403, 404, 429, 500, 502, 503])
        
        # Generate rest of log line (simplified)
        timestamp = current_time.strftime('%d/%b/%Y:%H:%M:%S %z')
        method = random.choice(["GET", "POST", "PUT", "DELETE"])
        path = random.choice(["/", "/index.html", "/api/items", "/login"])
        bytes_sent = random.randint(100, 90000)
        user_agent = f"Mozilla/{random.randint(1, 9)}.{random.randint(0, 9)}"
        response_time = f"{random.randint(0, 9)}.{random.randint(0, 999)}"
        upstream = random.choice(["checkout", "inventory", "payments"])
        
        log_line = f'{ip} - - [{timestamp}] "{method} {path} HTTP/1.1" {status_code} {bytes_sent} "-" "{user_agent}" {response_time} {upstream}'
        return log_line


class EventAwareNginxGenerator:
    """Example NGINX generator with event awareness"""
    
    def __init__(self, coordinator: EventCoordinator):
        self.coordinator = coordinator
    
    def generate_log_line(self, line_number: int, current_time: datetime) -> str:
        """Generate a single NGINX log line, checking for events"""
        
        # Check for active event
        event = self.coordinator.get_active_event("nginx", current_time)
        
        if event:
            # Generate event log
            ip = event.ip  # Same IP as Apache!
            should_error = self.coordinator.should_generate_error(event, "nginx")
            
            if should_error:
                status_code = self.coordinator.get_error_code(event, "nginx")
            else:
                status_code = random.choice([200, 201, 204])
            
            # Record log generation
            self.coordinator.record_log_generated(event.id, "nginx")
        else:
            # Normal generation
            ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
            status_code = random.choice([200, 201, 204, 301, 302, 304, 400, 401, 403, 404, 429, 500, 502, 503, 504])
        
        # Generate rest of log line (simplified)
        timestamp = current_time.strftime('%d/%b/%Y:%H:%M:%S %z')
        method = random.choice(["GET", "POST", "PUT", "DELETE"])
        path = random.choice(["/", "/api/v1/users", "/api/v1/orders", "/health"])
        bytes_sent = random.randint(100, 50000)
        referer = "-"
        user_agent = "Mozilla/5.0"
        response_time = f"0.{random.randint(0, 899):03d}"
        upstream = random.choice(["checkout", "inventory", "payments"])
        
        log_line = f'{ip} - - [{timestamp}] "{method} {path} HTTP/1.1" {status_code} {bytes_sent} "{referer}" "{user_agent}" rt={response_time} upstream={upstream}'
        return log_line


@dataclass
class NvidiaGpuMetrics:
    """Structured NVIDIA GPU metrics payload"""
    timestamp: str
    index: int
    name: str
    temperature_gpu: float
    utilization_gpu: int
    utilization_memory: int
    memory_total: int
    memory_used: int
    power_draw: float
    power_limit: float
    fan_speed: int


class NvidiaGpuMetricsGenerator:
    """Generate sample NVIDIA GPU metrics as nvidia-smi CSV log lines"""

    # Mirrors a common nvidia-smi query order
    CSV_FIELDS = [
        "timestamp",
        "index",
        "name",
        "temperature.gpu",
        "utilization.gpu",
        "utilization.memory",
        "memory.total",
        "memory.used",
        "power.draw",
        "power.limit",
        "fan.speed",
    ]

    def __init__(
        self,
        gpu_names: Optional[List[str]] = None,
        power_limits_watts: Optional[List[int]] = None,
        memory_totals_mb: Optional[List[int]] = None,
    ):
        self.gpu_names = gpu_names or ["NVIDIA RTX 4090"]
        self.power_limits_watts = power_limits_watts or [450]
        self.memory_totals_mb = memory_totals_mb or [24576]

    def generate_metrics(self, current_time: datetime, gpu_id: int = 0) -> NvidiaGpuMetrics:
        """Generate a metrics object for a single GPU"""
        name = self.gpu_names[gpu_id % len(self.gpu_names)]
        power_limit = self.power_limits_watts[gpu_id % len(self.power_limits_watts)]
        memory_total = self.memory_totals_mb[gpu_id % len(self.memory_totals_mb)]

        utilization = random.randint(0, 100)
        utilization_memory = int(min(100, max(0, utilization + random.randint(-15, 15))))

        base_power = 30.0  # idle baseline
        dynamic_power = (power_limit - base_power) * (utilization / 100.0)
        power_watts = max(0.0, min(power_limit, dynamic_power + base_power + random.uniform(-5, 5)))

        temperature_c = 30.0 + (utilization * 0.6) + random.uniform(-2, 4)
        temperature_c = max(25.0, min(95.0, temperature_c))

        memory_used = int(memory_total * (utilization / 110.0) + random.randint(0, 256))
        memory_used = max(0, min(memory_total, memory_used))

        fan_speed = int(min(100, max(20, utilization + random.randint(-10, 10))))

        return NvidiaGpuMetrics(
            timestamp=current_time.isoformat(),
            index=gpu_id,
            name=name,
            temperature_gpu=round(temperature_c, 1),
            utilization_gpu=utilization,
            utilization_memory=utilization_memory,
            memory_total=memory_total,
            memory_used=memory_used,
            power_draw=round(power_watts, 1),
            power_limit=float(power_limit),
            fan_speed=fan_speed,
        )

    def generate_csv_header(self) -> str:
        """Return the nvidia-smi --query-gpu header line"""
        return ", ".join(self.CSV_FIELDS)

    def generate_log_line(self, current_time: datetime, gpu_id: int = 0) -> str:
        """Generate a CSV log line similar to nvidia-smi --query-gpu"""
        metrics = self.generate_metrics(current_time, gpu_id)
        return (
            f"{metrics.timestamp}, "
            f"{metrics.index}, "
            f"{metrics.name}, "
            f"{metrics.temperature_gpu}, "
            f"{metrics.utilization_gpu}, "
            f"{metrics.utilization_memory}, "
            f"{metrics.memory_total}, "
            f"{metrics.memory_used}, "
            f"{metrics.power_draw}, "
            f"{metrics.power_limit}, "
            f"{metrics.fan_speed}"
        )


def load_event_config(config_file: str) -> List[EventConfig]:
    """Load event configuration from JSON file"""
    with open(config_file, 'r') as f:
        data = json.load(f)
    
    events = []
    for event_data in data.get("events", []):
        # Convert type string to EventType enum
        event_type = EventType(event_data["type"])
        
        # Create EventConfig
        event = EventConfig(
            id=event_data["id"],
            name=event_data["name"],
            type=event_type,
            start_time=event_data["start_time"],
            duration_seconds=event_data["duration_seconds"],
            ip=event_data["ip"],
            affected_formats=event_data["affected_formats"],
            apache_config=event_data.get("apache"),
            nginx_config=event_data.get("nginx"),
            error_rate=event_data.get("error_rate", 0.7),
            error_codes=event_data.get("error_codes", [403, 404, 500])
        )
        events.append(event)
    
    return events


def example_event_config() -> Dict:
    """Example event configuration"""
    return {
        "events": [
            {
                "id": "attack_001",
                "name": "Cross-Format Attack Pattern",
                "type": "cross_format_attack",
                "start_time": "+2m",  # 2 minutes after start
                "duration_seconds": 300,  # 5 minutes
                "ip": "192.168.1.100",
                "affected_formats": ["apache", "nginx"],
                "error_rate": 0.7,
                "error_codes": [403, 404, 500],
                "apache": {
                    "total_logs": 50,
                    "error_rate": 0.7,
                    "error_codes": [403, 404, 500]
                },
                "nginx": {
                    "total_logs": 40,
                    "error_rate": 0.7,
                    "error_codes": [403, 404, 500]
                }
            },
            {
                "id": "burst_001",
                "name": "Error Burst Pattern",
                "type": "error_burst",
                "start_time": "+10m",
                "duration_seconds": 30,
                "ip": "10.0.0.50",
                "affected_formats": ["apache"],
                "error_rate": 0.9,
                "error_codes": [500, 502, 503],
                "apache": {
                    "total_logs": 50,
                    "error_rate": 0.9
                }
            }
        ]
    }


def example_usage():
    """Example of how to use event generation"""
    
    # Create example event config
    config = example_event_config()
    
    # Save to file (for demonstration)
    with open("example_events.json", "w") as f:
        json.dump(config, f, indent=2)
    
    # Load events
    events = load_event_config("example_events.json")
    
    # Initialize coordinator
    start_time = datetime.now()
    coordinator = EventCoordinator(events, start_time)
    
    # Create generators
    apache_gen = EventAwareApacheGenerator(coordinator)
    nginx_gen = EventAwareNginxGenerator(coordinator)
    
    print("Event Generation Example")
    print("=" * 50)
    print(f"Start time: {start_time}")
    print(f"Events configured: {len(events)}")
    print("\nEvents:")
    for event in events:
        print(f"  - {event.name} ({event.id})")
        print(f"    IP: {event.ip}")
        print(f"    Start: {event.start_time}, Duration: {event.duration_seconds}s")
        print(f"    Formats: {', '.join(event.affected_formats)}")
    
    print("\n" + "=" * 50)
    print("Generating sample logs...")
    print("\nSample Apache logs (with events):")
    
    # Generate some sample logs
    current_time = start_time
    for i in range(10):
        log_line = apache_gen.generate_log_line(i, current_time)
        print(f"  {log_line[:100]}...")
        current_time += timedelta(seconds=1)
    
    print("\nSample NGINX logs (with events):")
    current_time = start_time
    for i in range(10):
        log_line = nginx_gen.generate_log_line(i, current_time)
        print(f"  {log_line[:100]}...")
        current_time += timedelta(seconds=1)
    
    print("\nSample NVIDIA GPU metrics logs (nvidia-smi CSV):")
    gpu_gen = NvidiaGpuMetricsGenerator(
        gpu_names=["NVIDIA RTX 4090", "NVIDIA A100"],
        power_limits_watts=[450, 400],
        memory_totals_mb=[24576, 40960],
    )
    print(f"  {gpu_gen.generate_csv_header()}")
    current_time = start_time
    for i in range(5):
        log_line = gpu_gen.generate_log_line(current_time, gpu_id=i % 2)
        print(f"  {log_line}")
        current_time += timedelta(seconds=1)

    print("\n" + "=" * 50)
    print("Event state:")
    for event_id, state in coordinator.event_state.items():
        print(f"  {event_id}:")
        print(f"    Apache logs: {state['apache_logs_generated']}")
        print(f"    NGINX logs: {state['nginx_logs_generated']}")


if __name__ == "__main__":
    example_usage()


