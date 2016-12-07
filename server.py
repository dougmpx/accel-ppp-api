from datetime import datetime
from flask import Flask, request, abort
from flask_json import FlaskJSON, JsonError, json_response, as_json
import subprocess
import string
from functools import wraps
import time
import re

app = Flask(__name__)
FlaskJSON(app)

API_TOKEN = 'e32f0676ed7aa10cc827fa243bad5bcf11416e454abcaf2eaa4813bc34d37470'

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not 'token' in request.args:
            abort(401)
        if request.args['token'] != API_TOKEN:
            abort(401)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/v1/clients', methods=['GET'])
@token_required
def clients_get_all():
    p = subprocess.Popen(["accel-cmd", "show sessions"], stdout=subprocess.PIPE)
    output, err = p.communicate()
    clients = output.split('\n')
    del clients[0]
    del clients[0]
    response = []
    for line in clients:
        line = line.translate(None, string.whitespace)
        line = line.split('|')
        #print line
        data_dict = {}
        response.append(data_dict)
        for index,item in enumerate(line):
            #print index,item
            if index == 0:
                data_dict['ifname'] = item
            if index == 1:
                data_dict['login'] = item
            if index == 2:
                data_dict['mac'] = item
            if index == 3:
                data_dict['ip'] = item
            if index == 4:
                data_dict['rates'] = item
            if index == 7:
                data_dict['state'] = item
            if index == 8:
                data_dict['uptime'] = item
    return json_response(data=response)

@app.route('/api/v1/clients/login/<string:login>', methods=['GET'])
@token_required
def get_client_login(login):
    p = subprocess.Popen(["accel-cmd", "show sessions", "match", "username", login], stdout=subprocess.PIPE)
    output, err = p.communicate()
    clients = output.split('\n')
    del clients[0]
    del clients[0]
    clients.pop()
    response = []
    for line in clients:
        #print line
        line = line.translate(None, string.whitespace)
        line = line.split('|')
        data_dict = {}
        response.append(data_dict)
    	for index,item in enumerate(line):
            #print index,item
            if index == 0:
                data_dict['ifname'] = item
            if index == 1:
                data_dict['login'] = item
            if index == 2:
                data_dict['mac'] = item
            if index == 3:
                data_dict['ip'] = item
            if index == 4:
                data_dict['rates'] = item
            if index == 7:
                data_dict['state'] = item
            if index == 8:
                data_dict['uptime'] = item
    return json_response(data=response)

@app.route('/api/v1/client/rates/<string:ifname>', methods=['GET'])
@token_required
def client_get_rates(ifname):
    try:
        # LAST RX BYTES
        file_last_rx = open('/sys/class/net/'+ifname+'/statistics/rx_bytes', 'r')
        last_rx = float(file_last_rx.read())
    
        # LAST TX BYTES
        file_last_tx = open('/sys/class/net/'+ifname+'/statistics/tx_bytes', 'r')
        last_tx = float(file_last_tx.read())
    
        time.sleep(2)
    
         # CURRENT RX BYTES
        file_current_rx = open('/sys/class/net/'+ifname+'/statistics/rx_bytes', 'r')
        current_rx = float(file_current_rx.read())
    
        # CURRENT TX BYTES
        file_current_tx = open('/sys/class/net/'+ifname+'/statistics/tx_bytes', 'r')
        current_tx = float(file_current_tx.read())

        tx = current_tx - last_tx
        rx = current_rx - last_rx
    
        tx = ((tx /2 / 1024 / 1024) * 8)
        rx = ((rx /2 /1024 / 1024) * 8)
    
        rates = {}
        rates['tx'] = tx
        rates['rx'] = rx
    except:
        return json_response(data=[], error={'Error to get values of interface'})
    return json_response(data=rates)

@app.route('/api/v1/logs', methods=['GET'])
@token_required
def get_logs():
    rs = []
    try:
	p = subprocess.Popen(["tail", "-n", "20", "/var/log/accel-ppp/accel-ppp.log"], stdout=subprocess.PIPE)
    	output, err = p.communicate()
        ansi_escape = re.compile(r'\x1b[^m]*m')
        output = ansi_escape.sub('', output)
        data = output.split('\n')
        for line in data:
            response = {}
            response['log'] = line
            rs.append(response)
        return json_response(data=rs)
    except:
        return json_response(data=[], error={'Error to get value of log file'})

if __name__ == '__main__':
    app.run()
