# Redmine-Ballcourt

This is a script to look at the issues in a Redmine system and send you an email summary of those issues for which the ball is in your court! That is to say, the issues that are explicitly assigned to you.

I wrote this because I wanted to send periodic reminders out to the members of our team -- perhaps once a week -- as a reminder that nobody else is likely to be working on these tickets because they're assigned to you.... are you comfortable with that?

## Installation

This is a standard Python 3 package. You can install it with pip:

```bash
pip install redmine_ballcourt
```

or you can clone this repository and install it with pip from this directory into whichever virtual environment you'd like to use it:

```bash
pip install .
```

In either case, a script called `redmine-ballcourt` will be installed in your path.

You can run this script with the `--help` or `-h` flag to see the options:

```bash
redmine-ballcourt -h
```

but you will need to set up a configuration file before it can actually do anything. The script will not run without a configuration file.

## Configuration

The script uses the excellent [Dynaconf](https://dynaconf.com/) library to manage configuration. This means that you can set up your configuration in a variety of ways, but here's a suggestion:

There is a file called [ballcourt.toml](ballcourt.toml) in the root of this repository.  This shows a set of example configuration settings.  You can either modify a copy of this file and place it in your current working directory, or you can use it as a basis and override the settings in a file of your own.  

At present, the script will look for:
* `/etc/ballcourt.toml`
* `ballcourt.toml` (in the current working directory)
* `.secrets.toml` (in the current working directory)

Later files, if found, will override the settings in earlier files.  So you might want to put your normal configuration into `ballcourt.toml`, and put your SMTP password and Redmine API key into `.secrets.toml`, and not check that into source control.

You can also use environment variables to set configuration values.  The environment variable names are the same as the configuration keys, but in all caps and with underscores instead of periods, and with a 'BALLCOURT_' prefix.  For example, the `url` configuration key can be set with the `BALLCOURT_URL` environment variable.
A `.env` file in the current working directory can also be used to set environment variables.

The sample `ballcourt.toml` will show you most of the configuration options you can set.  These include the templates for the HTML and text emails that will be sent, which are templated using [Jinja](https://jinja.palletsprojects.com/en/).

If you want to change the location of the configuration files, the easiest way at present is to use the environment variables `SETTINGS_FILE_FOR_DYNACONF` or `SETTINGS_FILES_FOR_DYNACONF`.  See the [Dynaconf documentation](https://dynaconf.com/) for more details.

## Usage

You can test the script by running it with the `-l` flag, which will simply list the Projects in your Redmine system.  If this works, then you've set your URL and API key correctly.

You can also try the `-u` flag, which will list the users.  On each line, the first field will be the user's login name, and you can use these later.

**PLEASE NOTE!**

The default operation of the script, if you run it without any options, is slightly dangerous, and I admit this is perhaps a bad idea. If you've configured it correctly, it will send an email to every user in the system, listing the issues that are assigned to them.  

So you probably want to restrict this while testing. 

Firstly, you can restrict the users or projects that are considered by specifying them in the settings.  For example, you could set `include_users = ["my_username"]` .

Secondly, you can use the `-d` flag to specify a debug email address, and the messages will all be sent to that address instead of to the users concerned.  So to see the messages that would be sent to user1 and user2, you could specify them in the `include_users` setting in your configuration file and then run:

`redmine-ballcourt -d myemail@example.com`

Thirdly, you can use the `-n` flag to specify a dry run, which will print the emails to the console instead of sending them.

But when you're ready to go, you can just run the script without any options, and it will send the emails to all the users concerned.

## License

This software is released under the GNU Public License v2.  See the [LICENSE](LICENSE) file for details.

Quentin Stafford-Fraser
quentinsf.com
Oct 2024
