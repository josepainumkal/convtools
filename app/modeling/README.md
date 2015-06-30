# PRMS Converter

In order for PRMS data to be interoperable with the rest of the Virtual Watershed (VW) 
ecosystem, we need to be able to convert to NetCDF format, the reference data format 
of the VW. To do this we've developed the PRMS adaptors as an element of the growing 
suite of VW adaptors.

This adaptor works in Ubuntu 14.04 LTS Operating System.

- Sharing and organizing datasets either produced by or useful to a watershed
  hydrologist using the Virtual Watershed Data Engine, powered by GSToRE
- Running hydrological models on data that either a scientist or others others have shared
- Connect datasets to CI-Vis's 3D immersive visualizations
- Create or view other visualizations
- Socialize: follow other scientists contributions

This documentation is mainly for developers, but it's also 
for anyone who wants to test the Virtual Watershed Platform or run a VWP
locally.

# Quickstart

### Get code, start dev server

The first step is to clone this repository

```bash
git clone https://github.com/mtpain/vwplatform.git 
```

and grab the [wcwave_adaptors]() submodule from the vwplatform directory

```bash
cd vwplatform && git submodule update --init
```

To run the web app locally for development, first start up and activate a virtual
environment, then install the requirements.

```bash
virtualenv venv && source venv/bin/activate && pip install -r requirements.txt
```

You will also need to add your userid (email) and password to default.conf, which you'll copy from `wcwave_adaptors/default.conf.template`.
Be careful not to sync your personalized `default.conf`, since this will expose your credentials to the world.

From the root directory of the repository

```bash
cp wcwave_adaptors/default.conf.template default.conf
```

then edit `default.conf`. If you need a Virtual Watershed account, please email maturner@uidaho.edu.

Then launch the web app

```bash
$ python manage.py runserver
```

and view it at http://localhost:5000 in your web browser.

### Initialize Databases

That's great, but if you try to create users or contribute resources, you will
run into an error because no databases have been created. To do this, we use
[flask-migrate](https://flask-migrate.readthedocs.org/en/latest/). 

First, create a `migrate` directory which will read information about the
databases (as represented in `app/models.py`)

```bash
python manage.py db init
```

Then, create a script in the `migrate/versions` directory that will handle
creating the database and tables for this version of the
'upgrade'/initialization

```bash
python manage.py db migrate -m"initialize db"
```

The `-m` flag gives a migration message that is copied (spaces removed) to be
part of the name of the migration script in `migration/versions`. 

Finally, to create the database and `user` and `resource` tables, 

```bash
python manage.py db upgrade
```

Now you can start up sqlite and check that the database and tables have been
created

```bash
sqlite3 data-dev.sqlite
```

and in the sqlite shell

```sql
sqlite> .tables
alembic_version  resource         users
```

Now you can create users and resources through the app and see the results in
the database

```sql
SELECT * FROM resource;
```

and

```sql
SELECT * FROM users;
```

This is enabled by the following lines in `manage.py`:

```python
...
from flask.ext.migrate import Migrate, MigrateCommand
...
migrate = Migrate(app, db)
...
manager.add_command('db', MigrateCommand)
```

# Structure

A Flask app can take many forms, but the documentation does [suggest a helpful
way to structure larger
applications](http://flask.pocoo.org/docs/0.10/patterns/packages/). The VW
Platform follows these recommendations pretty closely. For example, our 
style sheets are in `app/static/`, our models are in `app/models.py`, and
currently we have three
[Blueprint](http://flask.pocoo.org/docs/0.10/blueprints/) directories,
`app/main`, `app/auth`, and `app/share`, for the main views including search,
authentication and user registration, and sharing data. Our templates live in
`app/templates`, and all non-main blueprint templates live in their own
subdirectories of `app/templates`.

To get a better idea of how Flask lets us put all this together, check out 
[app/__init__.py](https://github.com/mtpain/vwplatform/blob/master/app/__init__.py)
and [manage.py](https://github.com/mtpain/vwplatform/blob/master/manage.py).
`app/__init__.py` contains initializations of the Flask extensions (Mail,
Moment, SQLAlchemy) used in the app. It also "registers" blueprints and their
prefix. Thus, when someone wants to log in the URL is `/auth/login` and when
a user creates an account they do so at `/auth/register`.

The blueprints are connected to the app in the `create_app` in 
`app/__init__.py`. This is also where Flask extensions are connected to the app.
For example, [flask-login](https://flask-login.readthedocs.org/en/latest/) is
connected and creates a login manager in the call `login_manager =
LoginManager()`. `manage.py` imports and calls `create_app`, as well as
handles different app startup procedures. In addition to `runserver` which was
demonstrated above, there are `db` and `shell`, assigned before the 
`if __name__ == '__main__':` statement in `manage.py`. 


# Extending the VW Platform web app

## Unity Visualizations

We plan on extending this app in a multitude of ways. One of the first is to
integrate Chase and the CI-Vis team's immersive visualization. To do that, we'll
have to add some sort of field to our metadata records that points to the
location where the visualization server can be found. Currently there is only
one model for data, and that is a high-level model called a `Resource`. Very
soon we'll also have a `File` model, where each Resource may have multiple
files, but each File belongs to only one resource. In Flask, data models are
represented as classes. See `app/models.py` for the VW Platform models.

I'd imagine that `Resource` would show it's vis-enabled if at least one of its
`File`'s were. So on that front, let's start there.

## Model runs

There is some interest in being able to run models and modify input data then
run models through our web interface. For that we'd likely create a new
blueprint, `modeling` let's say. 

## Live-streaming data

Joel at ISU is interested in integrating his streaming data as well as his
service to convert georaster data to iSNOBAL inputs. We need to be thinking
about how to integrate not just streaming data, but also enable researchers to
publish their own web services through our platform, or if that's not
appropriate, provide documentation on how to do that.
