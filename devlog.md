started the python virtual environment
```
python3 -m venv .venv
source .venv/bin/activate
```

installed project dependency packages
```
pip install Django
pip install djangorestframework
pip install django-filter
pip install drf-spectacular
pip freeze > requirements.txt
```

created django directories and files
```
django-admin startproject core .
python3 manage.py startapp api

mkdir api/v1
mv api/views.py api/v1/views.py
touch api/v1/__init__.py api/v1/urls.py api/v1/serializers.py api/v1/permissions.py api/v1/filters.py
```

added `rest_framework`, `drf_spectacular` and related settings to `core/settings.py`

```py
INSTALLED_APPS = [
  ...
  'rest_framework',
  'drf_spectacular',
]

REST_FRAMEWORK = {
  # YOUR SETTINGS
  'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
  'TITLE': 'Project API',
  'DESCRIPTION': 'A generic Django backend providing structured, RESTful API access to multiple frontend clients.',
  'VERSION': '1.0.0',
  # OTHER SETTINGS
}

```

added pandas and openpyxl
```sh
pip install pandas
pip install openpyxl
```

added seed.py to /api (not functional yet)
modified models.py in /api