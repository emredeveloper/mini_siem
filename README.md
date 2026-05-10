# Mini SIEM

Bu demo proje su akisi kurar:

`FastAPI backend -> JSON log dosyasi -> Filebeat -> Elasticsearch -> Kibana`

Amac:

- Backend loglarini merkezi olarak toplamak
- Hatalari ve trafik artislarini Kibana uzerinden gormek
- Istek surelerini ve problemli endpointleri izlemek

## Klasor Yapisi

- `backend/`: Ornek API ve JSON log uretimi
- `filebeat/`: Loglari Elasticsearch'e tasiyan agent config'i
- `kibana/`: Dashboard olusturma adimlari
- `scripts/`: Demo trafik uretme yardimcilari

## Gereksinimler

- Docker Desktop veya Docker Engine + Docker Compose

## 1. Stack'i Baslat

Bu klasorde:

```powershell
docker compose up --build
```

Servisler:

- Backend: `http://localhost:8000`
- Elasticsearch: `http://localhost:9200`
- Kibana: `http://localhost:5601`

## 2. Ornek Trafik Uret

Yeni bir terminalde:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\generate-traffic.ps1
```

Istersen elle de test edebilirsin:

```powershell
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:8000/simulate/slow
Invoke-RestMethod http://localhost:8000/simulate/error
```

## 3. Elasticsearch'e Gelen Loglari Kontrol Et

```powershell
Invoke-RestMethod "http://localhost:9200/mini-siem-logs-*/_search?size=5&sort=%40timestamp:desc"
```

Beklenen alanlar:

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

Adimlar icin:

- `kibana/dashboard-guide.md`

Bu guide ile su gorunumleri olusturursun:

- Toplam hata sayisi
- Dakikalik trafik grafigi
- 5xx endpointleri
- Yavas istek tablosu

## Neden Bu Mimari?

Bu ilk surumde backend loglari dogrudan Elasticsearch'e yazmiyor. Bunun yerine loglar once JSON olarak diske yaziliyor, sonra Filebeat bunlari Elasticsearch'e gonderiyor. Bu yapi gercek projelerde daha dayanikli olur:

- Uygulama Elasticsearch baglantisina dogrudan bagimli olmaz
- Log forwarding uygulama kodundan ayrilir
- Log formatini Filebeat seviyesinde gelistirmek kolaylasir

## Sonraki Adimlar

Istersek bir sonraki turda sunlari ekleyebiliriz:

1. Kibana dashboard'unu otomatik import eden saved objects dosyasi
2. Slack / e-posta alarm mekanizmasi
3. Filebeat yerine Logstash ile zenginlestirme
4. Auth, rate limit ve kullanici bazli izleme alanlari
