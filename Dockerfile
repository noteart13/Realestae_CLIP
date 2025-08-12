# Sử dụng python base image (slim để nhẹ hơn)
FROM python:3.10-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Sao chép file requirements và cài đặt các thư viện
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn vào image
COPY . .

# Expose cổng 8000 (cổng chạy Uvicorn bên trong container)
EXPOSE 8000

# Lệnh khởi chạy container: chạy Uvicorn server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
