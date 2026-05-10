# Kibana Dashboard Setup

In this version, instead of automatically importing the dashboard, we set it up manually and deliberately. The panels below take 5-10 minutes to create.

## 1. Create Data View

1. Open Kibana: `http://localhost:5601`
2. Go to `Stack Management > Data Views > Create data view`
3. Name: `Mini SIEM Logs`
4. Index pattern: `mini-siem-logs-*`
5. Timestamp field: `@timestamp`

## 2. Create Dashboard

1. Go to `Analytics > Dashboard > Create dashboard`
2. Add the Lens panels listed below.

## 3. Panel: Error Count

- Chart type: `Metric`
- Metric: `Count`
- Filter: `event.category: "error" OR log.level: "error"`
- Save as: `Total Error Count`

## 4. Panel: Traffic per Minute

- Chart type: `Line`
- Horizontal axis: `@timestamp`
- Interval: `1 minute`
- Vertical axis: `Count`
- Break down by (optional): `http.request.method`
- Save as: `Traffic per Minute`

## 5. Panel: Top Problem Endpoints

- Chart type: `Bar horizontal`
- Vertical axis: `Count`
- Break down or category: `Top values of url.path`
- Filter: `http.response.status_code >= 500 OR event.category: "error"`
- Save as: `5xx Endpoints`

## 6. Panel: Slow Requests

- Chart type: `Table`
- Rows: `url.path`, `http.response.status_code`
- Metric: `Average of labels.duration_ms`
- Filter: `labels.duration_ms >= 500`
- Save as: `Slow Requests`

## 7. Dashboard Name

Suggested dashboard name: `Mini SIEM Overview`

This is the first version; in a future iteration we can make this dashboard auto-importable as a Kibana saved object.
