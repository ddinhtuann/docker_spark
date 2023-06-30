import zipfile
import requests
import os
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024
app.config['TIME_OUT'] = 120


@app.route("/crackzip", methods = ['GET', 'POST'])

def crack_zip():
    if request.method == 'POST':

        zip_file = zipfile.ZipFile('/usr/share/Handwritten-digits-classification-pyspark/zip_folder/file.zip')
        with open('/usr/share/Handwritten-digits-classification-pyspark/zip_folder/wordlist0.txt') as f:
            passwords = f.readlines()

        found = "False"
        for password in passwords:
            try:
                zip_file.extractall(pwd = password.encode())
                found = "True"
                data  = {
		            "node": "cracker-37",
                    "found": found, 
                    "password": bytes(password, 'utf-8')
                }
                response = requests.post(url = 'http://10.0.68.37:2510/handlepassword', data = data)
                return "1"
            except Exception as e:
                pass
        data = {
                    "found": found,
		            "node": "cracker-37",
                    "password": None
                }

        response = requests.post(url = 'http://10.0.68.37:2510/handlepassword', data = data)
        return "1"

if __name__ == "__main__":

    app.run(host='0.0.0.0', port = 5001, debug=False)

    
    
    

    