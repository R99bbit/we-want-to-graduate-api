'''
@author R99bbit
@summary API Server(WITH E4 Connect)
@flask application
'''

from flask import Flask
from flask_restx import Api, Resource
import os
import json
import csv
import zipfile
from e4client import E4Connect # pip3 install e4client

def convert_unixtime(date_time):
    import datetime
    timestamp = datetime.datetime.fromtimestamp(int(date_time))
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')

def convert_csv_to_json(root_path):
    session_csv_path    = f'{root_path}'
    session_bvp_path    = f'{root_path}/BVP.csv'
    DATA = dict()

    ''' BVP.csv '''
    csvfile = open(session_bvp_path, 'r')
    fieldnames = ["photoplethysmograph"]
    data = list(csv.reader(csvfile))
    csvfile = [[float(d[0]) for d in data]]
    
    s = dict()
    for i in range(len(fieldnames)):
        s[fieldnames[i]] = csvfile[i]
    DATA['BVP'] = s

    return DATA

''' API '''
USER = 'uso699@naver.com'
PASS = 'qkrals1216!'
obj = E4Connect(user=USER, pwd=PASS)
app = Flask(__name__)
api = Api(app)

@api.route('/all_session_info')
class ResponseSessions(Resource):
    def get(self):
        return obj.sessions_list()

@api.route('/last_session_info')
class ResponseLastSession(Resource):
    def get(self):
        session_item = obj.sessions_list()[0]
        res = session_item['id']
        return res

@api.route('/get_last_session')
class ResponseLastSession(Resource):
    def get(self):
        ''' get last session id '''
        session_item = obj.sessions_list()[0]
        last_session_id = session_item['id']
        
        ''' download last session from E4Connect '''
        obj.download_session(last_session_id)
        
        ''' unzip session file '''
        session_zip_path = last_session_id + '.zip'
        session_zip_stream = zipfile.ZipFile(session_zip_path)
        session_zip_stream.extractall('./data')
        session_zip_stream.close()

        ''' csv to json '''
        res = convert_csv_to_json('data/')
        res['time'] = dict()
        res['time']['start_time'] = convert_unixtime(session_item['start_time'])
        res['time']['end_time'] = convert_unixtime(int(session_item['start_time']) + int(session_item['duration']))

        res['user'] = USER
        return res

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=3000)