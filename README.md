# About

This project is being developed as a site for the sale of digital products - reservation of seats in bus or car trips in Portugal.
Under development still...

# Installation

## Development mode
### Linux
This project uses PostGis extension for Postgresql DB because you should install
[GDAL libraries](https://docs.djangoproject.com/en/5.0/ref/contrib/gis/gdal/) to your local machine, for Linux example:
```
sudo apt-get install binutils libproj-dev gdal-bin
```

And for using django-extensions lib:
```
sudo apt-get install graphviz graphviz-dev
```

### macOS
We recommend installing Graphviz using the Homebrew package manager or MacPorts for macOS.

```
brew install graphviz
pip install pygraphviz
```
Graphviz may be installed in a location that is not on the default search path. In this case, it may be necessary to manually specify 
the path to the graphviz include and/or library directories, e.g.

[PyGraphviz docs](https://pygraphviz.github.io/documentation/stable/install.html)
```
pip install --config-settings="--global-option=build_ext" \
            --config-settings="--global-option=-I$(brew --prefix graphviz)/include/" \
            --config-settings="--global-option=-L$(brew --prefix graphviz)/lib/" \
            pygraphviz
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
To check coverage of codebase run:
```
coverage run manage.py test
coverage report -m
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

You can update the site on the server both manually and through an automatic tunnel for Continuous Integration and 
Continuous Development (CI/CD) on the GitHub repository.
### Description CI/CD
When the GitHub Actions service is enabled, the site is automatically updated after a Pull Request to the main master branch. 
All settings are in the file:
*.github/workflows/docker-image.yml*
The flow is set up to run all the tests that exist, then build the Docker image.
The Docker image is pushed to the Docker repository.
Then login to the server with the permissions specified in GitHub secrets. 
From there, a new Docker image is pulled from the Docker hub, the old container is stopped and deleted. 
A new container launched based on the new Docker image.
### Manual deployment
On the local machine side:

```
# Go to production branch with latest and tested changes, for example: develop
git checkout develop
# get out rom virtual environment if you here:
deactivate 
# Create a new docker image
docker build -t portotours/portotours:latest .
# push new docker image to the certain Docker hub:
docker push portotours/portotours:latest
```

Then go to the server and update site there:
```
ssh root@164.90.217.249
docker pull portotours/portotours:latest
docker ps -a
docker stop django-portotours 
docker rm django-portotours 
docker run -d --name django-portotours -p 8000:8000 portotours/portotours:latest 
docker ps -a
systemctl reload nginx
systemctl status nginx.service 
docker images
docker image rm   <your-old-docker-image-ID> 
docker ps -a
exit
```

## Dump DB and recovery DB
Cron and a file `backup_db.sh` are used to automatically receive a database dump and send it to email. On the server the file lives here: `/etc/backup_django`.
To recovery DB from dump you can use the file `recovery_db.sh` that is in same place on the server.
In project there saved copies in directory `cron_services`.

You can use commands to exchange files through ssh like this:
```
scp cron_services/backup_db.sh root@164.90.217.249:/etc/backup_django
```
