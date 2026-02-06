# Event Generation Strategies for Elastic Observability

This document explores how to generate logs with intentional patterns, anomalies, and events that can be detected by Elastic Observability (Elasticsearch, Kibana, etc.).

## Goal

Generate synthetic log data that contains **detectable patterns** such as:
- Same IP generating many errors across Apache and NGINX
- Burst patterns (sudden spikes in errors)
- Correlated events across multiple log formats
- Anomalies that stand out from normal traffic
- Attack patterns (brute force, scanning, etc.)

## Current State

Currently, log generators create **random** data:
- Random IPs for each log line
- Random status codes
- No correlation between Apache and NGINX logs
- No intentional patterns or events

## Event Generation Approaches

### Approach 1: Event Profiles / Scenarios

**Concept**: Define "event scenarios" that inject patterns into normal log generation.

**Structure**:
```python
event_scenarios = {
    "attack_pattern": {
        "ip": "192.168.1.100",
        "error_rate": 0.8,  # 80% errors
        "error_codes": [403, 404, 500],
        "duration_seconds": 300,
        "affected_formats": ["apache", "nginx"],
        "requests_per_second": 10
    },
    "burst_pattern": {
        "ip": "10.0.0.50",
        "burst_size": 50,
        "burst_duration": 30,
        "error_rate": 0.9
    }
}
```

**How it works**:
- During log generation, check if we're in an "event window"
- If yes, use event parameters instead of random values
- Generate logs matching the event pattern
- Return to normal random generation after event

---

### Approach 2: Coordinated Generation

**Concept**: Coordinate between Apache and NGINX generators to create correlated events.

**Structure**:
```python
class EventCoordinator:
    """Coordinates events across multiple log generators"""
    
    def __init__(self):
        self.active_events = []
        self.shared_state = {}  # Shared IPs, timestamps, etc.
    
    def register_event(self, event_config):
        # Schedule an event
        pass
    
    def get_ip_for_event(self, event_id):
        # Return IP associated with event
        pass
    
    def should_generate_error(self, format_type, event_id):
        # Determine if this log should be an error for this event
        pass
```

**How it works**:
- Single coordinator shared across generators
- Generators check coordinator before generating each line
- Coordinator provides: IP, status code, timing for events
- Ensures Apache and NGINX logs show same IP with errors

---

### Approach 3: Event Injection Points

**Concept**: Inject event logs at specific points during normal generation.

**Structure**:
```python
class ApacheLogGenerator(BaseLogGenerator):
    def generate(self):
        normal_lines = self.lines - event_lines
        
        # Generate normal logs
        for i in range(normal_lines):
            self._generate_normal_log()
        
        # Inject event logs
        self._inject_event_logs(event_lines)
        
        # Continue normal logs
        for i in range(remaining_lines):
            self._generate_normal_log()
```

**How it works**:
- Generate mostly normal logs
- At specific intervals, inject event pattern logs
- Event logs use consistent IPs, error codes, timestamps
- Creates detectable patterns within normal traffic

---

### Approach 4: Time-Based Event Windows

**Concept**: Define time windows where events occur, with specific characteristics.

**Structure**:
```python
event_schedule = [
    {
        "start_time": "10:00:00",
        "end_time": "10:05:00",
        "type": "cross_format_attack",
        "ip": "203.0.113.42",
        "apache_errors": 25,
        "nginx_errors": 20,
        "error_codes": [403, 404, 500]
    }
]
```

**How it works**:
- Check current time during generation
- If within event window, generate event logs
- Outside window, generate normal logs
- Creates realistic time-based patterns

---

## Specific Event Types to Generate

### 1. Cross-Format Attack Pattern

**Pattern**: Same IP generates errors in both Apache and NGINX within a time window.

**Implementation**:
```python
# Shared event state
attack_ip = "192.168.1.100"
error_codes = [403, 404, 500]
event_start = datetime.now()
event_duration = timedelta(minutes=5)

# In Apache generator:
if datetime.now() < event_start + event_duration:
    if random.random() < 0.7:  # 70% chance of error
        ip = attack_ip
        status_code = random.choice(error_codes)
    else:
        # Normal generation
        ip = random_ip()
        status_code = random_status()

# In NGINX generator (same logic):
if datetime.now() < event_start + event_duration:
    if random.random() < 0.7:
        ip = attack_ip  # Same IP!
        status_code = random.choice(error_codes)
```

**Elastic Detection**: Query for IPs with errors in both Apache and NGINX logs within time window.

---

### 2. Error Burst Pattern

**Pattern**: Sudden spike in errors from specific IPs.

