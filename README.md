# hhSearcher
## О программе
**hhSearcher** - это личный telegram-bot предназначеный для просмотра вакансий с сайта _hh.ru_ по определённым критериям. 
Основная его задача состоит в возможности мониторить вакансии определённых направлений в обход приложения _hh_.
## Требования
**ОС:** *nix подобная

**Python:** 3.11 (можно ниже, но тогда нужно будет удалить аннотацию типов)
## Установка
### Подготовка
Заходим в telegram находим bot-а BotFather создаём своего бота и подключаем токен для его работы.
### Техническая часть

Скачиваем проект: \
`git clone https://github.com/StickKing/hhSearcher` 

Производим установку всех необходимых пакетов: \
`pip install -r requirement.txt`

Заходим в файл **settings.py** указываем абсолютный путь к БД, токен и тип опыта работы по которому будет производиться поиск.
Далее запускае файл **models.py** произойдёт создание БД и нескольких категорий вакансий (которые далее можно будет удалить).


Для регулярного пополнения БД вакансиями используется **get_all_vacancy.py**, для его непрерывной работы необходимо
зайти в файл **/etc/crontab** любым редактором (nano, vi и т.д.) и добавить в конец следующую строку: \
`*/5 *  * * *   root    <pyhton path>/python3.11 <script path>/get_all_vacancy.py 2> <errors path>/errors.txt`

_pyhton path_ - это абсолютный путь к python. Если вы используете Debian 11 то создайте venv и укажите путь к **venv/bin/python**.

_script path_ - это абсолютный путь к папке с данным проектом где лежит исполняемый файл.

_errors path_ - это абсолютный путь к текстовомц файлу куда будет перенаправляться вывод скрипта.

Теперь необходимо создать службу нашего бота. Создаём файл по следующему пути /etc/systemd/system/hh.service \
```
[Unit]
Description=TelegramBot
After=multi-user.target

[Service]
User=your user
Group=root
Type=simple
Restart=always
ExecStart=<pyhton path>/python3.11 <script path>/main.py

[Install]
WantedBy=multi-user.target
```
В нём так же указываем _pyhton path_ и _script path_ описанные выше. 

Сохраняем файл и производим: 
`systemctl daemon-reload` \
Затем:
`systemctl start hh.service`


Бот запущем можно пользоваться его возможностями.
