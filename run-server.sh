#!/bin/bash
install_dir=$(cd $(dirname $0) && pwd)
cd $install_dir
. env/bin/activate
env FLASK_APP=server.py flask run
