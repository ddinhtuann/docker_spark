
from flask import Flask, jsonify, request
import ujson
import os
import shutil
import subprocess
import glob
import requests
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024
app.config['TIME_OUT'] = 120



@app.route("/crossdotProduct", methods = ['GET', 'POST'])
def calculate_crossdot():
    if request.method == 'POST':
        
        data = ujson.load(request.files['data'])
        print("1")
        hdfs_path = '/webhdfs/v1/user/coretech/sample.json?op=CREATE&overwrite=true'
        
        response = requests.put(hdfs_host + hdfs_path, headers=headers, params=params, data=ujson.dumps(data))
        print("2")
        os.system('/spark/bin/spark-submit --deploy-mode cluster --master spark://spark-master37:7077 --executor-memory 4G --driver-memory 8G --driver-cores 4 --executor-cores 2 --jars  "/usr/share/Handwritten-digits-classification-pyspark/jars/*" --class CrossDot hdfs://namenode37:9000/user/coretech/crossdot.jar')
        return "success"
        

if __name__ == "__main__":

    hdfs_host = 'http://namenode37:9870'
    headers = {'Content-Type': 'application/octet-stream'}
    params = {'user.name': 'root'}
    app.run(host='0.0.0.0', port = 5001, debug=True)


