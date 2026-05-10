# Mini SIEM

This demo project establishes the following data flow:

`FastAPI backend -> JSON log file -> Filebeat -> Elasticsearch -> Kibana`

**Purpose:**

- Centrally collect backend logs
- View errors and traffic anomalies through Kibana
- Monitor request durations and problematic endpoints

## Folder Structure

- `backend/`: Sample API and JSON log generation
- `filebeat/`: Agent configuration that ships logs to Elasticsearch
- `kibana/`: Dashboard creation steps
- `scripts/`: Demo traffic generation helpers

## Requirements

- Docker Desktop or Docker Engine + Docker Compose

## 1. Start the Stack

In this directory:

```powershell
docker compose up --build
```

Services:

- Backend: `http://localhost:8000`
- Elasticsearch: `http://localhost:9200`
- Kibana: `http://localhost:5601`

## 2. Generate Sample Traffic

In a new terminal:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\generate-traffic.ps1
```

Or test manually if you prefer:

```powershell
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:8000/simulate/slow
Invoke-RestMethod http://localhost:8000/simulate/error
```

## 3. Verify Logs in Elasticsearch

```powershell
Invoke-RestMethod "http://localhost:9200/mini-siem-logs-*/_search?size=5&sort=%40timestamp:desc"
```

Expected fields:

- `@timestamp`
- `message`
- `log.level`
- `event.category`
- `event.type`
- `http.request.method`
- `http.response.status_code`
- `url.path`
- `client.ip`
- `labels.duration_ms`

## 4. Kibana Dashboard

For setup steps, see:

- `kibana/dashboard-guide.md`

With this guide, you'll create the following visualizations:

- Total error count
- Traffic per minute chart
- 5xx status endpoints
- Slow requests table

## Why This Architecture?

In this initial version, the backend doesn't write logs directly to Elasticsearch. Instead, logs are first written as JSON to disk, then Filebeat ships them to Elasticsearch. This approach is more resilient in real-world projects:

- The application doesn't depend directly on Elasticsearch connectivity
- Log forwarding is decoupled from application code
- Log formatting can be enhanced at the Filebeat level

## Next Steps

In future iterations, we could add:

1. Automated Kibana dashboard import via saved objects
2. Slack / email alerting mechanism
3. Log enrichment with Logstash instead of Filebeat
4. Auth, rate limit ve kullanici bazli izleme alanlari
