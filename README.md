# Приложение RAI

## Быстрый запуск

### Требования
- Docker и Docker Compose, а также `.env` файл

### Установка и запуск

1. Клонируйте этот репозиторий

2. Откройте терминал в папке с файлами и выполните:

```bash
docker-compose up -d
```

3. Дождитесь запуска обоих контейнеров (это может занять несколько минут при первом запуске)

4. Приложение будет доступно по адресу: http://localhost:8000

## Информация о портах
- Web-приложение: 8000
- PostgreSQL: 5434 (внешний порт)
