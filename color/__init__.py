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


def get_rgb():
    try:
        red = int(r.get("red").decode("UTF-8"))
    except:
        red = 0
    try:
        green = int(r.get("green").decode("UTF-8"))
    except:
        green = 0
    try:
        blue = int(r.get("blue").decode("UTF-8"))
    except:
        blue = 0
    return {"red": red, "green": green, "blue": blue}


@APP.route("/")
def _index():
    colors = get_rgb()
    red = colors["red"]
    green = colors["green"]
    blue = colors["blue"]
    total = red + green + blue
    if total == 0:
        total = 1
    r_percent = str(int(red * 100 / total)) + "%"
    g_percent = str(int(green * 100 / total)) + "%"
    b_percent = str(int(blue * 100 / total)) + "%"
    return render_template(
        "index.html", commit_hash=commit_hash, r=r_percent, g=g_percent, b=b_percent
    )


@APP.route("/api/v1/red", methods=["POST"])
def _api_v1_red():
    r.incr("red")
    return jsonify(get_rgb())


@APP.route("/api/v1/green", methods=["POST"])
def _api_v1_green():
    r.incr("green")
    return jsonify(get_rgb())


@APP.route("/api/v1/blue", methods=["POST"])
def _api_v1_blue():
    r.incr("blue")
    return jsonify(get_rgb())
