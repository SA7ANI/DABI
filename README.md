# LORD DABI Bot

[![DeepSource](https://static.deepsource.io/deepsource-badge-light-mini.svg)](https://deepsource.io/gh/SA7ANI/DABI/?ref=repository-badge)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/223b5710f2fa41d58775094ee65b6957)](https://app.codacy.com/gh/SA7ANI/DABI?utm_source=github.com&utm_medium=referral&utm_content=SA7ANI/DABI&utm_campaign=Badge_Grade)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

![Banner](https://telegra.ph/file/65a5109e77991ff84d665.jpg)

A modular telegram Python bot running on python3 with an sqlalchemy database.

Originally a simple group management bot with multiple admin features, it has evolved, becoming extremely modular and 
simple to use. Note that this project uses well-known Telegram-bot of it's time @BanhammerMarie_bot from Paul Larson as it's base.

Can be found on telegram as [DABI](https://t.me/LordDabiBot).

<details>
  <summary>Installation</summary>

## Starting the bot

Once you've setup your database and your configuration (see below) is complete, simply run:

`python3 -m dabi`

## Setting up the bot (Read this before trying to use!)

Please make sure to use python3.6, as I cannot guarantee everything will work as expected on older python versions!
This is because markdown parsing is done by iterating through a dict, which are ordered by default in 3.6.

### Configuration

There are two possible ways of configuring your bot: a config.py file, or ENV variables.

The prefered version is to use a `config.py` file, as it makes it easier to see all your settings grouped together.
This file should be placed in your `dabi` folder, alongside the `__main__.py` file . 
This is where your bot token will be loaded from, as well as your database URI (if you're using a database), and most of 
your other settings.

It is recommended to import sample_config and extend the Config class, as this will ensure your config contains all 
defaults set in the sample_config, hence making it easier to upgrade.

An example `config.py` file could be:
```
from dabi.sample_config import Config


class Development(Config):
    OWNER_ID =  834309762 # my telegram ID
    OWNER_USERNAME = "SA7ANI"  # my telegram username
    API_KEY = "your bot api key"  # my api key, as provided by the botfather
    SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost:5432/database'  # sample db credentials
    MESSAGE_DUMP = '-1234567890' # some group chat that your bot is a member of
    USE_MESSAGE_DUMP = True
    SUDO_USERS = []  # List of id's for users which have sudo access to the bot.
    LOAD = []
    NO_LOAD = []
    TELETHON_HASH = None # for purge stuffs
    TELETHON_ID = None
```

### Python dependencies

Install the necessary python dependencies by moving to the project directory and running:

`pip3 install -r requirements.txt`.

This will install all necessary python packages.

### Database

If you wish to use a database-dependent module (eg: locks, notes, userinfo, users, filters, welcomes),
you'll need to have a database installed on your system. I use postgres, so I recommend using it for optimal compatibility.

In the case of postgres, this is how you would set up a the database on a debian/ubuntu system. Other distributions may vary.

- install postgresql:

`sudo apt-get update && sudo apt-get install postgresql`

- change to the postgres user:

`sudo su - postgres`

- create a new database user (change YOUR_USER appropriately):

`createuser -P -s -e YOUR_USER`

This will be followed by you needing to input your password.

- create a new database table:

`createdb -O YOUR_USER YOUR_DB_NAME`

Change YOUR_USER and YOUR_DB_NAME appropriately.

- finally:

`psql YOUR_DB_NAME -h YOUR_HOST YOUR_USER`

This will allow you to connect to your database via your terminal.
By default, YOUR_HOST should be 0.0.0.0:5432.

You should now be able to build your database URI. This will be:

`sqldbtype://username:pw@hostname:port/db_name`

Replace sqldbtype with whichever db youre using (eg postgres, mysql, sqllite, etc)
repeat for your username, password, hostname (localhost?), port (5432?), and db name.

## Modules
### Setting load order

The module load order can be changed via the `LOAD` and `NO_LOAD` configuration settings.
These should both represent lists.

If `LOAD` is an empty list, all modules in `modules/` will be selected for loading by default.

If `NO_LOAD` is not present, or is an empty list, all modules selected for loading will be loaded.

If a module is in both `LOAD` and `NO_LOAD`, the module will not be loaded - `NO_LOAD` takes priority.

### Creating your own modules

Creating a module has been simplified as much as possible - but do not hesitate to suggest further simplification.

All that is needed is that your .py file be in the modules folder.

To add commands, make sure to import the dispatcher via

`from dabi import dispatcher`.

You can then add commands using the usual

`dispatcher.add_handler()`.

Assigning the `__help__` variable to a string describing this modules' available
commands will allow the bot to load it and add the documentation for
your module to the `/help` command. Setting the `__mod_name__` variable will also allow you to use a nicer, user
friendly name for a module.

The `__migrate__()` function is used for migrating chats - when a chat is upgraded to a supergroup, the ID changes, so 
it is necessary to migrate it in the db.

The `__stats__()` function is for retrieving module statistics, eg number of users, number of chats. This is accessed 
through the `/stats` command, which is only available to the bot owner.

</details>

### Credits

Well, it's all in the commit history and [contributors](https://github.com/SA7ANI/DABI/graphs/contributors) Feel free to open pull requests should any be missing.

### DeepSource Stats

[![DeepSource](https://deepsource.io/gh/SA7ANI/DABI.svg/?label=active+issues&show_trend=true)](https://deepsource.io/gh/SA7ANI/DABI/?ref=repository-badge)
[![DeepSource](https://deepsource.io/gh/SA7ANI/DABI.svg/?label=resolved+issues&show_trend=true)](https://deepsource.io/gh/SA7ANI/DABI/?ref=repository-badge)
