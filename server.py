import json
import subprocess

from flask import Flask, escape, request
from prometheus_client import Counter, Gauge, exposition
from requests import get

app = Flask(__name__)

power = Gauge("power", "current power in watts (W)", ["type"])
voltage = Gauge("voltage", "current voltage (V)", ["type"])
fs = Gauge("filesystem", "Filesytem stats from df", ["id", "mount", "stat"])

@app.route('/')
@app.route('/metrics')
def server():
    sample = get('http://192.168.1.106/current-sample').json()

    for channel in sample["channels"]:
        power.labels(type=channel["type"]).set(channel["p_W"])
        voltage.labels(type=channel["type"]).set(channel["v_V"])

    disk_info = json.loads(subprocess.getoutput("df -B1 | tail -n +2 | awk '{print \"[\\\"\"$1\"\\\",\"$2\",\"$3\",\"$4\",\\\"\"$6\"\\\"]\"}' | jq -s ."))
    for line in disk_info:
        fs.labels(id=line[0], mount=line[-1], stat="size").set(line[1])
        fs.labels(id=line[0], mount=line[-1], stat="used").set(line[2])
        fs.labels(id=line[0], mount=line[-1], stat="avail").set(line[3])
        
    return exposition.generate_latest()
