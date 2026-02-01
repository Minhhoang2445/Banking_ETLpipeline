# 🏦 Banking Data Ingestion Platform

> **Mini Data Platform** - Hệ thống ETL xử lý dữ liệu ngân hàng sử dụng FastAPI + Apache Airflow + Docker

---

## 📋 Giới thiệu dự án

### Mục đích

Đây là một hệ thống **Data Ingestion** cho phép:

- Upload file dữ liệu ngân hàng (Excel/CSV) qua REST API
- Tự động chuyển đổi Excel → CSV
- Trigger pipeline xử lý dữ liệu (ETL) thông qua Apache Airflow
- Lưu kết quả vào Data Warehouse (PostgreSQL)

### Bài toán giải quyết

Trong thực tế, dữ liệu khách hàng ngân hàng thường được xuất từ các hệ thống legacy dưới dạng Excel/CSV. Dự án này giải quyết bài toán:

| Vấn đề                         | Giải pháp                                                       |
| ------------------------------ | --------------------------------------------------------------- |
| Xử lý thủ công file Excel/CSV  | API tự động nhận và xử lý file                                  |
| Không có quy trình ETL rõ ràng | Airflow DAG với các bước: Validate → Extract → Transform → Load |
| Trùng lặp dữ liệu              | Hash file để phát hiện file đã upload                           |
| Khó triển khai môi trường      | Docker Compose một bước                                         |

---

## 🏗️ Kiến trúc tổng quan

```
┌────────────────┐    ┌─────────────────┐    ┌──────────────────┐
│   Client       │    │   FastAPI       │    │   Apache Airflow │
│  (Upload file) │───▶│  Ingestion API  │───▶│   ETL Pipeline   │
└────────────────┘    └─────────────────┘    └──────────────────┘
                             │                        │
                             ▼                        ▼
                      ┌─────────────┐         ┌──────────────┐
                      │ /data folder│         │  PostgreSQL  │
                      │ (CSV files) │         │  Data Warehouse│
                      └─────────────┘         └──────────────┘
```

### Thành phần chính

| Component          | Mô tả                                                            |
| ------------------ | ---------------------------------------------------------------- |
| **FastAPI**        | REST API nhận file upload, chuyển đổi Excel→CSV, trigger Airflow |
| **Apache Airflow** | Điều phối và thực thi pipeline ETL                               |
| **PostgreSQL**     | Database cho Airflow metadata + Data Warehouse                   |
| **Docker Compose** | Đóng gói và chạy toàn bộ hệ thống                                |

---

## 💻 Yêu cầu hệ thống

### Chạy bằng Docker (khuyến nghị)

- **Docker Desktop**: phiên bản 20.x trở lên
- **Docker Compose**: phiên bản 2.x trở lên
- **RAM**: tối thiểu 4GB
- **Disk**: tối thiểu 2GB trống

### Chạy local (không Docker)

- **Python**: 3.9 - 3.11
- **PostgreSQL**: 13.x trở lên
- **pip**: phiên bản mới nhất

---

## 📁 Cấu trúc thư mục

```
FinalProject/
├── 📂 ingestion_api/          # FastAPI Application
│   ├── main.py                # Entry point của API
│   ├── routers/               # API endpoints
│   │   └── ingest.py          # Endpoint upload file
│   ├── services/              # Business logic
│   │   └── file_ingest_service.py
│   └── schemas/               # Pydantic schemas
│       └── ingest_response.py
│
├── 📂 dags/                   # Airflow DAGs
│   └── banking_campaign_analysis_dag.py  # Pipeline ETL chính
│
├── 📂 plugins/                # Airflow custom operators & helpers
│   ├── extract.py             # Trích xuất dữ liệu
│   ├── transform.py           # Chuyển đổi dữ liệu
│   ├── load.py                # Load vào Data Warehouse
│   ├── validateFile.py        # Validate file (hash check)
│   ├── validateData.py        # Validate dữ liệu
│   └── prepareStaging.py      # Chuẩn bị bảng staging
│
├── 📂 data/                   # Thư mục chứa file CSV đã upload
├── 📂 logs/                   # Airflow logs
├── 📂 scripts/                # Scripts hỗ trợ
│
├── docker-compose.yaml        # Cấu hình Docker services
├── requirements.txt           # Python dependencies
├── .env                       # Biến môi trường
└── README.md                  # Tài liệu này
```

