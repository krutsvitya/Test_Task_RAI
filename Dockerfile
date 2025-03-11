FROM python:3.12-slim

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Копируем скрипт запуска
COPY startup.sh /startup.sh

# Делаем скрипт исполняемым
RUN chmod +x /startup.sh

# Открываем порт
EXPOSE 8000

# Запускаем скрипт при старте контейнера
CMD ["/startup.sh"]