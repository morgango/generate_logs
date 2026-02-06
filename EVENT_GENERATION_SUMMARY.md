# Event Generation Summary

## Overview

This document summarizes the approach for generating logs with intentional patterns/events that can be detected by Elastic Observability.

## Key Concept

Instead of detecting events in logs, we **generate logs with events embedded** so that Elastic Observability can detect them.

## Files Created

### 1. `EVENT_GENERATION_STRATEGIES.md`
Comprehensive guide covering:
- Different approaches to event generation
- Specific event types (cross-format attacks, bursts, scanning, etc.)
- Implementation strategies
- Event configuration schemas
- Elastic detection queries

### 2. `event_generation_example.py`
Working example implementation showing:
- `EventCoordinator` class for managing events
- `EventAwareApacheGenerator` and `EventAwareNginxGenerator` examples
- Event configuration loading
- How generators check for active events

### 3. `example_events.json`
Example event configuration file with:
- Cross-format attack pattern
- Error burst pattern
- Scanning pattern
- Brute force pattern
- Service degradation pattern

## How It Works

### Architecture Flow

```
Event Config (JSON)
    ↓
Event Coordinator (manages state)
    ↓
Apache Generator ──┐
                   ├── Check coordinator → Generate event or normal log
NGINX Generator ──┘
    ↓
Log Files with Events Embedded
    ↓
Elastic Observability (detects patterns)
```

### Key Components

1. **Event Configuration**: JSON file defining what events to generate
2. **Event Coordinator**: Central class that tracks active events and provides state to generators
3. **Modified Generators**: Generators check coordinator before each log line to determine if event is active

### Example Event: Cross-Format Attack

**Configuration**:
```json
{
  "id": "attack_001",
  "type": "cross_format_attack",
  "start_time": "+2m",
  "duration_seconds": 300,
  "ip": "192.168.1.100",
  "affected_formats": ["apache", "nginx"],
  "apache": {"error_rate": 0.7, "error_codes": [403, 404, 500]},
  "nginx": {"error_rate": 0.7, "error_codes": [403, 404, 500]}
}
```

**What Happens**:
1. At 2 minutes after start, event becomes active
2. Apache generator checks coordinator → event active → use IP `192.168.1.100`, 70% chance of error
3. NGINX generator checks coordinator → event active → use same IP `192.168.1.100`, 70% chance of error
4. Both generate logs with same IP and errors for 5 minutes
5. Elastic can detect: same IP with errors in both formats within time window

## Event Types Supported

1. **Cross-Format Attack**: Same IP generates errors in Apache AND NGINX
2. **Error Burst**: Sudden spike in errors from specific IP
3. **Scanning Pattern**: IP tries many paths, generating 404s
4. **Brute Force**: Repeated login attempts with 401/403
5. **Service Degradation**: Gradual increase in 5xx errors

## Integration Points

To integrate event generation into existing code:

1. **Add Event Coordinator** to `generate_logs.py`
   - Load event config from file
   - Initialize coordinator
   - Pass to generators

2. **Modify Generators** in `log_generators.py`
   - Add coordinator parameter
   - Check coordinator before generating each line
   - Use event IP/status if event active, else random

3. **Event Configuration File**
   - Create JSON config file
   - Define events with timing, IPs, error rates
   - Make configurable via CLI flag

## Elastic Detection Queries

Once events are generated, use these queries in Kibana:

### Cross-Format Attack:
```kql
(client.ip: "192.168.1.100") AND 
(http.response.status_code >= 400) AND 
((log.file.path: "*apache*") OR (log.file.path: "*nginx*"))
```

### Error Burst:
```kql
http.response.status_code >= 500
| stats count() by client.ip, span(@timestamp, 1m)
| where count() > 20
```

### Scanning Pattern:
```kql
http.response.status_code: 404
| stats dc(url.path) as unique_paths, count() as total_404s by client.ip
| where unique_paths > 10 AND total_404s > 20
```

## Next Steps

1. **Review** `EVENT_GENERATION_STRATEGIES.md` for detailed approaches
2. **Examine** `event_generation_example.py` for implementation details
3. **Customize** `example_events.json` with your desired patterns
4. **Integrate** event generation into existing generators (if desired)
5. **Test** with Elastic Observability to verify detection

## Benefits

- ✅ Generate realistic attack/anomaly patterns
- ✅ Test Elastic detection capabilities
- ✅ Create training data for security teams
- ✅ Validate monitoring and alerting rules
- ✅ Demonstrate observability platform features

## Notes

- Events are optional - can be enabled/disabled
- Events mix with normal traffic (realistic)
- Timing is coordinated across formats
- Configurable via JSON (no code changes needed for new events)


