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
To create superuser:
```
python manage.py createsuperuser
```
### Loading fixtures
```
python manage.py loaddata --format json products/fixtures/*
```

### Run project:
```
python manage.py runserver
```

### Celery
```
celery -A portotours worker -l INFO --beat --scheduler django
```
### Flower
```
celery -A portotours flower -l INFO
```


***and open in browser ->*** [http://localhost:8000/](http://localhost:8000/)

### Tests
```
python3 manage.py test --verbosity=2 --keepdb
```
## Production mode

#### The cloud used for production deployment: 
[Digital Ocean Docs](https://docs.digitalocean.com/products/)

