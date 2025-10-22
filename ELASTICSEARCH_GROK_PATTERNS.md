# Elasticsearch Grok Patterns for Direct ECS Field Extraction

This document provides Grok patterns that extract fields directly to Elastic Common Schema (ECS) field names, eliminating the need for field mapping.

## Format Overview

| Format | Identifier | Grok Pattern | Direct ECS Fields |
|--------|------------|--------------|-------------------|
| Apache | `fmt=apache` | Apache HTTP Access | `@timestamp`, `client.ip`, `http.request.method`, `http.response.status_code` |
| CSV | `fmt=csv` | Comma-delimited | `@timestamp`, `log.level`, `service.name` |
| PIPE | `fmt=pipe` | Pipe-delimited + key=value | `@timestamp`, `log.level`, `service.name`, `transaction.id` |
| KV | `fmt=kv` | Key=value pairs | `@timestamp`, `log.level`, `service.name`, `http.request.id` |
| Hadoop | `fmt=hadoop` | Space-delimited system logs | `@timestamp`, `log.level`, `host.name`, `process.name` |
| Logstash | `fmt=logstash` | Semi-colon delimited | `@timestamp`, `log.level`, `service.name`, `user.id` |
| NGINX | `fmt=nginx` | HTTP Access (NGINX) | `@timestamp`, `client.ip`, `http.request.method`, `http.response.status_code` |
| Tomcat | `fmt=tomcat` | Java Application | `@timestamp`, `log.level`, `process.name`, `log.origin.thread` |
| MySQL | `fmt=mysql` | Database Query | `@timestamp`, `user.name`, `database.name`, `db.query` |
| Redis | `fmt=redis` | Cache/Database | `@timestamp`, `log.level`, `process.pid`, `service.role` |

## Direct ECS Grok Patterns

### 1. Apache HTTP Access Logs
```
fmt=%{WORD:custom.type} %{IPV4:source.ip}\s-\s-\s\[(?<custom.timestamp>%{MONTHDAY}/%{MONTH}/%{YEAR}:%{HOUR}:%{MINUTE}:%{SECOND}) \]\s"%{WORD:http.request.method} %{NOTSPACE:url.path} %{DATA:http.version}"\s%{INT:http.response.status_code}\s%{INT:http.response.body.bytes}\s"-"\s"(?<user_agent.original>%{DATA}/%{INT}\.%{INT})"\s(?<custom.response_time>%{DATA}\.%{INT})\s%{GREEDYDATA:custom.upstream}
```


**Direct ECS Field Extraction:**
- Fields are extracted directly to ECS field names
- `custom.type` will be converted to uppercase

### 2. CSV Format
```
fmt=%{WORD:custom.type} %{TIMESTAMP_ISO8601:@timestamp},%{WORD:log.level},%{DATA:service.name},%{DATA:user.id},%{NUMBER:event.duration:int},%{NUMBER:http.response.status_code:int},%{GREEDYDATA:custom.message}

```

**Direct ECS Field Extraction:**
- Fields are extracted directly to ECS field names
- `custom.type` will be converted to uppercase

### 3. PIPE Format
```
fmt=%{WORD:custom.type} %{TIMESTAMP_ISO8601:@timestamp}\|%{WORD:log.level}\|%{DATA:service.name}\|txn=%{DATA:transaction.id}\|amount=%{NUMBER:transaction.amount:float}\|country=%{WORD:client.geo.country_iso_code}\|session=%{DATA:session.id}
```

**Direct ECS Field Extraction:**
- Fields are extracted directly to ECS field names
- `custom.type` will be converted to uppercase

### 4. KV Format
```
fmt=%{WORD:custom.type} ts=%{TIMESTAMP_ISO8601:@timestamp} level=%{WORD:log.level} service=%{DATA:service.name} req=%{DATA:http.request.id} duration_ms=%{NUMBER:event.duration_ms:int} msg=%{GREEDYDATA:custom.message}
```

**Direct ECS Field Extraction:**
- Fields are extracted directly to ECS field names
- `custom.type` will be converted to uppercase

