import math
import json
from types import SimpleNamespace
import logging
from time import sleep
import time
from datetime import datetime
from pybit import HTTP, WebSocket

###### Configurations (EDIT)
api_key = 'R2RZqlWU2N5tDoIYAz'
api_secret = 'NrkyuSYWTeLlNYjREf74obOTBmK72CAAsbfu'
Test = True # Set to False to use the Mainnet, or False to use the Testnet

enforce_stop_loss_range = True # Enforce Stop Loss Range feature switch (True/False)
default_stop_loss_cap_ratio = 10.0 # Maximum Stop Loss % allowed (ratio of price difference, after leverage)
override_stop_loss_cap_ratio = { # Use this to set custom Stop Loss % for specific asset pairs (override the default), you can add more pairs as you desire by adding a comma at the end and a new symbol
  "BTCUSDT": 5.0,
  "ETHUSDT": 5.0,
  "SHIB1000USDT": 1.0
}

#################################################################################################################
#################################################################################################################
############################# ////////// No need to edit below this line ////////// #############################
#################################################################################################################
#################################################################################################################

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
        
    ''' *** We wil not use WebSockets for now, only REST API due to missing fields in the WebSocket API ***
    ws_USDT = WebSocket(wsURL_USDT, subscriptions=['position'], api_key=api_key, api_secret=api_secret)
    ws_Inverse = WebSocket(wsURL_Inverse, subscriptions=['position'], api_key=api_key, api_secret=api_secret)
    
    while(1):
        # Fetch Active Positions through WebSockets (USDT and Inverse)
        fetched_websockets = []
        
        fetched_positions = ws_USDT.fetch('position')
        if(fetched_positions):
            positions = json.loads(json.dumps(fetched_positions, default=lambda s: vars(s)))
            
            for coins, coin_data in positions.items():
                for side, position in coin_data.items():
                    fetched_websockets.append(position)
        
        fetched_positions = ws_Inverse.fetch('position')
        if fetched_positions:
            positions = json.loads(json.dumps(fetched_positions, default=lambda s: vars(s)))
            
            for coin, position in positions.items():
                fetched_websockets.append(position)
        
        # Now we set Stop Losses
        for position in fetched_websockets:
        '''
        
    while(1):    
        # Fetch list of active positions
        fetched_sessions = []
        
        fetched_positions = session.my_position(endpoint="/private/linear/position/list")['result'] # USDT Perpetual
        if(fetched_positions):
            for position in fetched_positions:
                if position['is_valid'] == True and position['data']["size"] > 0: # Required per the ByBit API to be is_valid=True data, and we only want the active positions (size>0)
                    fetched_sessions.append(position['data'])
                    
        fetched_positions = session.my_position(endpoint="/v2/private/position/list")['result'] # Inverse Perpetual
        if(fetched_positions):
            for position in fetched_positions:
                if position['is_valid'] == True and position['data']["size"] > 0: # Required per the ByBit API to be is_valid=True data, and we only want the active positions (size>0)
                    fetched_sessions.append(position['data'])
                     
        fetched_positions = session.my_position(endpoint="/futures/private/position/list")['result'] # Inverse Futures
        if(fetched_positions):
            for position in fetched_positions:
                if position['is_valid'] == True and position['data']["size"] > 0: # Required per the ByBit API to be is_valid=True data, and we only want the active positions (size>0)
                    fetched_sessions.append(position['data'])
         
        for position in fetched_sessions:
            position_idx = ""
            mode = ""
            
            symbol = position["symbol"]
            side = position["side"]
            size = float(position["size"])
            leverage = float(position["leverage"])
            stop_loss = float(position["stop_loss"])
            entry_price = float(position["entry_price"])
            final_decimals_count = str(tick_size[symbol])[::-1].find('.') - 1 # Tick Size number of decimals - 1
            tp_sl_mode = position["tp_sl_mode"] # "Partial" or "Full" position TP/SL mode [Currently not supported in WebSocket API]
            if "position_idx" in position:
                position_idx = position["position_idx"] # 0 for One-Way Mode, 1 for Buy in Hedge Mode, 2 for Sell in Hedge Mode [Currently not supported in WebSocket API]
            if "mode" in position:
                mode = position["mode"] # 0 for One-Way Mode, 3 for Hedge Mode
            
            
            
            # Enforce Stop Loss Range feature
            if(enforce_stop_loss_range):
                if symbol in override_stop_loss_cap_ratio: # Look if any custom stop ratio for this symbol
                    stop_loss_cap_ratio = override_stop_loss_cap_ratio[symbol]
                else:
                    stop_loss_cap_ratio = default_stop_loss_cap_ratio

                # FIRST check if immediate market close is needed in case price already breached with no Stop Loss in place
                # Fetch latest tickers
                fetched_latest_tickers = session.latest_information_for_symbol(symbol=symbol)['result']
                if(fetched_latest_tickers):
                    for ticker in fetched_latest_tickers:
                        if ticker['symbol'] == symbol:
                            last_price = float(ticker['last_price'])
                            
                        if side == 'Buy':
                            position_leveraged_stop_loss = round((entry_price - ((stop_loss_cap_ratio/100) / leverage * entry_price)), final_decimals_count)
                            if last_price < position_leveraged_stop_loss:
                                try:
                                    session.place_active_order(symbol=symbol, side="Sell", order_type="Market", qty=size, time_in_force="GoodTillCancel", reduce_only=True, close_on_trigger=True)
                                    log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + symbol + " LONG Force-Stopped: "+str(last_price)+"."
                                    print(log)
                                    with open("SL_forced.txt", "a") as myfile:
                                        myfile.write(log+'\n')
                                except Exception:
                                    pass
                        elif side == 'Sell':
                            position_leveraged_stop_loss = round((entry_price + ((stop_loss_cap_ratio/100) / leverage * entry_price)), final_decimals_count)
                            if last_price > position_leveraged_stop_loss:
                                try:
                                    session.place_active_order(symbol=symbol, side="Buy", order_type="Market", qty=size, time_in_force="GoodTillCancel", reduce_only=True, close_on_trigger=True)
                                    log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + symbol + " SHORT Force-Stopped: "+str(last_price)+"."
                                    print(log)
                                    with open("SL_forced.txt", "a") as myfile:
                                        myfile.write(log+'\n')
                                except Exception:
                                    pass


                # Otherwise, search Conditional Orders if Stop Loss already exists with 'qty'=position size AND 'trigger_price' >= within allowed range
                total_allowed_stop_loss_found = 0.0
                conditional_stop_loss_orders_ids = [] # Used to store the stop_order_id of the Stop Losses that need to be cleared if no satisfying one found
                
                fetched_conditional_orders = session.query_conditional_order(symbol=symbol)
                if(fetched_conditional_orders):
                    for conditional_order in fetched_conditional_orders["result"]:
                        # Note: order side should be opposite of position size
                        if side == "Buy" and conditional_order['side'] == "Sell" and conditional_order['order_type'] == 'Market' and conditional_order['order_status'] == 'Untriggered': # Stop Loss for a Long
                            if symbol.endswith('USDT'): # USDT Perpetual
                                stop_price = float(conditional_order['trigger_price'])
                                stop_order_id = conditional_order['stop_order_id']
                                if stop_price < entry_price and conditional_order['close_on_trigger'] == True and conditional_order['reduce_only'] == True:
                                    position_leveraged_stop_loss = round((entry_price - ((stop_loss_cap_ratio/100) / leverage * entry_price)), final_decimals_count)
                                    if stop_price >= position_leveraged_stop_loss:
                                        # Stop Loss found inside the allowed range, keep it
                                        total_allowed_stop_loss_found += float(conditional_order['qty'])
                                    else:
                                        # Stop Loss found outside the allowed range, useless so remove it
                                        session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id) 
                                        
                            else: # Inverse Perpetuals or Futures
                                stop_price = float(conditional_order['stop_px'])
                                stop_order_id = conditional_order['order_id']
                                position_leveraged_stop_loss = round((entry_price - ((stop_loss_cap_ratio/100) / leverage * entry_price)), final_decimals_count)
                                if stop_price >= position_leveraged_stop_loss:
                                    # Stop Loss found inside the allowed range, keep it
                                    total_allowed_stop_loss_found += float(conditional_order['qty'])
                                else:
                                    # Stop Loss found outside the allowed range, useless so remove it
                                    session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id) 

                        
                        
                        
                        elif side == "Sell" and conditional_order['side'] == "Buy" and conditional_order['order_type'] == 'Market' and conditional_order['order_status'] == 'Untriggered': # Stop Loss for a Short
                            if symbol.endswith('USDT'): # USDT Perpetual
                                stop_price = float(conditional_order['trigger_price'])
                                stop_order_id = conditional_order['stop_order_id']
                                if stop_price > entry_price and conditional_order['close_on_trigger'] == True and conditional_order['reduce_only'] == True:
                                    position_leveraged_stop_loss = round((entry_price + ((stop_loss_cap_ratio/100) / leverage * entry_price)), final_decimals_count)
                                    if stop_price <= position_leveraged_stop_loss:
                                        # Stop Loss found inside the allowed range, keep it
                                        total_allowed_stop_loss_found += float(conditional_order['qty'])
                                    else:
                                        # Stop Loss found outside the allowed range, useless so remove it
                                        session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id)
                            
                            else: # Inverse Perpetuals or Futures
                                stop_price = float(conditional_order['stop_px'])
                                stop_order_id = conditional_order['order_id']
                                position_leveraged_stop_loss = round((entry_price + ((stop_loss_cap_ratio/100) / leverage * entry_price)), final_decimals_count)
                                if stop_price <= position_leveraged_stop_loss:
                                    # Stop Loss found inside the allowed range, keep it
                                    total_allowed_stop_loss_found += float(conditional_order['qty'])
                                else:
                                    # Stop Loss found outside the allowed range, useless so remove it
                                    session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id) 
                            
                            
                            
                # We couldn't find enough Stop Losses in the allowed range, so add the remaining needed
                if total_allowed_stop_loss_found < size:
                    # Prepare set_trading_stop arguments to pass to API
                    set_trading_stop_args = {'symbol': symbol, 'side': side}
                    if tp_sl_mode == "Partial":
                        set_trading_stop_args['sl_size'] = size # If Partial Mode then we need to send full size to close full position
                    
                    if side == 'Buy':
                        position_leveraged_stop_loss = round((entry_price - ((stop_loss_cap_ratio/100) / leverage * entry_price)), final_decimals_count)
                        if stop_loss == 0 or stop_loss < position_leveraged_stop_loss:
                            try:
                                #session.place_conditional_order(symbol=symbol, order_type="Market", reduce_only=True, side= "Sell", qty=size, stop_px=position_leveraged_stop_loss,time_in_force="GoodTillCancel")
                                set_trading_stop_args['stop_loss'] = position_leveraged_stop_loss
                                session.set_trading_stop(**set_trading_stop_args)
                                log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + symbol + " LONG Maximum Stop-Loss adjusted to: "+str(position_leveraged_stop_loss)+" (" + str(stop_loss_cap_ratio) + "%)."
                                print(log)
                                with open("SL_protected.txt", "a") as myfile:
                                    myfile.write(log+'\n')
                            except Exception:
                                pass
                    elif side == 'Sell':
                        position_leveraged_stop_loss = round((entry_price + ((stop_loss_cap_ratio/100) / leverage * entry_price)), final_decimals_count)
                        if stop_loss == 0 or stop_loss > position_leveraged_stop_loss:
                            try:
                                #session.place_conditional_order(symbol=symbol, order_type="Market", reduce_only=True, side= "Buy", qty=size, stop_px=position_leveraged_stop_loss,time_in_force="GoodTillCancel")
                                set_trading_stop_args['stop_loss'] = position_leveraged_stop_loss
                                session.set_trading_stop(**set_trading_stop_args)
                                log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + symbol + " SHORT Maximum Stop-Loss adjusted to: "+str(position_leveraged_stop_loss)+" (" + str(stop_loss_cap_ratio) + "%)."
                                print(log)
                                with open("SL_protected.txt", "a") as myfile:
                                    myfile.write(log+'\n')
                            except Exception:
                                pass
        sleep(1)
