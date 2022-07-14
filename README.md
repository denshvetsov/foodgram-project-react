# praktikum_new_diplom
![foodgram ci workflow](https://github.com/denshvetsov/foodgram-project-react/actions/workflows/main.yml/badge.svg)

## Cтек технологий:
[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=56C0C0&color=008080)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat&logo=Django&logoColor=56C0C0&color=008080)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat&logo=Django%20REST%20Framework&logoColor=56C0C0&color=008080)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat&logo=PostgreSQL&logoColor=56C0C0&color=008080)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat&logo=NGINX&logoColor=56C0C0&color=008080)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat&logo=gunicorn&logoColor=56C0C0&color=008080)](https://gunicorn.org/)
[![Docker](https://img.shields.io/badge/-Docker-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![Docker-compose](https://img.shields.io/badge/-Docker%20compose-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![Docker Hub](https://img.shields.io/badge/-Docker%20Hub-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/products/docker-hub)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat&logo=GitHub%20actions&logoColor=56C0C0&color=008080)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat&logo=Yandex.Cloud&logoColor=56C0C0&color=008080)](https://cloud.yandex.ru/)

## Сайт

https://foodgram.auxlink.com/

# Foodgram - «Продуктовый помощник»

Пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд

# Системные требования
- выделенный linux Ubuntu сервер
- внешний IP адрес
- зарегистрировнное доменное имя
- nginx
- cerbot
- docker
- docker compose

# Установка
Подготовьте сервер к установке
Клонируйте репозиторий
в каталоге /infra/ Создайте .env файл в формате

DEBUG=False
SECRET_KEY=Ah!Is3g|&~6f9_DgQE["$8(A$]<:&&
ALLOWED_HOSTS=127.0.0.1 10.0.1.100 localhost web foodgram.auxlink.com 95.165.26.109 backend
CSRF_TRUSTED_ORIGINS = http://localhost http://127.0.0.1 https://foodgram.auxlink.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
EMAIL_HOST=smtp.<ваш домен>.ru
EMAIL_PORT=587
EMAIL_HOST_USER=<ваша почта>
EMAIL_HOST_PASSWORD=<ваш пароль>
DEFAULT_FROM_EMAIL=<ваша почта>
EMAIL_USE_TLS=True

скопируйте папку /infra/
scp -r infra/* di@<you server ip>:/home/<username>/foodgram/

подключитесь к серверу через ssh и перейдите в каталог
/home/<username>/foodgram/

запустите установку и сборку контейнеров
docker compose up -d

## Полезные команды при работе с Docker
посмотреть логи контейнера
docker logs --since=1h <container_id>

подключить к контейнеру
docker exec -it bb2bfcf5a354 sh

# список контейнеров, образов, и volumes
docker ps
docker image ls
docker volume ls

остановить все контейнеры и удалить
docker compose stop
sudo docker compose rm web
docker stop $(docker ps -a -q) 
docker rm $(docker ps -a -q)
docker rmi $(docker image ls)

# остановить и удалить все контенеры на сервере
docker stop $(docker ps -a -q) && docker rm $(docker ps -a -q) && docker rmi $(docker image ls)


# Создайте суперпользователя
Создайте администратора как в обычном Django-проекте
docker ps
docker exec -it <CONTAINER ID> bash

python manage.py createsuperuser

теперь вы можете работать с админ панелью
<you server name>/admin/


# Автор backend сервисов
[Денис Швецов](https://github.com/denshvetsov)



