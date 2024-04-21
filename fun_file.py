from SmartApi import SmartConnect
from logzero import logger
import pyotp
import requests
import pandas as pd
from datetime import datetime
import requests
import numpy as np
import credentials
import os.path
from datetime import datetime, timedelta


smartApi = SmartConnect(credentials.API_HIS_KEY)
#1. Login function
def login():
    try:
        token = credentials.QR_VAL
        totp = pyotp.TOTP(token).now()
    except Exception as e:
        logger.error("Invalid Token: The provided token is not valid.")
        raise e
    data = smartApi.generateSession(credentials.USER_NAME,credentials.PIN,totp)
    if data['status'] == False:
        logger.error(data)
    else:
        authToken = data['data']['jwtToken']
        refreshToken = data['data']['refreshToken']
        feedToken = smartApi.getfeedToken()		
		#fetch User Profile
		#logger.info(f"You Credentials: {data}")
		#res = smartApi.getProfile(refreshToken)
        smartApi.generateToken(refreshToken)
        res = smartApi.getProfile(refreshToken)
        print(res['data']['name'])
		#res=res['data']['exchanges']
    return authToken,feedToken,refreshToken

#2. Fetch the tocken JSON dataset (file) online from the AngelAPI 
def intializeSymbolTokenMap():
    path = './all_tocken_data.csv'
    if(os.path.isfile(path)):
        choice=input('Do you want to update the tocken copy type : Y|y or any key to cont...:  ')
        if (choice=='Y' or choice=='y'):
            url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
            d = requests.get(url).json()
            '''Put the data into dataframe '''
            token_df = pd.DataFrame.from_dict(d)
            #Convert it to datetime format
            token_df['expiry'] = pd.to_datetime(token_df['expiry'],format='mixed').apply(lambda x: x.date())
            #Convert strike to float format
            token_df = token_df.astype({'strike': float})
            credentials.TOKEN_MAP = token_df
            token_df.to_csv('all_tocken_data.csv')
            return token_df
        else:
            token_df = pd.read_csv('all_tocken_data.csv')
            credentials.TOKEN_MAP = token_df
            return token_df
    else:
        url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
        d = requests.get(url).json()
        '''Put the data into dataframe '''
        token_df = pd.DataFrame.from_dict(d)
        #Convert it to datetime format
        token_df['expiry'] = pd.to_datetime(token_df['expiry'],format='mixed').apply(lambda x: x.date())
        #Convert strike to float format
        token_df = token_df.astype({'strike': float})
        credentials.TOKEN_MAP = token_df
        token_df.to_csv('all_tocken_data.csv')
        return token_df        
        

#3. Search the tocken information for the JSON file which we stored in a var
def getTokenInfo(exch_seg,symbol, instrumenttype=None,strike_price=0,pe_ce=None):
    token_df=credentials.TOKEN_MAP
    df = token_df
    strike_price = strike_price*100
    if exch_seg == 'NSE' or exch_seg == 'BSE':
        #instrumenttype is null for Equity shares.
        eq_df = df[(df['exch_seg'] == 'NSE') & (df['symbol'].str.contains(symbol)) & (df['symbol'].str.contains('EQ')) ]
        return eq_df
    
    elif exch_seg == 'NFO' and ((instrumenttype == 'FUTSTK') or (instrumenttype == 'FUTIDX')):
        return df[(df['exch_seg'] == 'NFO') & (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol)].sort_values(by=['expiry'])

    elif exch_seg == 'NFO' and (instrumenttype == 'OPTSTK' or instrumenttype == 'OPTIDX'):
        return df[(df['exch_seg'] == 'NFO') & (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol) & (df['strike'] == strike_price) & (df['symbol'].str.endswith(pe_ce))].sort_values(by=['expiry'])

#4. Stock / Option Seelction
def user_selection():
    ch=input("Enter 1 or 2 \n1: STOCK (NSE)\n2: OPTION\n")
    if ch=='1':
        stockName=input("The name of stock").upper()
        tokenInfo=getTokenInfo('NSE',stockName)
        return tokenInfo,'NSE'
    elif ch=='2':
        ans = False
        while not ans:
            es=input("Enter NIFTY | BANKNIFTY").upper()
            if es== 'NIFTY' or es == 'BANKNIFTY':
                ans = True
            else:
                print("Invalid selection :( Please try again.")
        sp=int(input('Enter strike price'))
        anc = False
        while not anc:
            cp=input('CE or PE').upper()
            if cp== 'CE' or cp == 'PE':
                anc = True
            else:
                print("Invalid selection :( Please try again.")
        tokenInfo=getTokenInfo('NFO',es,'OPTIDX',sp,cp).iloc[0]
        return tokenInfo,'NFO'




#5. Fetching the historic data from SmartApi 
def get_tocken_his_data(exc_seg,symboltoken,interval="TEN_MINUTE",from_date=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M"),end_date=datetime.now().strftime("%Y-%m-%d %H:%M")):
    
    try:
        historicParam={
        "exchange": exc_seg,
        "symboltoken": str(symboltoken),
        "interval": interval,
        "fromdate": from_date, 
        "todate": end_date
        }        
        api_response = smartApi.getCandleData(historicParam)
        h_df = pd.DataFrame(api_response['data'],columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
    except Exception as e:
        print("Historic Api failed: {}".format(e.message))
    return h_df
