## Postgresql

We use the SQLAlchemy Database Toolkit as ORM and Alembic as database migration tool. To make changes to the Postgresql database, edit the data models in `postgresql/models.py`. Port-forward the Postgresql Pod to port 5000 and run `make make-migrations` to generate a migration script in `alembic/versions/`. Run `make migrate` to apply it. To access Postgresql from the command line, use `psql -p 5432 -h localhost -U user -d postgres` with password `password` and run for example `\dt` to show all tables.
