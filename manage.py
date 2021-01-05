#coding:utf8
from app import create_app
from app import app_url

app = create_app()

if __name__ == "__main__":
    app.run(host=app_url)

