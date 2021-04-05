""" Let's make a color! """

import os
import subprocess
import random
import string
import itertools

from flask import Flask, jsonify, request, render_template, redirect, abort
import redis

APP = Flask(__name__)

# Load file based configuration overrides if present
if os.path.exists(os.path.join(os.getcwd(), "config.py")):
    APP.config.from_pyfile(os.path.join(os.getcwd(), "config.py"))
else:
    APP.config.from_pyfile(os.path.join(os.getcwd(), "config.env.py"))

APP.secret_key = APP.config["SECRET_KEY"]

r = redis.Redis(host=APP.config["REDIS_HOST"], port=int(APP.config["REDIS_PORT"]))

commit_hash = None
try:
    commit_hash = (
        subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
        .strip()
        .decode("utf-8")
    )
# pylint: disable=bare-except
except:
    pass


@APP.route("/static/<path:path>", methods=["GET"])
def _send_static(path):
    return send_from_directory("static", path)


@APP.route("/favicon.ico")
def _send_favicon():
    return send_from_directory("static", "favicon.ico")


@APP.route("/")
def _index():
    count = int(r.get("count").decode("UTF-8"))
    clicks = 0
    for key in r.scan_iter("clicks:*"):
        clicks += int(r.get(key).decode("UTF-8"))
    return render_template(
        "index.html", commit_hash=commit_hash, count=count, clicks=clicks
    )
