# yamdb_final
![Django-app workflow](https://github.com/Maltassarus/yamdb_final/actions/workflows/yamdb_workflow.yaml/badge.svg)

CI и CD проекта api_yamdb

## Технологии в проекте
- Python 3.7
- Django 2.2.16
- REST Framework 3.12.4
- PyJWT 2.1.0
- Django filter 2.4.0
- Gunicorn 20.0.4

и т. д. (см. requirements.txt)

## Инструкции по запуску



### Переменные .env файла
```
# логин для подключения к серверу по ssh
USER
# IP-адрес сервера
HOST
# Пароль для сервера (в случае наличия)
PASSPHRASE
# SSH-ключ
SSH_KEY
# ID чата в месседжере "Телеграм"
TELEGRAM_TO
# токен бота в месседжере "Телеграм"
TELEGRAM_TOKEN
# переменная с типом БД
DB_ENGINE
# имя БД
DB_NAME
# имя пользователя БД
POSTGRES_USER
# пароль к БД
POSTGRES_PASSWORD
# название контейнера
DB_HOST
# порт БД
DB_PORT
# Имя пользователя DockerHub
DOCKER_USER
# Пароль аккаунта на DockerHub
DOCKER_PASSWORD
```

## Адрес сервера с приложением
http://yamdb-maltassarus.ddns.net/