# Yatube

## Описание проекта:
Проект сайта-дневника. После регистрации можно:
- создавать посты;
- прикреплять изображения;
- подписываться/отписываться на авторов; 
- оставлять к постам комментарии.

## Запуск проекта

Клонируйте репозиторий: 
 
``` 
git clone https://github.com/anton8963kobelev/hw05_final.git
``` 

Перейдите в папку проекта в командной строке:

``` 
cd hw05_final
``` 

Создайте и активируйте виртуальное окружение:

``` 
python -m venv venv
``` 
``` 
source venv/Scripts/activate
``` 

Установите зависимости из файла *requirements.txt*: 
 
``` 
pip install -r requirements.txt
``` 


Выполните миграции и соберите статику проекта: 
 
``` 
python manage.py migrate
``` 
``` 
python manage.py collectstatic
``` 

Запустите сервер:
``` 
python manage.py runserver
``` 
