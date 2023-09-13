<div align="center">

  # FoodGram <br> Продуктовый помощник

  ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
  ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
  ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)

  ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
  ![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
  ![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
  
  ![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
</div>

## Описание проекта

FoodGram - онлайн-сервис, по поиску и созданию кулинарных шедевров. 
В рамках данного сервиса пользователи могут делиться своими рецептами, 
подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список избранного,
а также скачивать сводный список продуктов в формате pdf.

## Подготовка сервера и деплой проекта

1. Создать директорию foodgram/ в домашней директории сервера.

2. В корне папки foodgram поместить файл .env, заполнить его по шаблону

  ```env
  # Django environments
  DJANGO_TOKEN= ...
  DJANGO_DEBUG= ...
  DJANGO_HOSTS= ...
  
  # Postgres environments
  POSTGRES_DB= ...
  POSTGRES_USER= ...
  POSTGRES_PASSWORD= ...
  DB_HOST= ...
  DB_PORT= ...
```

4. Установить Nginx и настроить конфигурацию так, чтобы все запросы шли в контейнеры на порт 8000.

    ```bash
        sudo apt install nginx -y 
        sudo nano etc/nginx/sites-enabled/default
    ```
    
    Пример конфигурация nginx
    ```bash
        server {
            server_name <IP> <Домен сайта>;
            server_tokens off;
        
            location / {
                proxy_set_header Host $http_host;
                proxy_pass http://127.0.0.1:8000;
        }
    ```
    
    > При необходимости настройте SSL-соединение

5. Установить docker и docker-compose
   
``` bash
    sudo apt update
    sudo apt install curl
    curl -fSL https://get.docker.com -o get-docker.sh
    sudo sh ./get-docker.sh
    sudo apt-get install docker-compose-plugin     
```

4. Добавить в Secrets GitHub Actions данного репозитория на GitHub переменные окружения

``` env
    DOCKER_USERNAME=<имя пользователя DockerHub>
    DOCKER_PASSWORD=<пароль от DockerHub>
    
    USER=<username для подключения к удаленному серверу>
    HOST=<ip сервера>
    PASSPHRASE=<пароль для сервера, если он установлен>
    SSH_KEY=<ваш приватный SSH-ключ>
    
    TELEGRAM_TO=<id вашего Телеграм-аккаунта>
    TELEGRAM_TOKEN=<токен вашего бота>
```
5. Запустить workflow проекта выполнив команды:

```bash
  git add .
  git commit -m ''
  git push
```
## Документация
С примерами запросов можно ознакомиться в [Документации](http://localhost/api/redoc/)

<div align=center>

## Контакты

[![Telegram Badge](https://img.shields.io/badge/-youzoff-blue?style=social&logo=telegram&link=https://t.me/youzoff)](https://t.me/dkushlevich) [![ Badge](https://img.shields.io/badge/-k.yuzov@yandex.ru-c14438?style=flat&logo=Gmail&logoColor=white&link=mailto:k.yuzov@yandex.ru)](mailto:k.yuzov@yandex.ru)

</div>
