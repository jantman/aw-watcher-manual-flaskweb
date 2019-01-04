from flask import Flask, render_template
import os
from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

app = Flask(__name__)

def get_config():
    confpath = os.path.dirname(os.path.realpath(__file__))
    if not os.path.exists(confpath):
        raise RuntimeError('ERROR: Configuration not found: %s' % confpath)
    with open(os.path.join(confpath, 'config.yaml'), 'r') as fh:
        data = load(fh, Loader=Loader)
    return data

@app.route("/")
def hello():
    return "Hello World!"
