from flask import Flask, render_template, redirect, request
import os
from yaml import load
import time
from datetime import datetime, timedelta
import logging
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader
from aw_core.models import Event
from aw_client import ActivityWatchClient

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)


def get_config():
    confpath = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'config.yaml'
    )
    if not os.path.exists(confpath):
        raise RuntimeError('ERROR: Configuration not found: %s' % confpath)
    with open(confpath, 'r') as fh:
        data = load(fh, Loader=Loader)
    return data


def get_state_path():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'state.txt'
    )


def get_state(config):
    statepath = get_state_path()
    if not os.path.exists(statepath):
        return None, None, None
    with open(statepath, 'r') as fh:
        raw = fh.read()
    app.logger.debug('Read state: %s', raw)
    try:
        ts, cat, item = raw.strip().split(':', 2)
        ts = int(ts)
        assert cat in config['categories']
        assert item in config['categories'][cat]
    except Exception:
        app.logger.error('Unable to parse state: %s', raw)
        return None, None, None
    return ts, cat, item


def set_state(ts, cat, item):
    statepath = get_state_path()
    s = '%d:%s:%s' % (ts, cat, item)
    app.logger.info('Writing state: %s', s)
    with open(statepath, 'w') as fh:
        fh.write(s)


def remove_state():
    statepath = get_state_path()
    if not os.path.exists(statepath):
        return
    app.logger.info('Removing state')
    os.unlink(statepath)


def timedelta_to_hms(td):
    hours = 0
    minutes = 0
    seconds = td.total_seconds()
    if seconds > 3600:
        hours = seconds / 3600
        seconds = seconds % 3600
    if seconds > 60:
        minutes = seconds / 60
        seconds = seconds % 60
    return hours, minutes, seconds


def timedelta_to_str(td):
    h, m, s = timedelta_to_hms(td)
    res = ''
    if h > 0:
        res = '%dh' % h
    if m > 0:
        res += '%dm' % m
    res += '%ds' % s
    return res


def end_current_event(start_ts, category, item, end_dt=None):
    start_dt = datetime.utcfromtimestamp(start_ts)
    if end_dt is None:
        end_dt = datetime.utcnow()
    app.logger.debug('Instantiating client (127.0.0.1:5600)')
    client = ActivityWatchClient(
        "aw-watcher-manual-flaskweb", host='127.0.0.1:5600'
    )
    bucket_id = "{}_{}".format("aw-watcher-manual-flaskweb", client.hostname)
    app.logger.debug('Creating bucket: %s', bucket_id)
    client.create_bucket(bucket_id, event_type="currentwindow")
    t = 'manual: %s/%s' % (category, item)
    evt = Event(
        timestamp=start_dt, duration=(end_dt - start_dt).total_seconds(),
        data={'app': t, 'title': t, 'category': category, 'item': item}
    )
    inserted_event = client.insert_event(bucket_id, evt)
    app.logger.info('Inserted event: %s', inserted_event)


@app.route("/")
def index():
    config = get_config()
    curr_ts, curr_cat, curr_item = get_state(config)
    timestr = 'unset'
    if curr_ts is not None:
        start_dt = datetime.utcfromtimestamp(curr_ts)
        timestr = timedelta_to_str(datetime.utcnow() - start_dt)
    return render_template(
        'index.html', config=config, curr_cat=curr_cat, curr_item=curr_item,
        timestr=timestr
    )


@app.route("/select/<category>/<item>")
def select_item(category, item):
    app.logger.debug('Selected category=%s item=%s', category, item)
    config = get_config()
    curr_ts, curr_cat, curr_item = get_state(config)
    if curr_cat is not None and curr_item is not None:
        app.logger.debug(
            'Ending current event (category=%s item=%s)', curr_cat, curr_item
        )
        end_current_event(curr_ts, curr_cat, curr_item)
    set_state(int(time.time()), category, item)
    return redirect('/', code=302)


@app.route('/discard')
def discard():
    remove_state()
    return redirect('/', code=302)


@app.route('/finish')
def finish():
    config = get_config()
    curr_ts, curr_cat, curr_item = get_state(config)
    end_current_event(curr_ts, curr_cat, curr_item)
    remove_state()
    return redirect('/', code=302)


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    config = get_config()
    curr_ts, curr_cat, curr_item = get_state(config)
    if curr_ts is None:
        return redirect('/', code=302)
    if request.method == 'POST':
        start_dt = datetime.utcfromtimestamp(curr_ts)
        end_dt = start_dt + timedelta(
            seconds=int(request.form['seconds']) +
                    (int(request.form['minutes']) * 60) +
                    (int(request.form['hours']) * 3600)
        )
        new_cat, new_item = request.form['item'].split('/', 1)
        app.logger.info(
            'Handling edited event; current state: ts=%s cat=%s item=%s; '
            'saving: ts=%s cat=%s item=%s end_dt=', curr_ts, curr_cat,
            curr_item, curr_ts, new_cat, new_item, end_dt
        )
        end_current_event(curr_ts, new_cat, new_item, end_dt=end_dt)
        remove_state()
        return redirect('/', code=302)
    else:
        start_dt = datetime.utcfromtimestamp(curr_ts)
        hours, minutes, seconds = timedelta_to_hms(
            datetime.utcnow() - start_dt
        )
        return render_template(
            'edit.html', config=config, curr_cat=curr_cat, curr_item=curr_item,
            curr_ts=curr_ts, hours=hours, minutes=minutes, seconds=seconds
        )
