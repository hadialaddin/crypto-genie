import math
import json
from types import SimpleNamespace
import logging
from time import sleep
import time
from pybit import HTTP, WebSocket

###### Configurations (EDIT)
api_key = 'TYPE BYBIT API KEY HERE'
api_secret = 'TYPE BYBIT API SECRET HERE'
Test = True # Set to False to use the Mainnet, or False to use the Testnet
default_stop_loss_cap_ratio = 10.0 # Maximum Stop Loss % allowed (ratio of price difference, after leverage)
override_stop_loss_cap_ratio = { # Use this to set custom Stop Loss % for specific asset pairs (override the default), you can add more pairs as you desire by adding a comma at the end and a new symbol
  "BTCUSDT": 20.0,
  "ETHUSDT": 5.0
} 

########################################################
# ////////// No need to edit below this line //////////#

###### ByBit Base Endpoints (only edit if they don't match the currently published ones by ByBit at: https://bybit-exchange.github.io/docs/linear/#t-websocket
wsURL_USDT_mainnet = "wss://stream.bybit.com/realtime_private"
wsURL_USDT_testnet = "wss://stream-testnet.bybit.com/realtime_private"
wsURL_Inverse_mainnet = "wss://stream.bybit.com/realtime"
wsURL_Inverse_testnet = "wss://stream-testnet.bybit.com/realtime"
sessionURL_mainnet = "https://api.bybit.com"
sessionURL_testnet = "https://api-testnet.bybit.com"
######

if Test == True:
    wsURL_USDT = wsURL_USDT_testnet
    wsURL_Inverse = wsURL_Inverse_testnet
    sessionURL = sessionURL_testnet
else:
    wsURL_USDT = wsURL_USDT_mainnet
    wsURL_Inverse = wsURL_Inverse_mainnet
    sessionURL = sessionURL_mainnet

if __name__ == "__main__":
    
    session = HTTP(endpoint=sessionURL, api_key=api_key, api_secret=api_secret)
    tick_size = {}

    for symbol in session.query_symbol()["result"]:
        tick_size[symbol["name"]] = symbol["price_filter"]["tick_size"]

    ws_USDT = WebSocket(wsURL_USDT, subscriptions=['position'], api_key=api_key, api_secret=api_secret)
    ws_Inverse = WebSocket(wsURL_Inverse, subscriptions=['position'], api_key=api_key, api_secret=api_secret)
    
    while(1):
        fetched_websockets = []
        
        # Fetch USDT positions
        fetched_positions = ws_USDT.fetch('position')
        if(fetched_positions):
            positions = json.loads(json.dumps(fetched_positions, default=lambda s: vars(s)))
            
            for coins, coin_data in positions.items():
                for side, position in coin_data.items():
                    fetched_websockets.append(position)
        
        # Fetch Inverse positions
        fetched_positions = ws_Inverse.fetch('position')
        if fetched_positions:
            positions = json.loads(json.dumps(fetched_positions, default=lambda s: vars(s)))
            
            for coin, position in positions.items():
                fetched_websockets.append(position)

        # Now we set Stop Losses
        for position in fetched_websockets:
            symbol = position["symbol"]
            side = position["side"]
            leverage = float(position["leverage"])
            stop_loss = float(position["stop_loss"])
            entry_price = float(position["entry_price"])
            
            final_decimals_count = str(tick_size[symbol])[::-1].find('.') - 1 # Tick Size number of decimals - 1
            
            if symbol in override_stop_loss_cap_ratio: # Look if any custom stop ratio for this symbol
                stop_loss_cap_ratio = override_stop_loss_cap_ratio[symbol]
            else:
                stop_loss_cap_ratio = default_stop_loss_cap_ratio
            
            if side == 'Buy':
                position_leveraged_stop_loss = round((entry_price - ((stop_loss_cap_ratio/100) / leverage * entry_price)), final_decimals_count)
                if stop_loss == 0 or stop_loss < position_leveraged_stop_loss:
                    try:
                        session.set_trading_stop(symbol=symbol, side=side, stop_loss=position_leveraged_stop_loss)
                        print(symbol + " LONG Stop-Loss adjusted: "+str(position_leveraged_stop_loss)+" (" + str(stop_loss_cap_ratio) + "%)")
                    except Exception:
                        pass
            elif side == 'Sell':
                position_leveraged_stop_loss = round((entry_price + ((stop_loss_cap_ratio/100) / leverage * entry_price)), final_decimals_count)
                if stop_loss == 0 or stop_loss > position_leveraged_stop_loss:
                    try:
                        session.set_trading_stop(symbol=symbol, side=side, stop_loss=position_leveraged_stop_loss)
                        print(symbol + " SHORT Stop-Loss adjusted: "+str(position_leveraged_stop_loss)+" (" + str(stop_loss_cap_ratio) + "%)")
                    except Exception:
                        pass

        sleep(1)