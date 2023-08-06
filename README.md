# FastAPI JWT Demo

<!-- markdownlint-disable -->
[![lint](https://github.com/Redevil10/fastapi-jwt/actions/workflows/lint.yaml/badge.svg)](https://github.com/Redevil10/fastapi-jwt/actions/workflows/lint.yaml)
[![test](https://github.com/Redevil10/fastapi-jwt/actions/workflows/test.yaml/badge.svg)](https://github.com/Redevil10/fastapi-jwt/actions/workflows/test.yaml)
[![coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/Redevil10/426778eefb0a2907ee258ec5ff7c5960/raw/covbadge.json)](https://github.com/Redevil10/fastapi-jwt/actions/workflows/test.yaml)
[![python](https://img.shields.io/badge/python-3.10%20%7C%20_3.11-blue)](https://github.com/Redevil10/fastapi-jwt/actions/workflows/test.yaml)
<!-- markdownlint-restore -->

## Introduction
FastAPI + JWT + SQLAlchemy + SQLite(or Postgres) demo.
The code follows the official document of [FastAPI OAuth2 JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/).


## Run Locally
1. Clone the repository

2. Create virtual env and activate
   ```bash
   $ pyenv shell 3.11
   $ python -m venv venv
   $ source venv/bin/activate
   (venv) $ pip install -U pip
   ```
3. Install poetry and dependencies
   ```bash
   (venv) $ pip install poetry
   (venv) $ poetry install
   ```
4. Start FastAPI app locally
    ```bash
    (venv) $ uvicorn main:app --reload
    ```
5. Visit `http://localhost:8000/docs`

6. If running the app for the first time, the *users* table in the database is empty. To be able to log in and use the API, you can send a **POST** request to endpoint:
 `http://localhost:8000/users/init` with an empty body. This will create the default superuser defined in *./config.py*.


## Test
FastAPI has a built-in **TestClient** class which is based on *pytest* and *requests*, this makes it very easy to write tests.
To run all test cases:
```bash
(venv) $ pytest
```
This will create a test database named *fastapi_app_test.db* at the beginning of the test, run all test cases, then remove the database file after finishing the last test case.
