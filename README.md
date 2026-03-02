# Hospital Smart Assistant

[![codecov](https://codecov.io/gh/nashta-csui/hospital-smart-assistant/graph/badge.svg)](https://codecov.io/gh/secona/hospital-smart-assistant)

## Mengenai ORM dan Database (untuk developer)

ORM yang digunakan pada proyek ini adalah SQLAlchemy dengan
[ORM deklaratif](https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html).
Untuk menjalankan migrasi dan version control schema database, proyek ini
menggunakan [Alembic](https://alembic.sqlalchemy.org/en/latest/).

Database yang digunakan adalah PostgreSQL dengan plugin `pgvector`. Pada proyek
ini, kami menggunakan container pgvector/pgvector, yakni wrapper container
PostgreSQL yang sudah dipasangkan extension pgvector.

Salah satu cara untuk menjalankan database untuk development lokal adalah dengan
menggunakan Docker. Jalankan perintah berikut untuk pull image pgvector/pgvector
lalu menjalankannya secara lokal:

```bash
docker pull pgvector/pgvector:0.8.2-pg18-trixie

docker run -p 5432:5432 -e POSTGRES_PASSWORD=<password> -e POSTGRES_USER=<username> -e POSTGRES_DB=smart-hospital pgvector/pgvector:0.8.2-pg18-trixie
```

> Untuk kemudahan development, gunakan nilai POSTGRES_PASSWORD dan POSTGRES_USER
> yang sederhana saja. Untuk deployment ke staging dan prod, nilai-nilai ini
> akan di-inject lewat script CD.

Kemudian, untuk menyalakan extension pgvector, jalankan perintah berikut pada
database menggunakan sebuah client PostgreSQL(psql, DBeaver, DbVisualizer,
dll.):

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Berikut adalah contoh command yang dijalankan apabila menggunakan psql:

```bash
psql -U root -h 127.0.0.1 -d smart-hospital -c "CREATE EXTENSION IF NOT EXISTS vector;"

# atau, menggunakan file init.sql pada proyek...

psql -U root -h 127.0.0.1 -d smart-hospital -f init.sql
```
