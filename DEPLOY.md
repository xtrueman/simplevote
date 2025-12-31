# Инструкция по развертыванию SimpleVote

## Предварительные требования

- Ubuntu/Debian сервер
- Python 3.8+
- Nginx
- Права sudo

## Шаг 1: Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install -y python3 python3-pip python3-venv nginx
```

## Шаг 2: Развертывание приложения

```bash
# Создание директории
sudo mkdir -p /srv/simplevote
sudo chown $USER:$USER /srv/simplevote

# Клонирование/копирование файлов проекта
cd /srv/simplevote
# Скопируйте все файлы проекта в /srv/simplevote

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

## Шаг 3: Настройка systemd сервиса

```bash
# Копирование service файла
sudo cp /srv/simplevote/simplevote.service /etc/systemd/system/

# Перезагрузка systemd
sudo systemctl daemon-reload

# Запуск сервиса
sudo systemctl start simplevote

# Проверка статуса
sudo systemctl status simplevote

# Автозапуск при старте системы
sudo systemctl enable simplevote
```

## Шаг 4: Настройка Nginx

```bash
# Копирование конфигурации
sudo cp /srv/simplevote/simplevote.conf /etc/nginx/sites-available/

# Создание символической ссылки
sudo ln -s /etc/nginx/sites-available/simplevote.conf /etc/nginx/sites-enabled/

# Удаление дефолтного сайта (опционально)
sudo rm /etc/nginx/sites-enabled/default

# Проверка конфигурации
sudo nginx -t

# Перезапуск Nginx
sudo systemctl restart nginx

# Автозапуск Nginx
sudo systemctl enable nginx
```

## Шаг 5: Настройка DNS

Добавьте A-запись для домена `vote.llmtech.ru`, указывающую на IP вашего сервера.

## Шаг 6: Настройка HTTPS (опционально, но рекомендуется)

```bash
# Установка Certbot
sudo apt install -y certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d vote.llmtech.ru

# Автоматическое обновление сертификата
sudo systemctl enable certbot.timer
```

## Проверка работы

- Главная страница: http://vote.llmtech.ru/
- Админка: http://vote.llmtech.ru/admin.html
- API документация: http://vote.llmtech.ru/api/docs
- ReDoc: http://vote.llmtech.ru/api/redoc

## Управление сервисом

```bash
# Просмотр логов
sudo journalctl -u simplevote -f

# Остановка сервиса
sudo systemctl stop simplevote

# Перезапуск сервиса
sudo systemctl restart simplevote

# Проверка статуса
sudo systemctl status simplevote
```

## Обновление приложения

```bash
# Переход в директорию проекта
cd /srv/simplevote

# Активация виртуального окружения
source venv/bin/activate

# Обновление кода (git pull или копирование новых файлов)

# Обновление зависимостей (если изменились)
pip install -r requirements.txt

# Перезапуск сервиса
sudo systemctl restart simplevote
```

## Устранение проблем

### Сервис не запускается

```bash
# Проверка логов
sudo journalctl -u simplevote -n 50 --no-pager

# Проверка прав доступа
sudo chown -R www-data:www-data /srv/simplevote
sudo chmod -R 755 /srv/simplevote
```

### Nginx показывает 502 Bad Gateway

```bash
# Проверка, что FastAPI сервис запущен
sudo systemctl status simplevote

# Проверка, что порт 8000 прослушивается
sudo netstat -tlnp | grep 8000
```

### Логи Nginx

```bash
# Access log
sudo tail -f /var/log/nginx/simplevote_access.log

# Error log
sudo tail -f /var/log/nginx/simplevote_error.log
```

## Настройка файрвола (опционально)

```bash
# Если используется ufw
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

## Резервное копирование

Поскольку приложение хранит данные в памяти, они теряются при перезапуске. Если требуется сохранение данных между перезапусками, необходимо модифицировать код для использования базы данных.
