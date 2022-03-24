###
#packages
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
from sklearn.model_selection import GridSearchCV
from sklearn.svm import LinearSVR
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm
################################################################
def DATE(String):
    import datetime
    STR = String.split("-")
    Y = int(STR[0])
    M = int(STR[1])
    D = int(STR[2])
    return(datetime.date(Y,M,D))

def Normalize_by(Lst,value):
    _Lst = np.array(Lst)
    return value*(_Lst/_Lst.max())

class BackTester:
    def __init__(self,price_db_file_path,initial_wealth,price_name = 'close',date_name='date'):
        self.price_tag =  price_name
        self.date_tag = date_name
        self.streaming_db = sendCSVfile(price_db_file_path)
        self.price_db = pd.read_csv(price_db_file_path)
        self._initial_wealth = initial_wealth

    def RESET_ALL(self):
        self.Long_signal = []
        self.Short_signal = []
        self.wealth_reset(self._initial_wealth)
        self.holdings_reset()
        
    def wealth_reset(self,initial_wealth):
        self._wealth = initial_wealth
        self._wealth_track = {'wealth':[],'date':[]}
        self.total_wealth = {'tot_wealth':[],'date':[]}

    def holdings_reset(self):
        self.holdings = 0
        self.holding_track = {'holdings':[],'date':[]}

    def update_wealth_holding(self,wealth_change,date,show_progress):
        self._wealth += wealth_change
        self._wealth_track['wealth'].append(self._wealth)
        self._wealth_track['date'].append(date)

    def Naive_update(self):
        self.holding_track['date'].append(self.date)
        self._wealth_track['date'].append(self.date)
        self.holding_track['holdings'].append(self.holdings)
        self._wealth_track['wealth'].append(self._wealth)
        self.Total_wealth_update()

    def Total_wealth_update(self):
        self.total_wealth['date'].append(self.date)
        self.total_wealth['tot_wealth'].append( self._wealth + self.price*self.holdings )

    def Handle_signal(self,signal,amount):
        if signal is None or amount is None:
            self.Long_signal.append(0)
            self.Short_signal.append(0) 
        else:
            if  signal == 'Long':
                self.holdings += amount
                self._wealth -= amount*self.price 
                self.Long_signal.append(1)
                self.Short_signal.append(0)
                
            elif signal == 'Short':
                self.holdings -= amount
                self._wealth += amount*self.price  
                self.Long_signal.append(0)
                self.Short_signal.append(1)
        self.Naive_update()
    
    def convertStringToJSON(self, st):
        return json.dumps(st)

    def start(self,Trading_Strat,reset=True):
        if reset:
            self.RESET_ALL()
        for item in tqdm(self.streaming_db):#<-----------Receive streaming data from server
            self.price = float(item[self.price_tag])
            self.date = DATE(item[self.date_tag])
            #Executing the algo 
            item['holdings'] = self.holdings
            feed = (self.convertStringToJSON(item)).encode('utf-8')
            Order  = Trading_Strat(feed,self._wealth)
            try:
                direction,amount = Order['Direction'],Order['Amount']
            except:
                direction,amount  = None,None
            self.Handle_signal( direction,amount )

    def Get_history(self):
        DCT = self._wealth_track.copy()
        DCT['holdings'] = self.holding_track['holdings']
        DCT['Total Wealth'] = self.total_wealth['tot_wealth']
        DCT['Long'] = self.Long_signal.copy()
        DCT['Short'] = self.Short_signal.copy()
        return pd.DataFrame(DCT)

    def Plot_history(self,additional_data_list = [],legends_list = []):
        import matplotlib as mpl
        import matplotlib.dates as mdates
        from matplotlib.dates import DateFormatter

        font_name = "STKaiti"
        mpl.rcParams['font.family']=font_name
        mpl.rcParams['axes.unicode_minus']=False # in case minus sign is shown as box
        font = {'size'   : 12}

        mpl.rc('font', **font)
        ############################
        df = self.Get_history()
        fig, ax = plt.subplots(figsize=(16, 9))
        ax.plot(df['date'],df['Total Wealth'])
        price_move = Normalize_by(self.price_db[self.price_tag],df['Total Wealth'].max())
        ax.plot(df['date'],price_move)#<-------BTC

        LONG_LST1 = [i for i in df.Long.multiply(price_move) if i != 0 ]
        SHORT_LST1 = [i for i in df.Short.multiply(price_move) if i != 0 ]
        LONG_LST2 = [i for i in df.Long.multiply(df['Total Wealth']) if i != 0 ]
        SHORT_LST2 = [i for i in df.Short.multiply(df['Total Wealth']) if i != 0 ]


        ax.set(xlabel="Date", ylabel="Total Wealth",title="Algo Performance")

        
        ax.plot(self.holding_track['date'],Normalize_by(self.holding_track['holdings'],df['Total Wealth'].max()))#,kind='bar')
        # Format the x axis
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=max(1,int(df.shape[0]/35))))
        ax.xaxis.set_major_formatter(DateFormatter("%y-%m-%d"))
        
        for dt in additional_data_list:
            ax.plot(df['date'],Normalize_by(dt,df['Total Wealth'].max()))
            
        ####
        ax.scatter(df.query('Long == 1')['date'],LONG_LST1,marker = '^',color = 'green')
        ax.scatter(df.query('Short == 1')['date'],SHORT_LST1,marker = 'v',color = 'red')
        ####
        ax.scatter(df.query('Long == 1')['date'],LONG_LST2,marker = '^',color = 'green')
        ax.scatter(df.query('Short == 1')['date'],SHORT_LST2,marker = 'v',color = 'red')
        
        plt.legend(['Total Wealth','Stock Price Normalized','Holdings','Long Signal','Short Signal'] + legends_list)
        return fig
    
