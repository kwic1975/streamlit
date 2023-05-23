import streamlit as st
import requests
import pandas as pd
import datetime
import pandas


tmzone = "US/Eastern"

apiroot = 'https://api.coingecko.com/api/v3'
apikey = ''
dex='uniswap_v3'
volume=1.5e5
lag=6

@st.cache_data(ttl=datetime.timedelta(hours=8))
def get_coin_gecko_data(url):
    response_API=requests.get(f"{url}/exchanges/{dex}",  timeout=10).json()["tickers"]
    return response_API

response_API=get_coin_gecko_data(apiroot)

vols = pd.Series(dtype=float)
for i in response_API:
    id_ = i["coin_id"] 
    vols.loc[id_] = i["converted_volume"]["usd"]

vols = vols.sort_values(ascending=False)
list_coins=vols.index.to_list()

st.button('Connect Wallet')
with st.form("my_form"):
    
    DEX = st.selectbox('Select DEX',('Uniswap',))

    Chain = st.selectbox('Select Chain',('Ethereum', 'Arbitrum', 'Polygon'))

    Coin = st.selectbox('Select Coin',list_coins,index=1)

    Direction = st.radio("Select Position",('LONG', 'SHORT',))

    Price = st.number_input('Please provide the Price in USD at which entry order was filled', min_value=0.0000,step=0.0000000001,format='%.12f')

    Qty = st.slider('Set Qty as percentage of your holding', 0.10, 1.00, 1.00, step=0.10)

    Target = st.slider('What is your profit target?', 0.00, 0.99, 0.05, step=0.01)


    Stop = st.slider('What is your Stop?', 0.00, 0.99, 0.05, step=0.01)


    Delay = st.slider('What is your Stop Delay in minutes?', 0, 180, 60, step=30)


    Speed = st.slider('What is your Trail Speed?', 0.00, 2.00, 1.00, step=0.25)


    Smoothing = st.select_slider('What Smoothing function should be used?', options=['SMA','None','EMA'],value=('None'))

    submitted = st.form_submit_button("Submit")
    if submitted:
       st.write("Done", DEX,Chain,Coin,Direction,Price,Qty,Target,Stop,Delay,Speed,Smoothing)
       price_API=requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={Coin}&vs_currencies=usd&include_last_updated_at=true&precision=18",).json()
       price_df = pd.DataFrame()
       for k in price_API:
           price_df.loc[k, "USD_PX_LAST"] = price_API[k]["usd"]
           price_df.loc[k, "PX_LAST_DTTM"] = price_API[k]["last_updated_at"]  
           price_df[ "PX_LAST_DTTM"]=pandas.to_datetime(price_df['PX_LAST_DTTM'],unit='s')
           price_df[ "PX_LAST_DTTM"]=price_df["PX_LAST_DTTM"].dt.tz_localize('UTC').dt.tz_convert(tmzone)
       PX_LAST=price_df['USD_PX_LAST'][0]
       if PX_LAST>= Price*(1+Target) :
            st.write(price_df['USD_PX_LAST'][0],price_df['PX_LAST_DTTM'][0],"Error-Market is above Target") 
       elif PX_LAST<= Price*(1-Stop) :
            st.write(price_df['USD_PX_LAST'][0],price_df['PX_LAST_DTTM'][0],"Error-Market is below Stop") 
       else:
            st.write(price_df['USD_PX_LAST'][0],price_df['PX_LAST_DTTM'][0],"OK-Market is between Target and Stop")  





