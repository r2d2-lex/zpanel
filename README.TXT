1. Postgres create database:
create database zpanel;
CREATE USER zpanel WITH PASSWORD 'zpanel';
GRANT ALL PRIVILEGES ON DATABASE "zpanel" to zpanel;

2. Create database
python db.py
    with Database() as db:
        db.create_db()

3. sudo apt install virtualenv python3-venv

4. cd /%root%/
example root dir: cd /var/www
git clone git clone https://github.com/r2d2-lex/zpanel.git

4. cd /%root%/zpanel
python3 -m venv venv

5. source ./venv/bin/activate

6. pip install -r requirements.txt
6.1 Может понадобится: apt-get install --reinstall libpq-dev

7. Создайте конфиг и установите нужные переменные:
cd /%root%/zpanel/
cp config-example.py config.py

8. Установите gunicorn
pip install gunicorn
8.1 Test: gunicorn --bind 0.0.0.0:8000 main:app -k uvicorn.workers.UvicornWorker
8.2 Copy service/zpanel.service: cp service/zpanel.service /etc/systemd/system/zpanel.service

9. Запустите сервис:
$ sudo systemctl start zpanel.service
$ sudo systemctl enable zpanel.service

9.1 Проверьте состояние работы сервиса:
$ sudo systemctl status zpanel.service

10. Скопируйте из service/nginx/zpanel в /etc/nginx/sites-available
10.1 ln -s /etc/nginx/sites-available/zpanel /etc/nginx/sites-enabled/
10.2 nginx -t
10.3 systemctl reload nginx