def sendCSVfile(data_file_path):
    out = []
    csvfile = open(data_file_path, 'r')
    reader = csv.DictReader(csvfile)
    for row in reader:
        out += [row]
    return out

#Trading Algo Library
def Random_algo(received,current_wealth,Rnd_seed = None):
    import random 
    #time,price,current_holdings,
    try:
        received = received.replace("'",'"')
    except TypeError:
        pass 
    received = json.loads(received)
    time = received['date']
    price = float(received['close'])
    current_holdings = float(received['holdings'])
    if Rnd_seed is None:
        Rnd_seed = abs(hash(str(time))) % (10 ** 8)
    random.seed(Rnd_seed) #To ensure re-creatability
    fraction = 0.1 #Assume to be fixed ratio, could try kelly queritieron in future
    direction = random.choice(['Long','Short','Do Nothing'])
    #When long,buy stock amount such that value equal to fraction of current wealth
    if direction == 'Long':
        amount = fraction * current_wealth / price
    elif direction == 'Short':
        amount = current_holdings #Assume we sell all for now 
    else:
        #print(f'<{time}>:Do Nothing')
        return None
    #print(f'<{time}>:{direction} {amount} BTC')
    return {'Direction': direction, 'Amount':amount} #3,4

class Moving_Avg:
    def __init__(self,fraction = 0.1):
        self.price_history = pd.DataFrame({'date':[],'price':[]}) 
        self.last_50_days = []
        self.last_20_days = []
        self.MA50 = [0 for i in range(49)]
        self.MA20 = [0 for i in range(49)]
        self.fraction = fraction

    def Update_50days(self,price):
        if len(self.last_50_days) < 50:
            self.last_50_days.append(price)
        else:
            self.last_50_days = self.last_50_days[1:] + [price]

    def Update_20days(self,price):
        if len(self.last_20_days) < 20:
            self.last_20_days.append(price)
        else:
            self.last_20_days = self.last_20_days[1:] + [price]

    def Signal_Changed(self):
        self.MA50.append(np.average(self.last_50_days))
        self.MA20.append(np.average(self.last_20_days))
        current_signal = np.average(self.last_50_days) < np.average(self.last_20_days)
        return current_signal != self.signal

    def send_signal(self,received,current_wealth):
        try:
            received = received.replace("'",'"')
        except TypeError:
            pass 
        received = json.loads(received)
        time = received['date']
        price = float(received['close'])
        current_holdings = float(received['holdings'])
        self.Update_20days(price)
        self.Update_50days(price)
        if  len(self.last_50_days) < 50 or len(self.last_20_days) < 20:
            out = None #<------------------------------------------------Return None,None if do nothing
        else:
            if self.Signal_Changed():
                #print('Signal Changed!')
                if np.average(self.last_50_days) < np.average(self.last_20_days):
                    out = {'Direction': 'Short', 'Amount':current_holdings}
                else:
                    out = {'Direction': 'Long', 'Amount':self.fraction * current_wealth / price}
            else:
                out = None
        self.signal = np.average(self.last_50_days) < np.average(self.last_20_days)
        return out 

