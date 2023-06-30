
from flask import Flask, jsonify, request
import ujson
import os
import time
import subprocess
import glob
import requests
app = Flask(__name__)


@app.route("/getlist", methods = ['GET', 'POST'])
def get_list():
    if request.method == 'POST':
        
        res = []
        request_data = request.get_json()
        print(request_data)
        
        datas = request_data['data']
        print(datas)

        for data in datas:
            res.append(data['values'])


        v= {
            "data": res
        }

        time_stamp = str(int(time.time()))
        hdfs_path = '/webhdfs/v1/user/coretech/' + time_stamp + '.json?op=CREATE&overwrite=true'
        response = requests.put(hdfs_host + hdfs_path, headers=headers, params=params, data=ujson.dumps(v))
        
        r = requests.post(url = 'http://10.0.80.188:40003/tbl_Category/Data', json = v)
        assert r.status_code == 200
        print("post success")
        return jsonify({'result': r.json()})


@app.route("/getpassword", methods = ['GET', 'POST'])
def get_password():

    print("0")
    if request.method == "POST":

        pass_found = request.form.get("password")
        print(pass_found)



if __name__ == "__main__":

    hdfs_host = 'http://namenode37:9870'
    headers = {'Content-Type': 'application/octet-stream'}
    params = {'user.name': 'root'}
    app.run(host='0.0.0.0', port = 5000, debug=True)


