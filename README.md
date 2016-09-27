# Kutemail

A simple and easy-to-use email client for KDE or Qt.

![screenshot of Kutemail in action](https://raw.githubusercontent.com/Etenil/kutemail/master/kutemail-screenshot.png)

## Current state

What works, what doesn't and what to expect.

- Only one IMAP account can be configured.
- Make sure nothing confidential is in it as the password is currently stored in clear.
- Emails are not cached locally, so need to be queried after each restart
- Email fetch is done in-thread, so the UI is unresponsive while refreshing
- A global lack of icons and GUI best practices

## Install

To install this software, make sure you have python3 (I use 3.5, not sure if previous versions will work)
pyqt5 and imaplib installed, then you should be fine.

Alternatively, you can use pip for everything except PyQt5, and install in a virtual environment like so:

```
$ pyvenv venv
$ source venv/bin/activate
(venv)$ sed -i 's/packages = false/packages = true/' venv/pyvenv.cfg
(venv)$ pip install -r requirements.txt
```

## Running

To run the client, use this command:

```
$ python3 kutemail.py
```

## Config

On the first run, a dialog will ask your email details. This only works for Gmail for now (that's what
I test with). These get saved in `~/config/kutemail.rc`. This file is a python pickle dump. I'm not sure
how safe it is to modify it; you're probably better off deleting it and going through the dialog again.

Note that this file will most likely change a lot, and probably end up in a more human-readable format.
