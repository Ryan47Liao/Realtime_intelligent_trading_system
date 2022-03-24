
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
################################################################
from re import S
import socket
import threading
import csv
import json
import argparse
import sys
from threading import Thread
import time
################################################################
from BTC_Trading_Algo import TWT_BTC

class TWT_BTC_Client:
    def __init__(self,HOST = "localhost", PORT = 9999,init_wealth = 1e10,Trading_Algo=None):
        self.HOST = HOST
        self.PORT = PORT
        self.Set_Trading_Algo(Trading_Algo)
        self.wealth = init_wealth

    def Set_Trading_Algo(self,Trading_Algo):
        self.Trading_Algo = Trading_Algo
    
    def _connect(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.sock:  # TCP
            # Connect to server and send data
            self.sock.connect((self.HOST, self.PORT))
            while True:
                try:
                    received = str(self.sock.recv(1024), "utf-8") #Intepret string into Json
                    print("Received: {}".format(received))
                    #####################
                    try:
                        RCVD = received.replace("'",'"')
                    except TypeError:
                        pass 
                    RCVD = json.loads(RCVD)
                    self.date = RCVD['date']
                    self.price = float(RCVD['close'])
                    #####################
                    Order = self.Trading_Algo(received = received,current_wealth = self.wealth) #Holding is contained
                    #Order example:{"Direction":str,"Amount":float}
                    cash_prev = self.wealth
                    if Order is not None:
                        self.Send_Order(Order) 
                        self.Handle_Order(Order)
                    print(f'$$$Cash:{cash_prev} -> {self.wealth}\n')
                except SyntaxError:
                    print("Message Over")
                    break
            sys.exit(0)
            
    def Handle_Order(self,Order):
        signal = Order['Direction']
        amount = Order['Amount']
        if  signal == 'Long':
            self.wealth -= amount*self.price 
            
        elif signal == 'Short':
            self.wealth += amount*self.price  

            
    def Send_Order(self,Order):
        self.sock.sendall(bytes(str(Order) , "utf-8"))

    def connect(self):
        t = Thread(target = self._connect)
        t.start()

if __name__ == "__main__":
    df_all = pd.read_csv('BTC_TWT_GC.csv')
    df_pre2020 = df_all.query('date < "2020-01-01"')
    df_Post2020 = df_all.query('date >= "2020-01-01"')
    df_Post2020.to_csv('df_Post2020.csv')
        
    Twt = TWT_BTC(df_pre2020,use_hist_price=False,shreshold = 0.05)
    
    client = TWT_BTC_Client(Trading_Algo = Twt.send_signal)
    client._connect()