---

## 🐳 Hướng dẫn chạy bằng Docker

### Bước 1: Clone source code

```bash
git clone <repository-url>
cd FinalProject
```

### Bước 2: Cấu hình môi trường

Kiểm tra file `.env` và cập nhật nếu cần:

```env
AIRFLOW_UID=50000
```

### Bước 3: Khởi tạo Airflow và chạy các services

```bash
# Khởi chạy toàn bộ hệ thống
docker-compose up -d

# Xem logs (optional)
docker-compose logs -f
```

> ⏱️ **Lần đầu chạy sẽ mất 2-3 phút** để Airflow khởi tạo database và tạo user admin.

### Bước 4: Khởi chạy FastAPI (chạy riêng trên host)

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Chạy FastAPI
cd ingestion_api
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Bước 5: Truy cập các services

| Service                  | URL                        | Credentials       |
| ------------------------ | -------------------------- | ----------------- |
| **FastAPI Docs**         | http://localhost:8000/docs | -                 |
| **Airflow Web UI**       | http://localhost:8080      | admin / admin     |
| **PostgreSQL (Airflow)** | localhost:5434             | airflow / airflow |

### Dừng hệ thống

```bash
docker-compose down

# Xóa cả volumes (reset data)
docker-compose down -v
```

---

## 🖥️ Hướng dẫn chạy Local (không Docker)

### Bước 1: Tạo Virtual Environment

```bash
# Tạo virtualenv
python -m venv venv

# Kích hoạt (Windows)
.\venv\Scripts\activate

# Kích hoạt (Linux/Mac)
source venv/bin/activate
```

### Bước 2: Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Bước 3: Cấu hình Airflow (nếu chạy local)

```bash
# Thiết lập AIRFLOW_HOME
export AIRFLOW_HOME=$(pwd)

# Khởi tạo database
airflow db init

# Tạo user admin
airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com
```

### Bước 4: Chạy FastAPI

```bash
cd ingestion_api
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Bước 5: Chạy Airflow (2 terminal riêng)

```bash
# Terminal 1: Webserver
airflow webserver --port 8080

# Terminal 2: Scheduler
airflow scheduler
```

---

## 📡 Cách sử dụng API

### Endpoint Upload File

| Method | Endpoint       | Mô tả                          |
| ------ | -------------- | ------------------------------ |
| `POST` | `/ingest/file` | Upload file Excel/CSV để xử lý |

### Ví dụ Request bằng cURL

**Upload file CSV:**

```bash
curl -X POST "http://localhost:8000/ingest/file" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@banking_data.csv"
```

**Upload file Excel (.xlsx):**

```bash
curl -X POST "http://localhost:8000/ingest/file" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@banking_data.xlsx"
```

### Response thành công

```json
{
  "message": "File ingested successfully (standardized to CSV)",
  "csv_path": "/opt/airflow/data/banking_20250201_174500.csv"
}
```

### Sử dụng Swagger UI

1. Truy cập http://localhost:8000/docs
2. Chọn endpoint `POST /ingest/file`
3. Click **Try it out**
4. Chọn file và click **Execute**

---

## 🔄 Luồng xử lý dữ liệu

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           LUỒNG XỬ LÝ DỮ LIỆU                            │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. UPLOAD FILE                                                          │
│     └─▶ Client gửi file Excel/CSV đến API /ingest/file                   │
│                                                                          │
│  2. LƯU FILE TẠM                                                         │
│     └─▶ FastAPI lưu file vào thư mục tạm (tempfile)                      │
│                                                                          │
│  3. CONVERT EXCEL → CSV (nếu cần)                                        │
│     └─▶ Sử dụng pandas để chuyển đổi .xlsx → .csv                        │
│     └─▶ Lưu CSV vào thư mục /data với timestamp                          │
│                                                                          │
│  4. TRIGGER AIRFLOW DAG                                                  │
│     └─▶ Gọi Airflow REST API để chạy DAG: banking_etl_pipeline           │
│     └─▶ Truyền csv_path qua dag_run.conf                                 │
│                                                                          │
│  5. AIRFLOW PIPELINE (DAG)                                               │
│     ├─▶ validate_file: Hash file để kiểm tra trùng lặp                   │
│     ├─▶ prepare_staging: Tạo/reset bảng staging                          │
│     ├─▶ extract: Đọc CSV và load vào staging table                       │
│     ├─▶ transform: Chuyển đổi và làm sạch dữ liệu                        │
│     ├─▶ validate_data: Validate dữ liệu đã transform                     │
│     └─▶ load: Lưu vào Data Warehouse và đánh dấu processed               │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### Chi tiết các bước trong Airflow DAG

| Task              | Mô tả                                                  | File                |
| ----------------- | ------------------------------------------------------ | ------------------- |
| `validate_file`   | Tính SHA256 hash của file, kiểm tra trùng lặp trong DB | `validateFile.py`   |
| `prepare_staging` | Tạo bảng staging nếu chưa có                           | `prepareStaging.py` |
| `extract`         | Đọc CSV và insert vào staging table                    | `extract.py`        |
| `transform`       | Làm sạch, chuẩn hóa dữ liệu                            | `transform.py`      |
| `validate_data`   | Kiểm tra chất lượng dữ liệu                            | `validateData.py`   |
| `load`            | Load vào bảng chính trong Data Warehouse               | `load.py`           |

---

## ⚙️ Cấu hình

### Biến môi trường quan trọng

| Biến                      | Mô tả                                | Giá trị mặc định                                                          |
| ------------------------- | ------------------------------------ | ------------------------------------------------------------------------- |
| `AIRFLOW_UID`             | User ID cho Airflow container        | `50000`                                                                   |
| `DW_CONN_STRING`          | Connection string đến Data Warehouse | `postgresql+psycopg2://postgres:123456@host.docker.internal:5433/Banking` |
| `AIRFLOW__CORE__EXECUTOR` | Executor type                        | `LocalExecutor`                                                           |

