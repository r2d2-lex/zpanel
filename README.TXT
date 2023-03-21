В процессе...

1. Postgres create database:
create database zpanel;
CREATE USER zpanel WITH PASSWORD 'zpanel';
GRANT ALL PRIVILEGES ON DATABASE "zpanel" to zpanel;

2. Create database
python db.py
    with Database() as db:
        db.create_db()
