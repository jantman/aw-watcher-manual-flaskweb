# aw-watcher-manual-flaskweb

Tiny flask webapp for ActivityWatch manual data input.

I've started using the excellent [ActivityWatch](https://activitywatch.net/) project to track how I spend my time when I'm at a computer. I know it's going to be really helpful, but I also wanted a way to perform coarse-grained tracking of time I spent away from the computer (cooking, watching TV, reading, etc). I really like what ActivityWatch does and I don't use an existing time tracking app, so this seemed like the simplest and most efficient solution.

__WARNING:__ This is an exremely crude, quick app. It can only handle one user at a time, and does all sorts of stuff that would be atrocious for pretty much any other use case (like saving state in a flat file on disk). ActivityWatch itself is really a single-user app, so this works as something that I can open in a tiny browser window on my desktop (where it, and ActivityWatch, runs), from my cell phone when I'm home, or from my laptop when I'm in the office (over VPN).

## What and How

What it does and how it works. When it sends data.

## Installation

1. Clone this git repo: ``git clone https://github.com/jantman/aw-watcher-manual-flaskweb.git``
2. Create a new virtualenv using Python 3.4+: ``python3 -m virtualenv .``
3. Activate the virtualenv: ``source bin/activate``
4. Install dependencies: ``pip install -r requirements.txt``
5. Install ActivityWatch's aw-core and aw-client from github, since they don't publish to PyPI. These examples are for the versions used in ActivityWatch v0.8.0b7:
   * ``pip install https://github.com/ActivityWatch/aw-core/archive/389321cbc4d0b12e2d26e3feb300e5e1a5ad8528.zip``
   * ``pip install https://github.com/ActivityWatch/aw-client/archive/0cf3de54dd60ded57832b0e6a88649f6bf8f67fd.zip``

## Configuration

Copy ``config.example.yaml`` to ``config.yaml`` and edit appropriately. Settings are as follows:

## Running

It's only a single user, so the built-in Flask dev server should be fine:

``FLASK_APP=flaskapp.py flask run``

and the app will be on [http://localhost:5000/](http://localhost:5000/)

If you want a different port, you can do that like: ``FLASK_APP=flaskapp.py flask run --port 8888``
