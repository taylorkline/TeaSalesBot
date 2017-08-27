[![Build Status](https://travis-ci.org/jkdf2/TeaSalesBot.svg?branch=master)](https://travis-ci.org/jkdf2/TeaSalesBot)
---------------------------

Tea Sales Bot
=============

The code for [/u/TeaSalesBot](https://www.reddit.com/user/TeaSalesBot) which responds to users of /r/tea who mention a vendor who has had recent sales posted to /r/TeaSales.

This bot is ran by [/u/taylorkline](https://www.reddit.com/user/taylorkline/).

Contributing
------------

Edit [vendors.json](https://github.com/jkdf2/TeaSalesBot/blob/master/vendors.json) to update the vendors for whom the bot will look up sales.

About
-----

This bot is written in `python3.6` and [integrated with Travis](https://travis-ci.org/jkdf2/TeaSalesBot) for continuous testing.

After adding appropriate credentials to `praw.ini.example` and renaming it to `praw.ini`, the following commands will get you up and running:

```
python3.6 -m venv teasalesenv
source teasalesenv/bin/activate
pip install -r requirements.txt
python3.6 bot.py
```