### 5. Hadoop Format
```
fmt=%{WORD:custom.type} %{TIMESTAMP_ISO8601:@timestamp} %{WORD:log.level} %{DATA:service.name}: %{HOSTNAME:host.name} %{DATA:hadoop.job.id} %{DATA:hadoop.task.id} memory=%{NUMBER:hadoop.task.memory_mb} cpu=%{NUMBER:hadoop.task.cpu_pct} duration=%{NUMBER:event.duration_ms:int} %{GREEDYDATA:custom.message}
```

**Direct ECS Field Extraction:**
- Fields are extracted directly to ECS field names
- `custom.type` will be converted to uppercase

### 6. Logstash Format
```
fmt=%{WORD:custom.type} @timestamp=%{TIMESTAMP_ISO8601:@timestamp}; level=%{WORD:log.level}; service=%{DATA:service.name}; request_id=%{DATA:http.request.id}; session_id=%{DATA:session.id}; user_id=%{DATA:user.id}; duration_ms=%{NUMBER:event.duration:int}; status_code=%{NUMBER:http.response.status_code:int}; ip=%{IPORHOST:client.ip}; user_agent=%{DATA:user_agent.original}; message=%{GREEDYDATA:custom.message}
```

**Direct ECS Field Extraction:**
- Fields are extracted directly to ECS field names
- `custom.type` will be converted to uppercase

### 7. NGINX Format
```
fmt=%{WORD:custom.type} %{IPORHOST:client.ip} %{DATA:ident} %{DATA:auth} \[%{HTTPDATE:@timestamp}\] "%{WORD:http.request.method} %{DATA:http.request.uri.original} %{DATA:http.version}" %{NUMBER:http.response.status_code:int} %{NUMBER:http.response.bytes:int} "%{DATA:http.request.referrer}" "%{DATA:user_agent.original}" rt=%{NUMBER:event.duration:float} upstream=%{DATA:service.name}
```

**Direct ECS Field Extraction:**
- Fields are extracted directly to ECS field names
- `custom.type` will be converted to uppercase

### 8. Tomcat Format
```
fmt=%{WORD:custom.type} %{TIMESTAMP_ISO8601:@timestamp} %{WORD:log.level} %{DATA:process.name} %{DATA:log.origin.thread} %{GREEDYDATA:custom.message}
```

**Direct ECS Field Extraction:**
- Fields are extracted directly to ECS field names
- `custom.type` will be converted to uppercase

### 9. MySQL Format
```
fmt=%{WORD:custom.type} %{TIMESTAMP_ISO8601:@timestamp} %{DATA:user.name}\[%{DATA:user.name}\] @ %{IPORHOST:host.ip} \[%{TIMESTAMP_ISO8601:query_timestamp}\] %{NUMBER:event.duration:float} %{NUMBER:lock_time:float} %{NUMBER:db.rows_sent:int} %{NUMBER:db.rows_examined:int} %{DATA:database.name} %{GREEDYDATA:db.query}
```

**Direct ECS Field Extraction:**
- Fields are extracted directly to ECS field names
- `custom.type` will be converted to uppercase

### 10. Redis Format
```
fmt=%{WORD:custom.type} %{TIMESTAMP_ISO8601:@timestamp} %{WORD:log.level} %{NUMBER:process.pid:int}:%{DATA:process_type} %{DATA:service.role} %{GREEDYDATA:custom.message}
```

**Direct ECS Field Extraction:**
- Fields are extracted directly to ECS field names
- `custom.type` will be converted to uppercase

## Simplified Logstash Configuration

