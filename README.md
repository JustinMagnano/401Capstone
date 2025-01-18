# Website
https://jarinvestments-e5gfgdh7d7axf7fh.centralus-01.azurewebsites.net/

# Capstone Project JAR StockApp

IFT401 Fall2024

Team:

Allysa Figueroa, Justin Magnano, Richard Watters 

Start Django Project:

    $ python3 manage.py runserver
## Pre-requisite Downloads

    $ sudo apt install python3.10.12 64bit
    $ sudo apt install django.admin 5.1
    $ sudo apt install python3-venv python3-pip
    $ pip3 install pipenv
    $ pip3 install utils
    $ pip install django-filter


## Setting up Python Virtual Environment

Necessary for not modifying Local Host Variables.

    $ mkdir NAME

*NAME = The directory can be named to whatever you want to.*

    $ cd NAME

    $ pip install django pipenv shell

*Creates Virtual Environment*

Example when in Virtual Environment:

    myprojectallysa@DESKTOP-IGQKR4N:~/dev/pythonDev/bankCode3$

Turn off Virtual Environment

    $ deactivate
## Updating DB from models.py:

Classes represent tables in the database.

Assigning tables from Classes.

    $ python manage.py makemigration
    $ python manage.py migrate # create table and add to database

## Make Class Table viewable in Django Object Admin Panel:

In stockApp/admin.py 

    from django.contrib import admin

    # Register your models here.
    from .models import *

    admin.site.register(Stock)
    admin.site.register(Portfolio)
    admin.site.register(Transaction)
    admin.site.register(Account)

## Creating Superuser:

Needed for accessing Django Object Admin Panel.
    
    $ python3 manage.py createsuperuser

## Change static filepath to localhost path:

Static html, css and js files will not load correctly if the full filepath is listed.

In myProject/settings.py:
    
    # change static filepath to localhost path where django project is located
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, '/home/allysa/dev/pythonDev/bankCode3/myproject/myproject/stockApp/static/stockApp'),
    ]
