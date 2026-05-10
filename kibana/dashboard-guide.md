# Kibana Dashboard Adimlari

Bu proje ilk asamada dashboard'u otomatik import etmek yerine elle ve kontrollu sekilde kuruyor. Asagidaki paneller 5-10 dakikada olusur.

## 1. Data View

1. Kibana'yi ac: `http://localhost:5601`
2. `Stack Management > Data Views > Create data view`
3. Name: `Mini SIEM Logs`
4. Index pattern: `mini-siem-logs-*`
5. Timestamp field: `@timestamp`

## 2. Dashboard

1. `Analytics > Dashboard > Create dashboard`
2. Asagidaki Lens panellerini ekle.

## 3. Panel: Hata Sayisi

- Chart type: `Metric`
- Metric: `Count`
- Filter: `event.category: "error" OR log.level: "error"`
- Kaydet: `Toplam Hata Sayisi`

## 4. Panel: Dakikalik Trafik

- Chart type: `Line`
- Horizontal axis: `@timestamp`
- Interval: `1 minute`
- Vertical axis: `Count`
- Break down by (opsiyonel): `http.request.method`
- Kaydet: `Dakikalik Trafik`

## 5. Panel: En Problemli Endpointler

- Chart type: `Bar horizontal`
- Vertical axis: `Count`
- Break down or category: `Top values of url.path`
- Filter: `http.response.status_code >= 500 OR event.category: "error"`
- Kaydet: `5xx Endpointleri`

## 6. Panel: Yavas Istekler

- Chart type: `Table`
- Rows: `url.path`, `http.response.status_code`
- Metric: `Average of labels.duration_ms`
- Filter: `labels.duration_ms >= 500`
- Kaydet: `Yavas Istekler`

## 7. Dashboard Ismi

Dashboard ismi onerisi: `Mini SIEM Overview`

Bu ilk versiyon; ikinci adimda istersek ayni dashboard'u Kibana saved objects olarak otomatik import edilecek hale getirebiliriz.