```ruby
filter {
  # Apache/NGINX HTTP Access Logs
  if [message] =~ /^fmt=(apache|nginx)/ {
    grok {
      match => { 
        "message" => "fmt=%{WORD:custom.type} %{IPV4:source.ip}\\s-\\s-\\s\\[(?<custom.timestamp>%{MONTHDAY}/%{MONTH}/%{YEAR}:%{HOUR}:%{MINUTE}:%{SECOND}) \\]\\s\"%{WORD:http.request.method} %{NOTSPACE:url.path} %{DATA:http.version}\"\\s%{INT:http.response.status_code}\\s%{INT:http.response.body.bytes}\\s\"-\"\\s\"(?<user_agent.original>%{DATA}/%{INT}\\.%{INT})\"\\s(?<custom.response_time>%{DATA}\\.%{INT})\\s%{GREEDYDATA:custom.upstream}"
      }
    }
    
    mutate {
      uppercase => { "custom.type" => "custom.type" }
    }
  }
  
  # CSV Format
  if [message] =~ /^fmt=csv/ {
    grok {
      match => { 
        "message" => "fmt=%{WORD:custom.type} %{TIMESTAMP_ISO8601:@timestamp},%{WORD:log.level},%{DATA:service.name},%{DATA:user.id},%{NUMBER:event.duration:int},%{NUMBER:http.response.status_code:int},%{GREEDYDATA:custom.message}"
      }
    }
    
    mutate {
      uppercase => { "custom.type" => "custom.type" }
    }
  }
  
  # PIPE Format
  if [message] =~ /^fmt=pipe/ {
    grok {
      match => { 
        "message" => "fmt=%{WORD:custom.type} %{TIMESTAMP_ISO8601:@timestamp}\|%{WORD:log.level}\|%{DATA:service.name}\|txn=%{DATA:transaction.id}\|amount=%{NUMBER:transaction.amount:float}\|country=%{WORD:client.geo.country_iso_code}\|session=%{DATA:session.id}"
      }
    }
    
    mutate {
      uppercase => { "custom.type" => "custom.type" }
    }
  }
  
  # KV Format
  if [message] =~ /^fmt=kv/ {
    grok {
      match => { 
        "message" => "fmt=%{WORD:custom.type} ts=%{TIMESTAMP_ISO8601:@timestamp} level=%{WORD:log.level} service=%{DATA:service.name} req=%{DATA:http.request.id} duration_ms=%{NUMBER:event.duration:int} msg=%{GREEDYDATA:custom.message}"
      }
    }
    
    mutate {
      uppercase => { "custom.type" => "custom.type" }
    }
  }
  
  # Hadoop Format
  if [message] =~ /^fmt=hadoop/ {
    grok {
      match => { 
        "message" => "fmt=%{WORD:custom.type} %{TIMESTAMP_ISO8601:@timestamp} %{WORD:log.level} %{DATA:process.name}: %{DATA:host.name} %{DATA:process.args} %{DATA:process.args} memory=%{NUMBER:system.memory.total:int} cpu=%{NUMBER:system.cpu.total.pct:int} duration=%{NUMBER:event.duration:int} %{GREEDYDATA:custom.message}"
      }
    }
    
    mutate {
      uppercase => { "custom.type" => "custom.type" }
    }
  }
  
  # Logstash Format
  if [message] =~ /^fmt=logstash/ {
    grok {
      match => { 
        "message" => "fmt=%{WORD:custom.type} @timestamp=%{TIMESTAMP_ISO8601:@timestamp}; level=%{WORD:log.level}; service=%{DATA:service.name}; request_id=%{DATA:http.request.id}; session_id=%{DATA:session.id}; user_id=%{DATA:user.id}; duration_ms=%{NUMBER:event.duration:int}; status_code=%{NUMBER:http.response.status_code:int}; ip=%{IPORHOST:client.ip}; user_agent=%{DATA:user_agent.original}; message=%{GREEDYDATA:custom.message}"
      }
    }
    
    mutate {
      uppercase => { "custom.type" => "custom.type" }
    }
  }
  
  # Tomcat Format
  if [message] =~ /^fmt=tomcat/ {
    grok {
      match => { 
        "message" => "fmt=%{WORD:custom.type} %{TIMESTAMP_ISO8601:@timestamp} %{WORD:log.level} %{DATA:process.name} %{DATA:log.origin.thread} %{GREEDYDATA:custom.message}"
      }
    }
    
    mutate {
      uppercase => { "custom.type" => "custom.type" }
    }
  }
  
  # MySQL Format
  if [message] =~ /^fmt=mysql/ {
    grok {
      match => { 
        "message" => "fmt=%{WORD:custom.type} %{TIMESTAMP_ISO8601:@timestamp} %{DATA:user.name}\[%{DATA:user.name}\] @ %{IPORHOST:host.ip} \[%{TIMESTAMP_ISO8601:query_timestamp}\] %{NUMBER:event.duration:float} %{NUMBER:lock_time:float} %{NUMBER:db.rows_sent:int} %{NUMBER:db.rows_examined:int} %{DATA:database.name} %{GREEDYDATA:db.query}"
      }
    }
    
    mutate {
      uppercase => { "custom_type" => "custom_type" }
      add_field => { "custom.type" => "%{custom_type}" }
      remove_field => [ "query_timestamp", "lock_time" ]
    }
  }
  
  # Redis Format
  if [message] =~ /^fmt=redis/ {
    grok {
      match => { 
        "message" => "fmt=%{WORD:custom.type} %{TIMESTAMP_ISO8601:@timestamp} %{WORD:log.level} %{NUMBER:process.pid:int}:%{DATA:process_type} %{DATA:service.role} %{GREEDYDATA:custom.message}"
      }
    }
    
    mutate {
      uppercase => { "custom.type" => "custom.type" }
      remove_field => [ "process_type" ]
    }
  }
}
```

