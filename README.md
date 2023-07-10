# Introduction
FastAPI + JWT + SQLAlchemy + SQLite(or Postgres) demo.
The code follows the official document of [FastAPI OAuth2 JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/).


# Run Locally
1. Clone the repo

2. Create virtual env and activate

3. Install python packages in `requirements.txt`

4. Start FastAPI app locally
    ```bash
    (venv) $ uvicorn main:app --reload
    ```
5. visit http://localhost:8000/docs

6. If running the app for the first time, the *users* table in the database is empty. To be able to login and use the API, you can send a **POST** request to endpoint:
 http://localhost:8000/users/init with an empty body. This will create the default superuser defined in *./configurations.py*.

   
# Test
FastAPI has a built-in **TestClient** class which is based on *pytest* and *requests*, this makes it very easy to write tests.
To run all test cases: 
```bash
(venv) $ pytest
```
This will create a test database named *fastapi_app_test.db* at the beginning of the test, run all test cases, then remove the database file after finishing the last test case. 
