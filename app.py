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
    session_acc_path    = f'{root_path}/ACC.csv'
    session_bvp_path    = f'{root_path}/BVP.csv'
    session_eda_path    = f'{root_path}/EDA.csv'
    session_hr_path     = f'{root_path}/HR.csv'
    session_ibi_path    = f'{root_path}/IBI.csv'
    session_temp_path   = f'{root_path}/TEMP.csv'
    session_tags_path    = f'{root_path}/tags.csv'
    DATA = dict()
    
    ''' TEMP.csv '''
    csvfile = open(session_temp_path, 'r')
    fieldnames = ['temperature(C)']
    data = list(csv.reader(csvfile))
    csvfile = [[float(d[0]) for d in data]]
    s = dict()
    for i in range(len(fieldnames)):
        s[fieldnames[i]] = csvfile[i]
    DATA['TEMP'] = s

    ''' EDA.csv '''
    csvfile = open(session_eda_path, 'r')
    fieldnames = ["microsecond"]
    data = list(csv.reader(csvfile))
    csvfile = [[float(d[0]) for d in data]]
    s = dict()
    for i in range(len(fieldnames)):
        s[fieldnames[i]] = csvfile[i]
    DATA['EDA'] = s

    ''' BVP.csv '''
    csvfile = open(session_bvp_path, 'r')
    fieldnames = ["photoplethysmograph"]
    data = list(csv.reader(csvfile))
    csvfile = [[float(d[0]) for d in data]]
    
    s = dict()
    for i in range(len(fieldnames)):
        s[fieldnames[i]] = csvfile[i]
    DATA['BVP'] = s

    ''' ACC.csv '''
    csvfile = open(session_acc_path, 'r')
    fieldnames = ["x", "y", "z"]
    data = list(csv.reader(csvfile))
    csvfile = []
    for i in range(len(fieldnames)):
        temp = [float(d[i]) for d in data]
        csvfile.append(temp)
    
    s = dict()
    for i in range(len(fieldnames)):
        s[fieldnames[i]] = csvfile[i]
    DATA['ACC'] = s

    ''' IBI.csv '''
    csvfile = open(session_ibi_path, 'r')
    fieldnames = ["sec", "duration-in-sec"]
    data = list(csv.reader(csvfile))
    csvfile = []

    if(os.stat(session_ibi_path).st_size == 0):
        s = dict()
    else:
        for i in range(len(fieldnames)):
            if i==1:
                temp = [data[0][1]]+[float(d[i]) for d in data[1:]]
            else:
                temp = [float(d[i]) for d in data]
            csvfile.append(temp)
        
        s = dict()
        for i in range(len(fieldnames)):
            s[fieldnames[i]] = csvfile[i]

    DATA['IBI'] = s

    ''' HR.csv '''
    if(os.stat(session_hr_path).st_size == 0):
        s = dict()
    else:
        csvfile = open(session_hr_path, 'r')
        fieldnames = ['initial-time-of-the-session', 'sample-rate(Hz)', "BVP"]
        data = list(csv.reader(csvfile))
        
        csvfile = [float(data[0][0]), float(data[1][0]), [float(d[0]) for d in data[2:]]]
                
        s = dict()
        for i in range(len(fieldnames)):
            s[fieldnames[i]] = csvfile[i]
    DATA['HR'] = s

    ''' tags '''
    if(os.stat(session_tags_path).st_size == 0):
        s = dict()
    else:
        csvfile = open(session_tags_path, 'r')
        fieldnames = ["event-time"]
        csvfile = [[float(d[0]) for d in data]]
            
        s = dict()
        for i in range(len(fieldnames)):
            s[fieldnames[i]] = csvfile[i]
    DATA['tags'] = s

    return DATA

''' API '''
USER = 'uso699@naver.com'
PASS = 'gimdodo4564'
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