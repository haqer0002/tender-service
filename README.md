# Tender Service

Сервис проведения тендеров предоставляет API для управления тендерами и предложениями, позволяя организациям создавать тендеры, а пользователям предлагать свои услуги.

## Стек технологий

- **Язык программирования:** Python 3.12.4
- **Веб-фреймворк:** FastAPI
- **База данных:** PostgreSQL
- **Контейнеризация:** Docker, Docker Compose

## Запуск проекта

### Предварительные требования

Убедитесь, что у вас установлены следующие инструменты:

- [Git](https://git-scm.com/downloads)
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Инструкция по запуску

1. **Клонирование репозитория**

   Клонируйте репозиторий проекта на ваш локальный компьютер:

   ```bash
   git clone https://github.com/haqer0002/tender-service.git
   ```
   Перейдите в директорию проекта:
   ```bash
    cd tender-service
   ```
2. **Запуск приложения с помощью Docker Compose**

   Выполните следующую команду для сборки и запуска контейнеров:
   ```bash
   docker-compose up --build
   ```
   Эта команда:
   - Соберет Docker-образ приложения.
   - Запустит контейнеры приложения и базы данных PostgreSQL.
   - Настроит связь между контейнерами.<br><br>

    <p> Если Docker не запускается или что-то работает не корректно, выполните следующую команду
    для остановки и удаления собранных контейнеров.</p>
   
      ```bash
      docker-compose down
      ```
3. **Запуск приложения с помощью Docker Compose**
    
    <p>После успешного запуска вы можете проверить доступность сервера с помощью команды:</p>

    ```bash
   curl -X GET http://localhost:8080/api/ping
    ```
   **Ожидаемый ответ:**

    ```json
   {"message": "ok"}
    ```
   
4. Доступ к документации API

    Вы можете использовать автоматически сгенерированную документацию Swagger UI для взаимодействия с API.
    
    Откройте в вашем браузере:
    
    ```bash
    http://localhost:8080/docs
    ```
    
    Здесь вы найдете описание всех доступных эндпоинтов и сможете протестировать их напрямую.

## Структура проекта

- **main.py**: Основной файл приложения FastAPI с определением всех эндпоинтов.
- **Dockerfile**: Файл для сборки Docker-образа приложения.
- **docker-compose.yml**: Конфигурационный файл Docker Compose для запуска приложения и базы данных.
- **requirements.txt**: Файл с зависимостями Python для проекта.
- **.env**: Файл с переменными окружения (необходимо создать самостоятельно).
- **README.md**: Документация проекта.
- **.gitignore**: Файл с исключениями для Git.
- **.dockerignore**: Файл с исключениями для Docker

## Возможные проблемы и их решения

### Ошибка подключения к базе данных:

Убедитесь, что сервис базы данных PostgreSQL запущен и доступен по указанному адресу и порту.

### Порты уже заняты:

Если порты `8080` или `5432` уже используются, измените их в файле `docker-compose.yml`:

```yaml
ports:
  - "8081:8080"  # Для приложения
  - "5433:5432"  # Для базы данных
```

И соответствующим образом обновите адреса в командах и настройках.

