import fun_file
import pandas as pd
from SmartApi import SmartConnect

#1. Login
authToken,feedToken,refreshToken = fun_file.login()
#2. init TOCKEN_MAP
token_df=fun_file.intializeSymbolTokenMap()
print(token_df)
#4. User Choice for selection
dff,e_seg=fun_file.user_selection()
if dff.empty:
    print('No match found ...Try again')
    fun_file.user_selection()
else:
    print(dff)
#5. Get historical data from the server
tocken=int(input('enter the tocken value to load Historic data'))
print("Defaut setting for 30 days , 10 min candle data")
hd=fun_file.get_tocken_his_data(e_seg,tocken)
print(hd)


'''    
#tokenInfo = getTokenInfo('NFO','NIFTY','OPTIDX',22500,'CE').iloc[0]
#tt = getTokenInfo('NSE','TATA')      

#Fetching the historical data
thirty_days_ago = datetime.now() - timedelta(days=30)
from_date = thirty_days_ago.strftime("%Y-%m-%d %H:%M")
to_date = datetime.now().strftime("%Y-%m-%d %H:%M")

historicParam={
"exchange": "NSE",
"symboltoken": 18143,
"interval": "TEN_MINUTE",
"fromdate": from_date, 
"todate": to_date
}

his_df=fun_file.get_tocken_data(historicParam)
print(his_df)
'''