**Implementation**:
```python
# Generate normal traffic
for i in range(normal_lines):
    generate_normal_log()

# Burst event
burst_ip = "10.0.0.50"
burst_size = 50
for i in range(burst_size):
    ip = burst_ip
    status_code = random.choice([500, 502, 503])  # Server errors
    generate_log(ip, status_code)
    time.sleep(0.1)  # Rapid generation

# Return to normal
for i in range(remaining_lines):
    generate_normal_log()
```

**Elastic Detection**: Detect sudden spikes in error rate by IP or overall.

---

### 3. Scanning Pattern

**Pattern**: IP tries many different paths, generating 404s.

**Implementation**:
```python
scanner_ip = "198.51.100.25"
scan_paths = [
    "/admin", "/wp-admin", "/phpmyadmin", "/.env",
    "/api/users", "/api/admin", "/config", "/backup"
]

for path in scan_paths:
    ip = scanner_ip
    status_code = 404  # Not found
    method = "GET"
    generate_log(ip, method, path, status_code)
```

**Elastic Detection**: Detect IPs with high 404 rate across many unique paths.

---

### 4. Brute Force Pattern

**Pattern**: Same IP repeatedly hitting login endpoint with 401/403.

**Implementation**:
```python
attacker_ip = "203.0.113.10"
login_path = "/login"

for i in range(20):  # 20 failed attempts
    ip = attacker_ip
    path = login_path
    status_code = random.choice([401, 403])  # Unauthorized/Forbidden
    method = "POST"
    generate_log(ip, method, path, status_code)
    time.sleep(random.uniform(1, 3))  # Realistic timing
```

**Elastic Detection**: Detect repeated 401/403 from same IP on auth endpoints.

---

### 5. Service Degradation Pattern

**Pattern**: Gradual increase in 5xx errors, then recovery.

**Implementation**:
```python
# Phase 1: Normal (0-2% errors)
# Phase 2: Degrading (10-20% errors)
# Phase 3: Critical (50-70% errors)
# Phase 4: Recovery (back to normal)

degradation_ips = ["10.0.0.1", "10.0.0.2", "10.0.0.3"]

for phase in ["normal", "degrading", "critical", "recovery"]:
    error_rate = {
        "normal": 0.02,
        "degrading": 0.15,
        "critical": 0.60,
        "recovery": 0.05
    }[phase]
    
    for i in range(lines_per_phase):
        if random.random() < error_rate:
            ip = random.choice(degradation_ips)
            status_code = random.choice([500, 502, 503])
        else:
            ip = random_ip()
            status_code = 200
        generate_log(ip, status_code)
```

**Elastic Detection**: Time-series analysis showing error rate trends.

---

### 6. Geographic Anomaly Pattern

**Pattern**: Unusual traffic from specific geographic region.

**Implementation**:
```python
# Use specific IP ranges for "suspicious" region
suspicious_ip_range = "203.0.113"  # Example: specific country/region

for i in range(anomaly_lines):
    ip = f"{suspicious_ip_range}.{random.randint(1, 255)}"
    # Higher error rate from this region
    if random.random() < 0.4:
        status_code = random.choice([403, 404, 429])
    else:
        status_code = 200
    generate_log(ip, status_code)
```

**Elastic Detection**: GeoIP analysis showing unusual patterns from specific regions.

---

## Implementation Strategies

### Strategy A: Event Configuration File

Create a JSON/YAML config file defining events:

```json
{
  "events": [
    {
      "id": "attack_001",
      "type": "cross_format_attack",
      "start_time": "10:00:00",
      "duration_seconds": 300,
      "ip": "192.168.1.100",
      "apache": {
        "error_count": 25,
        "error_codes": [403, 404, 500],
        "error_rate": 0.7
      },
      "nginx": {
        "error_count": 20,
        "error_codes": [403, 404, 500],
        "error_rate": 0.7
      }
    }
  ]
}
```

**Pros**: Easy to configure, reusable, testable
**Cons**: Requires parsing config, more complex

---

### Strategy B: Event Generator Class

Create a separate class that generates event logs:

```python
class EventGenerator:
    def generate_cross_format_attack(self, ip, duration, apache_gen, nginx_gen):
        # Generate Apache attack logs
        # Generate NGINX attack logs
        # Ensure same IP, overlapping timestamps
        pass
```

**Pros**: Clean separation, reusable
**Cons**: Requires coordination between generators

---

### Strategy C: Modified Generators with Event Mode

Add event generation mode to existing generators:

