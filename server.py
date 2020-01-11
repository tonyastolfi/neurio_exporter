from flask import Flask, escape, request
from prometheus_client import Counter, Gauge, exposition
from requests import get

app = Flask(__name__)

power = Gauge("power", "current power in watts (W)", ["type"])
voltage = Gauge("voltage", "current voltage (V)", ["type"])


@app.route('/')
def server():
    sample = get('http://192.168.1.106/current-sample').json()

    for channel in sample["channels"]:
        power.labels(type=channel["type"]).set(channel["p_W"])
        voltage.labels(type=channel["type"]).set(channel["v_V"])

    return exposition.generate_latest()
