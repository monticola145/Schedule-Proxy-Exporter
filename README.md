# schedule-proxy-exporter

## О приложении

Данное приложение нацелено на экспорт пар и занятий из РУЗ'а в Opencast

## Начало работы
### Настройка приложения

Для функционирования необходимо внести изменения в следующие файлы в папке OpencastAPI:

- [ПРИ НЕОБХОДИМОСТИ] acl.json - укажите актуальные права для доступа к событиям
- [ОБЯЗАТЕЛЬНО] mapping.json - укажите целевые аудитории, занятия из которых будут обрабатываться приложением
- [ПРИ НЕОБХОДИМОСТИ] metadata.json - укажите умолчательные значения для целевых метаданных
- [ПРИ НЕОБХОДИМОСТИ] processing.json - укажите умолчательные значения для метода обработки записи
- [ПРИ НЕОБХОДИМОСТИ] schedulling.json - укажите умолчательные значения для способа планирования и выгрузки
- [ПРИ НЕОБХОДИМОСТИ] series_acl.json - укажите актуальные права для доступа к сериям
- [ПРИ НЕОБХОДИМОСТИ] metadata.json - укажите умолчательные значения для целевых метаданных серий

### .env-файл

    Для корректной работы приложения необходимо создать и заполнить .env-файл (положить в директорию OpencastAPI) по следующей схеме:
    - OPENCAST_API_URL= ссылка на Opencast
    - OPENCAST_API_USER= логин для приложения
    - OPENCAST_API_PASSWORD= пароль для приложения
    - OPENCAST_API_ROLE= роль для приложения
    - OPENCAST_WORKFLOW_ID= schedule-and-upload (способ постинга событий в Opencast, желательно не менять значение)
    - SCHEDULE_API_URL= ссылка для доступа к schedule-api-proxy
    - EVENT_BEGIN_OFFSET_SECONDS=-240 (5-минутный отступ до начала пары во избежания коллизий)
    - EVENT_END_OFFSET_SECONDS= 900 (15-минутный отступ от конца пары во избежания коллизий)
    - AUTHORIZATION= токен для доступа к schedule-api-proxy

### Развёртывание приложения и установка зависимостей

Для использования приложения необходимо загрузить его? затем развернуть приложение, создав виртуальное окружение и установив зависимости:

- git clone git@github.com:monticola145/Schedule-Proxy-Exporter.git
- python -m venv venv && source venv/Scripts/activate
- pip install -r requirements.txt

Готово! Приложение готово к запуску.

## Запуск приложения и принцип его работы

Для запуска приложения необходимо использовать следующую консольную команду:

```
python exporting_script.py
```
Поздравляем, Вы великолепны. Программа начала свою работу и её ничто не остановит...  кроме Вас?

### Принцип работы приложения

- Суть:
   1) Приложение получает информацию о занятиях из базы данных (далее - БД)
   2) Приложение сортирует и находит занятия, которые:
        а) Актуальны (т.е. - датируются сегодняшним днём)
        б) Проходят в заранее указанных аудиториях (см. пункт "Начало работы" - "Настройка приложения")
   3) Данная информация встраивается в шаблон метаданных, которые отсылаются в Opencast. Вуаля! Событие теперь отображается в Opencast.
   3.1) Приложение также находит/создаёт серию, в которую включает новоиспечённое событие
   4) Итерация заканчивается, скрипт ожидает следующей итерации

## Расписание

    В данной версии выставлено умолчательное расписания активации скрипта:
    - 09:25
    - 11:05
    - 12:45
    - 12:55
    - 14:35
    - 16:15
    - 17:55
    - 18:05
    - 20:00

    То есть скрипт активируется за 5 минут до начала пары и через 15 минут после её окончания
    
### Автор:

[Monticola]
Git - https://github.com/monticola
Email - ```jandiev2001@yandex.ru```



    # schedule-proxy-exporter

## About the app

This application is aimed at exporting pairs and classes from RUZ to Opencast

## Getting started
### Setting up the application

The following files in the OpencastAPI folder need to be modified in order to function:

- [MUST] acl.json - specify actual rights for access to events
- [MUST] mapping.json - specify target audience from which classes will be processed by the application
- [MUST] metadata.json - specify default values for target metadata
- [IF REQUIRED] processing.json - specify default values for record processing method
- [IF REQUIRED] scheduling.json - specify default values for scheduling and uploading method
- [IF REQUIRED] series_acl.json - specify actual rights for access to series
- [IF REQUIRED] metadata.json - specify the default values for the target series metadata

### .env file

    In order for the application to work correctly you need to create and fill in the .env file (put it in the OpencastAPI directory) according to the following scheme:
    - OPENCAST_API_URL= link to Opencast
    - OPENCAST_API_USER= login for the application
    - OPENCAST_API_PASSWORD= password for the application
    - OPENCAST_API_ROLE= role for the application
    - OPENCAST_WORKFLOW_ID= schedule-and-upload (how events are posted to Opencast, preferably not to change the value)
    - SCHEDULE_API_URL= the link to access schedule-api-proxy
    - EVENT_BEGIN_OFFSET_SECONDS=-240 (5 minutes indent to the beginning of the pair to avoid collisions)
    - EVENT_END_OFFSET_SECONDS=900 (15-minute indent from the end of the pair to avoid collisions)
    - AUTHORIZATION= token for access to schedule-api-proxy

### Deployment of the application and installation of dependencies

To use an application, you have to download it, then deploy it by creating a virtual environment and installing dependencies:

- git clone git@github.com:monticola145/Schedule-Proxy-Exporter.git
- python -m venv venv && source venv/Scripts/activate
- pip install -r requirements.txt

It's done! The app is now ready to run.

## Launching the application and how it works

You need to use the following console command to run the application:

```
python exporting_script.py
```
Congratulations, you are great. The program has started and nothing can stop it... except you?

### Principle of the application

- Bottom line:
   1) The application retrieves information about classes from the database (hereinafter referred to as the database)
   2) The application sorts and finds classes that are:
        a) Relevant (i.e. - dated today)
        b. take place in previously specified classrooms (see "Getting Started" - "Setting up the Application")
   3) This information is embedded in a metadata template that is sent to Opencast. Voila! The event is now displayed in Opencast.
   3.1) The application also finds/creates a series that includes the newly created event
   4) Iteration ends, the script waits for the next iteration

## Schedule

    This version has the default schedule for activating the script:
    - 09:25
    - 11:05
    - 12:45
    - 12:55
    - 14:35
    - 16:15
    - 17:55
    - 18:05
    - 20:00

    That is, the script is activated 5 minutes before the start of the pair and 15 minutes after the end of the pair
    
### Author:

[Monticola]
Git - https://github.com/monticola
Email - ``jandiev2001@yandex.ru``