```python
class ApacheLogGenerator(BaseLogGenerator):
    def __init__(self, ..., event_config=None):
        self.event_config = event_config
    
    def generate(self):
        if self.event_config:
            self._generate_with_events()
        else:
            self._generate_normal()
    
    def _generate_with_events(self):
        # Check if current time is in event window
        # Generate event logs or normal logs accordingly
        pass
```

**Pros**: Minimal changes to existing code
**Cons**: Each generator needs event logic

---

### Strategy D: Event Injector (Post-Processing)

Generate normal logs, then inject event logs:

```python
# Step 1: Generate normal logs
generate_logs()

# Step 2: Inject event logs into files
inject_events("loadgen_apache.log", event_config)
inject_events("loadgen_nginx.log", event_config)
```

**Pros**: Simple, doesn't affect generation logic
**Cons**: Less realistic timing, requires file manipulation

---

## Recommended Approach: Hybrid with Event Coordinator

Combine multiple strategies:

1. **Event Coordinator**: Central class managing event state
2. **Event Configuration**: JSON/YAML file defining events
3. **Modified Generators**: Check coordinator before generating each line
4. **Time-Based**: Events scheduled at specific times

### Architecture:

```
EventConfig (JSON)
    ↓
EventCoordinator (manages state)
    ↓
ApacheGenerator ──┐
                  ├── Check coordinator
NGINXGenerator ──┘
    ↓
Generate logs with events embedded
```

### Example Flow:

1. Load event configuration
2. Initialize EventCoordinator with events
3. Pass coordinator to generators
4. During generation:
   - Generator checks: "Is there an active event?"
   - If yes: Use event IP, error codes, timing
   - If no: Generate normal random log
5. Coordinator tracks event state (start/end times, IPs, etc.)

---

## Event Configuration Schema

```python
{
    "events": [
        {
            "id": "unique_event_id",
            "name": "Cross-Format Attack",
            "type": "cross_format_attack",  # or "burst", "scanning", etc.
            "start_time": "10:00:00",  # HH:MM:SS or relative "+5m"
            "duration_seconds": 300,
            "ip": "192.168.1.100",
            "affected_formats": ["apache", "nginx"],
            "apache": {
                "total_logs": 50,
                "error_rate": 0.7,
                "error_codes": [403, 404, 500],
                "paths": ["/admin", "/api/users", "/login"]
            },
            "nginx": {
                "total_logs": 40,
                "error_rate": 0.7,
                "error_codes": [403, 404, 500],
                "paths": ["/api/v1/users", "/admin"]
            }
        },
        {
            "id": "burst_001",
            "type": "error_burst",
            "start_time": "+10m",  # 10 minutes after start
            "duration_seconds": 30,
            "ip": "10.0.0.50",
            "burst_size": 50,
            "error_codes": [500, 502, 503],
            "affected_formats": ["apache"]
        }
    ]
}
```

---

## Elastic Observability Detection Queries

Once events are generated, here are example queries to detect them:

### Cross-Format Attack Detection:
```kql
# Kibana Query Language
(client.ip: "192.168.1.100") AND 
(http.response.status_code >= 400) AND 
(
  (log.file.path: "*apache*") OR 
  (log.file.path: "*nginx*")
)
```

### Error Burst Detection:
```kql
# Detect IPs with sudden spike in errors
http.response.status_code >= 500
| stats count() by client.ip, span(@timestamp, 1m)
| where count() > 20
```

### Scanning Pattern Detection:
```kql
# IPs with many 404s on different paths
http.response.status_code: 404
| stats dc(url.path) as unique_paths, count() as total_404s by client.ip
| where unique_paths > 10 AND total_404s > 20
```

---

## Implementation Considerations

### 1. Timing Synchronization
- Ensure Apache and NGINX events overlap in time
- Use shared timestamps or coordinator for sync
- Consider timezone handling

### 2. Realistic Patterns
- Don't make events too obvious (100% errors)
- Mix normal and event logs
- Use realistic timing (not instant bursts)

### 3. Event Density
- Control how many events vs normal logs
- Avoid too many events (unrealistic)
- Make events rare enough to be interesting

### 4. Configurability
- Make events optional (flag to enable/disable)
- Allow customizing event parameters
- Support multiple concurrent events

### 5. Testing
- Verify events are generated correctly
- Test that Elastic can detect them
- Ensure events don't break log parsing

---

## Next Steps

1. **Choose implementation strategy** (recommended: Event Coordinator)
2. **Define event configuration format** (JSON schema)
3. **Implement EventCoordinator class**
4. **Modify generators** to check coordinator
5. **Create example event configs** for common patterns
6. **Test with Elastic Observability** to verify detection

Would you like me to create a specific implementation example for any of these approaches?