## Elasticsearch Index Template

```json
{
  "index_patterns": ["logs-*"],
  "template": {
    "mappings": {
      "properties": {
        "@timestamp": { "type": "date" },
        "client.ip": { "type": "ip" },
        "http.request.method": { "type": "keyword" },
        "http.request.uri.original": { "type": "text" },
        "http.response.status_code": { "type": "long" },
        "http.response.bytes": { "type": "long" },
        "http.request.referrer": { "type": "keyword" },
        "user_agent.original": { "type": "text" },
        "event.duration": { "type": "float" },
        "service.name": { "type": "keyword" },
        "log.level": { "type": "keyword" },
        "user.id": { "type": "keyword" },
        "transaction.id": { "type": "keyword" },
        "transaction.amount": { "type": "float" },
        "client.geo.country_iso_code": { "type": "keyword" },
        "session.id": { "type": "keyword" },
        "process.name": { "type": "keyword" },
        "host.name": { "type": "keyword" },
        "system.memory.total": { "type": "long" },
        "system.cpu.total.pct": { "type": "float" },
        "log.origin.thread": { "type": "keyword" },
        "user.name": { "type": "keyword" },
        "host.ip": { "type": "ip" },
        "db.rows_sent": { "type": "long" },
        "db.rows_examined": { "type": "long" },
        "database.name": { "type": "keyword" },
        "db.query": { "type": "text" },
        "process.pid": { "type": "long" },
        "service.role": { "type": "keyword" },
        "custom.type": { "type": "keyword" },
        "custom.message": { "type": "text" }
      }
    }
  }
}
```

## Key Benefits

1. **Direct ECS Field Extraction**: No intermediate field mapping required
2. **Simplified Configuration**: Reduced Logstash configuration complexity
3. **Better Performance**: Fewer field transformations needed
4. **Consistent Naming**: All fields follow ECS standards from extraction
5. **Easy Filtering**: Use `custom.type: "APACHE"` for format-specific queries

## Usage Examples

**Kibana Discover Filters:**
- `custom.type: "APACHE"` - Apache logs only
- `custom.type: "MYSQL"` - MySQL logs only
- `http.response.status_code: 500` - HTTP 500 errors
- `log.level: "ERROR"` - Error level logs
- `service.name: "checkout"` - Checkout service logs

**Elasticsearch Queries:**
```json
{
  "query": {
    "bool": {
      "must": [
        { "term": { "custom.type": "APACHE" } },
        { "range": { "http.response.status_code": { "gte": 400 } } }
      ]
    }
  }
}
```
