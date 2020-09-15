import json
import subprocess

from flask import Flask, escape, request
from prometheus_client import Counter, Gauge, exposition
from requests import get

app = Flask(__name__)

power = Gauge("power", "current power in watts (W)", ["type","ch_label", "ch"])
voltage = Gauge("voltage", "current voltage (V)", ["type","ch_label", "ch"])
fs = Gauge("filesystem", "Filesytem stats from df", ["id", "mount", "stat"])

@app.route('/')
@app.route('/metrics')
def server():
    sample = get('http://192.168.1.109/current-sample').json()

    for channel in sample["channels"]:
        power.labels(
            type=channel["type"],
            ch_label=(channel.get('label') or ''),
            ch=channel["ch"],
        ).set(channel["p_W"])
        
        voltage.labels(
            type=channel["type"],
            ch_label=(channel.get('label') or ''),
            ch=channel["ch"],
        ).set(channel["v_V"])

    disk_info = json.loads(subprocess.getoutput(
        "df -B1 | tail -n +2 | awk '{print \"[\\\"\"$1\"\\\",\"$2\",\"$3\",\"$4\",\\\"\"$6\"\\\"]\"}' | jq -s ."))
    for line in disk_info:
        fs_size = float(line[1])
        fs_used = float(line[2])
        fs_utilized_pct = fs_used * 100.0 / fs_size
        fs.labels(id=line[0], mount=line[-1], stat="size").set(line[1])
        fs.labels(id=line[0], mount=line[-1], stat="used").set(line[2])
        fs.labels(id=line[0], mount=line[-1], stat="avail").set(line[3])
        fs.labels(id=line[0], mount=line[-1], stat="util").set(fs_utilized_pct)

    response_text = exposition.generate_latest()
        
    print(response_text[:1000])
        
    return response_text