class TWT_BTC:
    def __init__(self,hist_data_btc = None,model = LinearRegression(),
                 pred_n = 1,use_hist_price = False,
                shreshold = 0.01,fraction_long=0.2,fraction_short = 0.1,
                Smile_Principle = True, n_days = 2):
        #1.database of BTC,TWT_Vol,Google_T
        self.current_data = hist_data_btc
        #2.Set trading params
        self.use_hist_price = use_hist_price
        self.shreshold = shreshold
        self.n_days = n_days
        self.fraction_long = fraction_long
        self.fraction_short = fraction_short
        self.Smile_Principle = Smile_Principle
        #3.Initializingt streaming data
        if hist_data_btc is not None:
            self.Last_streaming_data = {k:v for v,k in zip(self.current_data.tail(1).values[0],self.current_data.tail(1).keys())}
        else:
            self.Last_streaming_data = None 
        self.pred_n = pred_n
        self.Data_Eng()
        #4.Train the model
        self.Use_Model(model)
        self.Fit()
        #5.Keep track of prediction
        self.y_pred = {'date':[],'price_pred':[]}
    
    def Use_Model(self,clf):
        #Here is a list of potential models 
        #DecisionTreeRegressor(min_samples_leaf=10, min_samples_split=5) 0.7588140950179767
        #LinearSVR(epsilon=0.03) -0.28257581407114063
        #GradientBoostingRegressor(min_samples_split=20)
        self.clf = clf

    def Data_Eng(self,df = None):
        if df is None:
            df = self.current_data.copy()
        try:
            df.insert(len(df.columns), 'future_price', df.close.shift(-self.pred_n))
        except ValueError:
            pass
        return df.dropna() 

    def Fit(self):
        X,y = self.Get_Xy(self.Data_Eng(self.current_data))
        self.clf.fit(X,y)

    def Get_Xy(self,df,col_drop = ['future_price','close','date'],y_name = 'future_price',Standardize = False):
        X = df.copy()
        for var in col_drop:
            try:
                if self.use_hist_price:
                    if var != 'close':
                        X = X.drop(var,axis = 1)
                else:
                    X = X.drop(var,axis = 1)
            except:
                pass
        y = df[y_name]
        if Standardize:#Normalize X
            ss = StandardScaler()
            X = ss.fit_transform(X) 
        return X,y

    def df_Update(self,received):
        "Update database with received streaming data"
        self.Last_streaming_data['future_price'] = received['close'] #Now yesterday's tmr's price is realized
        self.current_data = pd.concat([self.current_data.dropna(),pd.DataFrame({key:[var] for key,var in self.Last_streaming_data.items()})])
        self.current_data = self.current_data.reset_index( drop = True )

        self.holdings = float(received.pop('holdings'))
        self.Last_streaming_data = received #Dict WITHOUT future_price
        
    def Price_Trend(self):
        n_days = self.n_days
        temp = self.current_data[-n_days:].close.rolling(2).apply(lambda x:list(x)[0]<list(x)[1])
        if temp.sum() == n_days-1:#Consecutive increase
            return 1
        elif temp.sum() == 0:#Consecutive Decrease
            return -1 
        
    def send_signal(self,received,current_wealth):
        try:
            received = received.replace("'",'"')
        except TypeError:
            pass 
        received = json.loads(received)
        try:
            received.pop('')
        except:
            pass
        #1.Update our existing model based on streaming data
        self.df_Update(received)
        #2.Predict the price n days later (Which is our Y)
        self.Fit() #Fit a new model 
        df_clean  = self.current_data.tail(1)
        X_test,_ = self.Get_Xy(df_clean)
        price_pred = self.clf.predict(X_test)[0]
        self.y_pred['date'].append(received['date'])
        self.y_pred['price_pred'].append(price_pred)
        #3.Generate an direction
        Spread = (price_pred-float(received['close']))/float(received['close'])
        price_trend = self.Price_Trend()
        if self.Smile_Principle:
            #print(price_trend,Spread)
            #S2:Increase for n days straight & predicted decrease
            if price_trend == 1:
                if Spread < 0: #Tmr's price will be lower, consecutive decreasing 
                    Direction = 'Short'
                    Amount = self.fraction_short*self.holdings
                else:
                    return #No Order
            #S1:Decrease for n days straight & predicted increase
            elif price_trend == -1:
                if Spread < 0: #Tmr's price will be lower
                    return #No Order
                else:
                    Direction = 'Long'
                    Amount = self.fraction_long*current_wealth/float(received['close']) 
            else:
                return None #No Order
        else:
            if abs(Spread) > self.shreshold:
                if Spread > 0: #Tmr's price will be HIGHER
                    Direction = 'Long'
                    Amount = self.fraction_long*current_wealth/float(received['close'])
                else:
                    Direction = 'Short'
                    Amount = self.fraction_short*self.holdings
            else:
                return None #No Order
        #4.Decide the amount of trading (Reaserch)
        try:
            Order = {'Direction': Direction, 'Amount':Amount} #3,4
            return Order
        except UnboundLocalError:
            return 
        
