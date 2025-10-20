# Elasticsearch Log Filtering Guide

This guide shows how to filter and distinguish between different log formats in Elasticsearch.

## Log Format Identifiers

Each log format has a clear identifier:

- **Apache**: `fmt=apache` prefix
- **Hadoop**: `fmt=hadoop` prefix  
- **JSON**: `"fmt": "json"` field in JSON structure
- **CSV**: `fmt=csv` prefix
- **Pipe**: `fmt=pipe` prefix
- **KV**: `fmt=kv` prefix

## Elasticsearch Queries

### 1. Filter by Log Type (Prefix Method)

```json
# Apache logs only
GET /your-index/_search
{
  "query": {
    "match": {
      "message": "fmt=apache"
    }
  }
}

# Hadoop logs only
GET /your-index/_search
{
  "query": {
    "match": {
      "message": "fmt=hadoop"
    }
  }
}

# JSON logs only
GET /your-index/_search
{
  "query": {
    "match": {
      "message": "fmt=json"
    }
  }
}
```

### 2. Filter by JSON Field (Most Precise)

```json
# JSON logs using fmt field
GET /your-index/_search
{
  "query": {
    "term": {
      "fmt": "json"
    }
  }
}
```

### 3. Pattern-Based Filtering

```json
# Apache HTTP logs
GET /your-index/_search
{
  "query": {
    "regexp": {
      "message": "fmt=apache.*HTTP/1\\.1"
    }
  }
}

# Hadoop job/task logs
GET /your-index/_search
{
  "query": {
    "regexp": {
      "message": "fmt=hadoop.*job_.*task_"
    }
  }
}
```

### 4. Aggregation by Log Type

```json
GET /your-index/_search
{
  "size": 0,
  "aggs": {
    "log_types": {
      "terms": {
        "script": {
          "source": """
            if (doc['message'].value.startsWith('fmt=apache')) return 'Apache';
            if (doc['message'].value.startsWith('fmt=hadoop')) return 'Hadoop';
            if (doc['message'].value.startsWith('fmt=json')) return 'JSON';
            if (doc['message'].value.startsWith('fmt=csv')) return 'CSV';
            if (doc['message'].value.startsWith('fmt=pipe')) return 'Pipe';
            if (doc['message'].value.startsWith('fmt=kv')) return 'KV';
            return 'Other';
          """
        }
      }
    }
  }
}
```

### 5. Kibana Discover Filters

In Kibana Discover, you can use these filters:

- **Apache logs**: `message: "fmt=apache"`
- **Hadoop logs**: `message: "fmt=hadoop"`
- **JSON logs**: `fmt: "json"`
- **CSV logs**: `message: "fmt=csv"`
- **Pipe logs**: `message: "fmt=pipe"`
- **KV logs**: `message: "fmt=kv"`

### 6. Time-Based Filtering

```json
# Apache logs from last hour
GET /your-index/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "message": "fmt=apache"
          }
        },
        {
          "range": {
            "@timestamp": {
              "gte": "now-1h"
            }
          }
        }
      ]
    }
  }
}
```

### 7. Service-Specific Filtering

```json
# Apache logs for specific upstream service
GET /your-index/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "message": "fmt=apache"
          }
        },
        {
          "match": {
            "message": "upstream=checkout"
          }
        }
      ]
    }
  }
}
```

## Logstash Configuration

If using Logstash, you can parse the format identifiers:

```ruby
filter {
  if [message] =~ /^fmt=apache/ {
    mutate {
      add_field => { "log_format" => "apache" }
      gsub => [ "message", "^fmt=apache ", "" ]
    }
  }
  
  if [message] =~ /^fmt=hadoop/ {
    mutate {
      add_field => { "log_format" => "hadoop" }
      gsub => [ "message", "^fmt=hadoop ", "" ]
    }
  }
  
  if [message] =~ /^fmt=json/ {
    mutate {
      add_field => { "log_format" => "json" }
      gsub => [ "message", "^fmt=json ", "" ]
    }
  }
}
```

## Example Log Output

### Apache Logs
```
fmt=apache 192.168.1.100 - - [20/Oct/2025:12:14:04 ] "GET /api/orders HTTP/1.1" 200 1024 "-" "Mozilla/5.0" rt=0.123 upstream=checkout
```

### Hadoop Logs
```
fmt=hadoop 2025-10-20T17:14:04.960474+00:00 ERROR DataNode: hadoop-8.cluster.local job_418830_7167 task_725733_3214_5 memory=7329MB cpu=56% duration=21042ms Inventory sync service unavailable
```

### JSON Logs
```json
{"fmt": "json", "ts": "2025-10-20T17:14:04.959643+00:00", "level": "CRITICAL", "service": "inventory", "user": "u8744", "duration_ms": 4676, "msg": "Critical stock data corruption detected"}
```

## Testing Commands

Generate test logs with different formats:

```bash
# Generate all formats
python3 generate_logs.py --format all --lines 100

# Generate only Apache logs
python3 generate_logs.py --format apache --lines 50

# Generate only Hadoop logs  
python3 generate_logs.py --format hadoop --lines 50

# Generate with duration for continuous testing
python3 generate_logs.py --format all --lines 10 --duration 60
```
