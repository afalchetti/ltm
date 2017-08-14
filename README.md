# Small Exercise in Software Server Development

## by Angelo Falchetti

Internal Project. Do not use it.

## How to use

First, you should configure the scripts and django with the particulars of the
server. To do this, run `python configure.py` with appropriate arguments (which
you can see using `python configure.py --help`).

Then, you should change the MySQL credentials found in `ltm/token/mysql.json`.
Set up MySQL appropriately and copy the Nginx config file to the Nginx directory.
Get an SSL certificate, possibly from [Let's Encrypt](https://letsencrypt.org/).

Finally run `start.sh`.