class Cheater:
    def __init__(self,data_base,predict = True,
                shreshold = 0,fraction_long=0.2,fraction_short = 0.1,
                Smile_Principle = True, n_days = 2):
        #1.database of BTC,TWT_Vol,Google_T
        self.db = data_base
        #2.Set trading params
        self.shreshold = shreshold
        self.n_days = n_days
        self.fraction_long = fraction_long
        self.fraction_short = fraction_short
        self.Smile_Principle = Smile_Principle
        self.predict = predict
        
        
    def Price_Trend(self,date_tmr):
        n_days = self.n_days
        temp = self.db.query(f'date < "{date_tmr}"')[-n_days-1:].close.rolling(2).apply(lambda x:list(x)[0]<list(x)[1])
        if temp.sum() == n_days:#Consecutive increase
            return 1
        elif temp.sum() == 0:#Consecutive Decrease
            return -1 
    
    def send_signal(self,received,current_wealth,Rnd_seed = None):
        import random 
        #time,price,current_holdings,
        try:
            received = received.replace("'",'"')
        except TypeError:
            pass 
        received = json.loads(received)
        time = received['date']
        price = float(received['close'])
        current_holdings = float(received['holdings'])
        self.holdings = current_holdings

        tmr = str(DATE(time) + timedelta(days=1))
        
        try:
            price_tmr = float(self.db.query(f'date == "{tmr}"').close)
            #print(price_tmr)
        except Exception as e :
            print(e)
            print(f"Tmr {tmr} not found...")
            price_tmr = price
        if self.predict:
            Spread = price_tmr - price
            price_trend = self.Price_Trend(tmr)
            ###################SMILE:
            if self.Smile_Principle:
                #print(price_trend,Spread)
                #S2:Increase for n days straight & predicted decrease
                if price_trend == 1:
                    if Spread < 0: #Tmr's price will be lower, consecutive decreasing 
                        Direction = 'Short'
                        Amount = self.fraction_short*self.holdings
                    else:
                        return #No Order
                #S1:Decrease for n days straight & predicted increase
                elif price_trend == -1:
                    if Spread < 0: #Tmr's price will be lower
                        return #No Order
                    else:
                        Direction = 'Long'
                        Amount = self.fraction_long*current_wealth/float(received['close']) 
                else:
                    return None #No Order
            else:
                if abs(Spread) > self.shreshold:
                    if Spread > 0: #Tmr's price will be HIGHER
                        Direction = 'Long'
                        Amount = self.fraction_long*current_wealth/float(received['close'])
                    else:
                        Direction = 'Short'
                        Amount = self.fraction_short*self.holdings
                else:
                    #4.Decide the amount of trading (Reaserch)
                    return None #No Order
        else:
            Spread = price_tmr - price
            price_trend = self.Price_Trend(tmr)
            ###################SMILE:
            if self.Smile_Principle:
                #S2:Increase for n days straight & predicted decrease
                if price_trend == 1:
                    Direction = 'Short'
                    Amount = self.fraction_short*self.holdings
                #S1:Decrease for n days straight & predicted increase
                elif price_trend == -1:
                    Direction = 'Long'
                    Amount = self.fraction_long*current_wealth/float(received['close']) 
                else:
                    return None #No Order
        
        try:
            Order = {'Direction': Direction, 'Amount':Amount} #3,4
            return Order
        except UnboundLocalError:
            return 
        
#######
if __name__ == '__main__':
    #Collect data subsets 
    # df_all = pd.read_csv('BTC_TWT_GC.csv')
    # df_pre2020 = df_all.query('date < "2020-01-01"')
    # df_Post2020 = df_all.query('date >= "2020-01-01"')
    # df_Post2020.to_csv('df_Post2020.csv')

    # df_pre_bull =  df_all.query('date >= "2021-07-01"')
    # df_post_bull =  df_all.query('date >= "2021-07-01"')
    # df_post_bull.to_csv('df_post_bull.csv')

    # df_pre_bear =  df_all.query('date  >= "2021-04-01"')
    # df_post_bear =  df_all.query('date  >= "2021-04-01"')
    # df_post_bear.to_csv('df_post_bear.csv')
    #

    # t = BackTester('df_Post2020.csv',initial_wealth = 1e10) #Initialize the BackTesting system
    # CT = Cheater(df_all,n_days=2)
    # t.start(CT.send_signal)
    # result = t.total_wealth['tot_wealth'][-1]
    # fig = t.Plot_history()
    # plt.show()
    #
    df_dummy = pd.read_csv('df_dummy.csv')

    CT = Cheater(df_dummy,n_days=2,predict=True)#False
    t = BackTester('df_dummy.csv',initial_wealth = 1e10)
    t.start(CT.send_signal)
    result = t.total_wealth['tot_wealth'][-1]
    fig = t.Plot_history()
    plt.show()

    CT2 = Cheater(df_dummy,n_days=2,predict=False)#False
    t.start(CT2.send_signal)
    result = t.total_wealth['tot_wealth'][-1]
    fig = t.Plot_history()
    plt.show()