### Airflow API Credentials

```python
AIRFLOW_URL = "http://localhost:8080"
AIRFLOW_USER = "admin"
AIRFLOW_PASS = "admin"
```

---

## 📝 Ghi chú & Hướng phát triển

### ✅ Tính năng đã có

- [x] Upload file CSV/Excel qua API
- [x] Tự động chuyển đổi Excel → CSV
- [x] Trigger Airflow DAG tự động
- [x] Hash file để chống trùng lặp (SHA256)
- [x] ETL Pipeline hoàn chỉnh

### 🚀 Hướng phát triển tiếp

- [ ] **Validate file nâng cao**: Kiểm tra schema, data types trước khi xử lý
- [ ] **Deduplication thông minh**: So sánh hash theo từng row, không chỉ file
- [ ] **Monitoring & Alerting**: Tích hợp Prometheus + Grafana
- [ ] **Logging tập trung**: Sử dụng ELK Stack (Elasticsearch, Logstash, Kibana)
- [ ] **Scale horizontal**: Sử dụng CeleryExecutor với Redis/RabbitMQ
- [ ] **Authentication**: Thêm JWT authentication cho API
- [ ] **Rate limiting**: Giới hạn số request để bảo vệ hệ thống
- [ ] **Retry mechanism**: Tự động retry khi task thất bại

### 🐛 Troubleshooting

| Lỗi                               | Nguyên nhân                 | Giải pháp                                                 |
| --------------------------------- | --------------------------- | --------------------------------------------------------- |
| Airflow Web UI không load         | Database chưa khởi tạo xong | Đợi 2-3 phút hoặc chạy `docker-compose logs airflow-init` |
| Upload file lỗi 500               | Airflow chưa sẵn sàng       | Kiểm tra Airflow đang chạy và DAG đã unpause              |
| File đã được xử lý trước đó       | Hash trùng lặp              | Đây là tính năng chống duplicate, upload file khác        |
| Không kết nối được Data Warehouse | Connection string sai       | Kiểm tra `DW_CONN_STRING` trong docker-compose.yaml       |

---

## 👥 Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng:

1. Fork repository
2. Tạo branch mới (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Mở Pull Request

---

## 📄 License

Dự án này được phát triển cho mục đích học tập.

---

<p align="center">
  <b>Made with ❤️ for Data Engineering Learning</b>
</p>
