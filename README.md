# Django-Backend 2025
A generic Django backend providing structured, RESTful API access to multiple frontend clients. mikejin

## Development Environment Setup
Create a python virtual environment. Here it is named `.venv` and is placed in the root folder. You can place it anywhere you'd like and name it whatever you'd like.
```sh
python3 -m venv .venv
```
Activate the virtual environment. Replace `.venv` with `path-to-your-venv`. If other systems are used or any errors encountered, refer to the [official python venv page](https://docs.python.org/3/library/venv.html)
```sh
source .venv/bin/activate
```
Install dependencies listed in `requirements.txt`.
```sh
pip install -r requirements.txt
```
Create database migrations
```sh
python3 manage.py makemigrations
python3 manage.py migrate
```
Run development server
```sh
python3 manage.py runserver
```

## IMPORTANT!!!
If you added other packages, do not forget to add them to `requirements.txt`
```sh
pip freeze > requirements.txt
```
Please also remember to update `devlog.md` where you document the development process. If there are design decisions, put them in `README.md`