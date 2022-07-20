# Installation and launch

**Installation**

You can clone this application:

```bash 
git clone https://github.com/Blastz13/chat_fastapi.git
```

Next, you need to install the necessary libraries:

```bash
poetry install
poetry update
```
You need to set variables in the environment: 

`JWT_SECRET` — Secret JWT key

`JWT_ALGORITHM` — Encryption algorithm method

`DB_USER` — Database username

`DB_PASSWORD` — Database password

`DB_HOST` — Database host

`DB_PORT` — Database port

`DB_NAME` — Database name

**Launch**

Change directory from web app, create and apply migrations:

```bash
cd chat_fastapi
alembic revision --autogenerate -m 'Initial'
alembic upgrade head
```

Now you can start the server:

```bash
uvicorn main:app --reload
```

### License

Copyright © 2021 [Blastz13](https://github.com/Blastz13/).