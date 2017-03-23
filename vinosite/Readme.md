Website catalog for Vino


Environment Installation
============

The web project relies on the Django framework (python). The easiest way to install this application is to use Docker, see the Readme file in upper directory.

If you want to deploy the webserver but won't/can't use Docker, follow these instructions:
 - install h5py and numpy within your python distribution (Anaconda under windows for example). These two packages needs binary libraries that can cause trouble if you try to build them with `pip`
 - install the required libraries, inside a virtual environnement (`virtualenv` or Anaconda environment), by running:
 ```
 pip install -r vino-py/pip-requires.txt
 pip install -r vinosite/pip-requires.txt
 ```
 - Under Windows, you have to install the package 'sqlite' with Anaconda
 - Go into the folder `vinosite`
 - Copy the config file `vinosite/local_settings.py.dist` to `vinosite/local_settings.py`.
 - Initialize the database by running:
 ``` 
 python manage.py makemigrations sharekernel
 python manage.py migrate
 ```
 - Start the server with the cammand: `python manage.py runserver`

Initialisation
==============
You can create the superuser account with this command:
```
python manage.py createsuperuser
```
Then, you will be able to log in to the administration backend through the URL http://localhost:8000/admin

You can populate the database with the sample data provided in samples directory (from the parent directory) with this command:
```
python manage.py populate_database
```

Run
===
For running the test server:
`python manage.py runserver`

See also this [django tutorial](https://docs.djangoproject.com/en/1.8/intro/tutorial01/) for basics on managing django application.
