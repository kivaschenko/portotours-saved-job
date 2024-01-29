# About

This project is being developed as a site for the sale of digital products - reservation of seats in bus or car trips in Portugal.
Under development still...

# Installation

## Development mode
This project uses PostGis extension for Postgresql DB because you should install
[GDAL libraries](https://docs.djangoproject.com/en/5.0/ref/contrib/gis/gdal/) to your local machine, for Linux example:
```
sudo apt-get install binutils libproj-dev gdal-bin
```

Go to root directory:
```
cd portotours
```

Copy sample of `.env` file and set your variables:
```
cp sample-env .env
```

Create virtual environment:
```
python3 -m venv env
```

Run environment: 
```
source env/bin/activate
```

Install all dependencies:
```
pip install --upgrade pip setuptools
pip install -r requirements.txt
```
Run migrations if new DB:
```
python manage.py migrate
```

To create superuser:
```
python manage.py createsuperuser
```
### Loading fixtures
```
python manage.py loaddata --format json products/fixtures/*
python manage.py loaddata --format=json products/fixtures/prod/languages.json
```

### Run project:
```
python manage.py runserver
```

### Celery

not implemented yet, coming soon...
```
celery -A portotours worker -l INFO --beat --scheduler django
```
### Flower
not implemented yet, coming soon...
```
celery -A portotours flower -l INFO
```


***and open in browser ->*** [http://localhost:8000/](http://localhost:8000/)

### Tests
```
python3 manage.py test --verbosity=2 --keepdb
```
#### Test credentials Django dashboard:
- before upload fixtures: `python manage.py loaddata accounts/fixtures/testing/users.json`

- Test admin
  - Admin email (username): `dev@example.com`
  - Admin password: `112358`

- Test customer
  - email: `customer@example.com`
  - password: `$0me$eecret`
  
### CSS, style Sass, Bootstrap 5
There are using `django-sass-processor` to compile `.scss` files.
Custom CSS file lives in `static/custom_css/custom.scss`.
If you have update some changes (added new .scss ) then run:
```
./manage.py compilescss
./manage.py collectstatic
```
within your (venv) command line interface.
[According Django Sass Processor docs.](https://github.com/jrief/django-sass-processor)

## Production mode

#### The cloud used for production deployment: 
[Digital Ocean Docs](https://docs.digitalocean.com/products/)

