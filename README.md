# Stamp-dashboard
Простая система для регистрации отслеживания заявлений акцизных марок.


# Инструкция по установке на Ubuntu

## Установка и настройка Redis

Установите требуемые пакеты:
```sh
sudo apt-get update
sudo apt-get install python3-pip python3-dev build-essential tcl
```

Скачайте и распакуйте Redis:
```sh
wget http://download.redis.io/redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
cd redis-stable
```

Далее выполните команду make:
```sh
make
```

Проведите тест сборки:
```sh
make test
```

Установите бинарники в систему:
```sh
sudo make install
```

Создайте папку с настройками
```sh
sudo mkdir /etc/redis
```

Скопируйте настройки по умолчанию:
```sh
sudo cp /tmp/redis-stable/redis.conf /etc/redis
```

В файле с настройками найдите строку `supervised no` и измените её на:
```sh
supervised systemd
```

Измените строку с `dir` на:
```sh
dir /var/lib/redis
```

Создайте новый юнит systemd:
```sh
sudo nano /etc/systemd/system/redis.service
```

Добавьте в файл следующие строки:
```
[Unit]
Description=Redis In-Memory Data Store
After=network.target

[Service]
User=redis
Group=redis
ExecStart=/usr/local/bin/redis-server /etc/redis/redis.conf
ExecStop=/usr/local/bin/redis-cli shutdown
Restart=always

[Install]
WantedBy=multi-user.target
```


Добавьте нового пользователя и группу:
```sh
sudo adduser --system --group --no-create-home redis
```

Создайте папку и нстройте доступ:
```sh
sudo mkdir /var/lib/redis
sudo chown redis:redis /var/lib/redis
sudo chmod 770 /var/lib/redis
```

Запустите Redis и включите автоматический запуск при загрузке системы:
```sh
sudo systemctl start redis
sudo systemctl enable redis
```


## Установка основной системы
Скачайте проект:
```sh
git clone https://github.com/dpanin/stamp-dashboard.git
```

После скачивание зайдите внутрь директории stamp-dashboard:
```sh
cd stamp-dashboard
```

Создайте виртуальное окружение в папке venv:
```sh
python3 -m venv venv/
```

Активируйте виртуальное окружение:
```sh
. venv/bin/activate
```

Установите требуемые пакеты для python:
```sh
pip install -r requirements.txt
```

Создайте новую базу данных, указав логин, почту, пароль и номер должности нового пользователя через пробел:
```sh
python setup_db.py [логин] [почта] [пароль] [номер должности]
```

Откройте порт 5000:
```sh
ufw allow 5000
```

Создайте новый юнит systemd:
```sh
sudo nano /etc/systemd/system/stamp-dashboard.service
```

Внутри задайте следующие настройки, задав имя пользователя и путь к папке:
```
[Unit]
Description=Gunicorn instance to serve stamp-dashboard
After=network.target

[Service]
User=[имя пользоватля]
Group=www-data
WorkingDirectory=/путь/к/папке/stamp-dashboard
Environment="PATH=/путь/к/папке/stamp=dashboard/venv/bin"
ExecStart=/путь/к/папке/stamp=dashboard/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 wsgi:app

[Install]
WantedBy=multi-user.target
```

Запустите Gunicorn службу и включите автоматический запуск при загрузке системы:
 ```
sudo systemctl start myproject
sudo systemctl enable myproject
```

Готово!
