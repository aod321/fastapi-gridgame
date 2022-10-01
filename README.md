# fastapi-gridgame
A backend for gridgame using FastApi, SQLAlchemy, MySQL, and Jinja2 Templates

Basic Requirements:

Python 3.9.4 (installed with updated pip)

fastapi --> pip install fastapi

uvicorn --> pip install uvicorn[standard]

sqlalchemy --> pip install sqlalchemy

jinja2 --> pip install jinja2

pymysql --> pip install pymysql

mysql --> pip install mysql

After all the pre-requisites are installed, use this command (with administrator rights) to run the application:

cd fastapi-gridgame

uvicorn sql_app.main:app --reload

To see docs, write: http://127.0.0.1:8000/docs







