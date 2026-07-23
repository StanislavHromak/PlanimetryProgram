# Використовуємо офіційний легкий образ Python
FROM python:3.12-slim

# Встановлюємо системні залежності (потрібні для bcrypt та cryptography)
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Встановлюємо робочу директорію всередині контейнера
WORKDIR /app

# Копіюємо файл з залежностями
COPY requirements.txt .

# Встановлюємо залежності
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь інший код проєкту
COPY . .

# Відкриваємо порт, на якому працює FastAPI
EXPOSE 8000

# Команда для запуску сервера
CMD ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"]