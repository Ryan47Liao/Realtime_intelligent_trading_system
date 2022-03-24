import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import csv
from datetime import datetime
from datetime import timedelta
#Modeling
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import json
from tqdm import tqdm
########################################################################
from re import S
import socket
import threading
import csv
import json
import argparse
import sys
import time

class ThreadedServer:
    def __init__(self,host,port,data_file_path,wait = 1):
        self.host = host
        self.port = port
        self.data_file_path = data_file_path
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.lock = threading.Lock()
        ################################################################
        self.holding = 0
        self.wait = wait

    def listen(self):
        print('Server Established')
        self.sock.listen(60)
        while True:
            print('Listening for client')
            client, address = self.sock.accept()
            client.settimeout(500)
            threading.Thread(target=self.listenToClient, args=(client, address)).start()
            threading.Thread(target=self.sendStreamToClient, 
                            args=(client, self.sendCSVfile())).start()

    def sendCSVfile(self):
        out = []
        csvfile = open(self.data_file_path, 'r')
        reader = csv.DictReader(csvfile)
        for row in reader:
            out += [row]
        return out

    def convertStringToJSON(self, st):
        return json.dumps(st)

    def sendStreamToClient(self, client, buffer):
        for i in buffer:
            print(i)#List of db 'asdasd,asdasd'
            print(type(i))
            i['holdings'] = self.holding    #Include current holding
            # try:
            client.send((self.convertStringToJSON(i) + '\n').encode('utf-8'))
            time.sleep(self.wait)
            # except:
            #     print('End of stream')
            #     return False
        client.send((self.convertStringToJSON(self.state) + '\n').encode('utf-8'))
        return False

    def listenToClient(self, client, address):
        size = 1024
        while True:
            try:
                data = str(client.recv(size), "utf-8").replace("'",'"')
                print('<<<<<<<<<Client Responded>>>>>>>>>>')
                answer = json.loads(data) #Transform str-dict back into dict
                self.handle_client_answer(answer)
                # client.send(response)
            except:
                print('Client closed the connection')
                print("Unexpected error:", sys.exc_info()[0])
                client.close()
                return False

    def handle_client_answer(self, answer):
        print(answer)
        holding = self.holding
        if  answer['Direction'] == 'Long':
            self.holding += answer['Amount']
        elif answer['Direction'] == 'Short':
            self.holding -= answer['Amount']
        print(f'Holdings:|{holding} -> {self.holding} BTC\n')

if __name__ == '__main__':
    df_all = pd.read_csv('BTC_TWT_GC.csv')
    df_pre2020 = df_all.query('date < "2020-01-01"')
    df_Post2020 = df_all.query('date >= "2020-01-01"')
    df_Post2020.to_csv('df_Post2020.csv')
    
    Server = ThreadedServer('127.0.0.1',9999,'df_Post2020.csv',wait = 0.1)
    Server.listen()
