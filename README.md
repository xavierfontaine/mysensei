# MySensei
## Installation
1. Install postgreSQL
```bash
sudo apt install postgresql-14
```
#2. Create the database and admin db user as the 'postgres' shell user (`sudo -u postgres -i`)
#```bash
#createdb -O postgres mysenseidb
#```
3. Create the admin user as the 'postgres' user, **replacing** 'mypassword' with
the appropriate one.

First assume the role of the 'postgres' shell user:
```bash
sudo -u postgres -i
```
Then use the terminal-based front-end to PostgreSQL to create the db and the admin:
```bash
psql
CREATE DATABASE mysenseidb;
CREATE USER admin WITH ENCRYPTED PASSWORD 'mypassword';
GRANT ALL PRIVILEGES ON DATABASE mysenseidb TO admin;
\q
```

## Design decisions
### Database
Most requests will combine a user id and some object id for identification. for
that reason, composite PK might be a good idea. Especially since requests on the
first column of the PK are pretty much as fast as if only that first column
was indexed (see [SO](https://stackoverflow.com/a/11352543)).

Some requests will require to combine two tables, but in general it will be for
matching notes and cards. Thus, junction tables will be quite rare.


Request typology:
* Full client-side retrieval: if the browser cache is empty, get back the cache
* Partial client-side retrieval: if my mechanism to check that the client's
  cache is up-to-date.
* Edition: based on the user id and some id on the object, modify the object.
* Match note and card: one of the few operations that requires correpsondance
  tables.
