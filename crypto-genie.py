import math
import json
from types import SimpleNamespace
import logging
from time import sleep
import time
from datetime import datetime
from pybit import HTTP, WebSocket

###### Configurations (EDIT)
api_key = 'TYPE BYBIT API KEY HERE'
api_secret = 'TYPE BYBIT API SECRET HERE'
Test = True # Set to False to use the Mainnet, or False to use the Testnet
exchange_market_taker_fee = 0.075
exchange_market_maker_fee = -0.025

# Enforce Static Stop Loss at an exact ratio (not less not more) feature switch (True/False). Only exception is if position is in profit, it allows moving the SL to breakeven or profit.
enforce_sl_static = True
# Maximum Stop Loss % allowed (ratio of price difference, after leverage)
default_sl_static_cap_ratio = 5.0
# Use this to set custom Stop Loss % for specific asset pairs (override the default), you can add more pairs as you desire by adding a comma at the end and a new symbol
override_sl_static_cap_ratio = {
  "BTCUSDT": 5.0,
  "ETHUSDT": 5.0
}

# Enforce Stop Loss Range feature switch (True/False). NOTE: You should only activate either the Static Stop Loss feature or this one, not both, to avoid issues.
enforce_sl_range = False
# Maximum Stop Loss % allowed (ratio of price difference, after leverage)
default_sl_range_cap_ratio = 15.0
# Use this to set custom Stop Loss % for specific asset pairs (override the default), you can add more pairs as you desire by adding a comma at the end and a new symbol
override_sl_range_cap_ratio = {
  "BTCUSDT": 5.0,
  "ETHUSDT": 10.0,
  "SOLUSDT": 10.0,
  "XRPUSDT": 10.0
}

# Enforce Take Profits feature switch (True/False)
enforce_tp = False
# Default Initial TP levels (will be created only if no other TPs exist). Won't be enforced otherwise.
# Structure is init_tp_price_ratio (after leverage) : init_tp_position_ratio WHERE init_tp_position_ratio < 100
# NOTE: Order DOES NOT matter
default_hard_tp = False # If set to True, it will always enforce these TP's even if you cancel or edit them. If set to False, it will only create them as Soft ones if no TP exists for the position (upon position creation OR if all TP's are removed), and will allow you to move them around or change their values as you wish
default_market_tp = False # If set to True, it will ensure profits are taken as Market Orders instead of Limit Orders
default_tp = {
    25.0 : 25.0,
    50.0 : 10.0,
    100.0 : 25.0,
    150.0 : 25.0,
    200.0 : 25.0,
    300.0 : 100.0
}

# Enforce Lock In Profits Stop Loss feature switch (True/False)
enforce_lock_in_p_sl = True
# Default Lock In Profits Stop Loss levels (when price level ratio is hit, position's SL moved to defined price ratio). Note it is a Hard SL meaning you can't loose once you hit those profit levels.
# Structure is lock_in_p_price_ratio (after leverage): lock_in_p_sl_ratio
# NOTE: Order DOES matter. Make sure the order is in Ascending OR Descending on the left and right sides to avoid issues
default_lock_in_p_sl = {
    20.0 : 5.0,
    50.0 : 15.0,
    100.0 : 40.0,
    150.0 : 70.0,
    200.0 : 100.0,
    300.0 : 200.0
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
        try:
            fetched_positions = session.my_position(endpoint="/private/linear/position/list")['result'] # USDT Perpetual
        except Exception:
            pass
        if(fetched_positions):
            for position in fetched_positions:
                if position['is_valid'] == True and position['data']["size"] > 0: # Required per the ByBit API to be is_valid=True data, and we only want the active positions (size>0)
                    fetched_sessions.append(position['data'])
                    
        try:
            fetched_positions = session.my_position(endpoint="/v2/private/position/list")['result'] # Inverse Perpetual
        except Exception:
            pass
        if(fetched_positions):
            for position in fetched_positions:
                if position['is_valid'] == True and position['data']["size"] > 0: # Required per the ByBit API to be is_valid=True data, and we only want the active positions (size>0)
                    fetched_sessions.append(position['data'])
                     
        try:
            fetched_positions = session.my_position(endpoint="/futures/private/position/list")['result'] # Inverse Futures
        except Exception:
            pass
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
            
            #######################################################
            # Enforce Static Stop Loss feature
            #######################################################
            
            if(enforce_sl_static):
                if symbol in override_sl_static_cap_ratio: # Look if any custom stop ratio for this symbol
                    stop_loss_cap_ratio = override_sl_static_cap_ratio[symbol]
                else:
                    stop_loss_cap_ratio = default_sl_static_cap_ratio

                # FIRST check if immediate market close is needed in case price already breached with no Stop Loss in place
                # Fetch latest tickers
                try:
                    fetched_latest_tickers = session.latest_information_for_symbol(symbol=symbol)['result']
                except Exception:
                    pass
                if(fetched_latest_tickers):
                    for ticker in fetched_latest_tickers:
                        if ticker['symbol'] == symbol:
                            last_price = float(ticker['last_price'])
                            
                        if side == 'Buy':
                            position_leveraged_stop_loss = round((entry_price - (((stop_loss_cap_ratio/100) / leverage) * entry_price)), final_decimals_count)
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
                            position_leveraged_stop_loss = round((entry_price + (((stop_loss_cap_ratio/100) / leverage) * entry_price)), final_decimals_count)
                            if last_price > position_leveraged_stop_loss:
                                try:
                                    session.place_active_order(symbol=symbol, side="Buy", order_type="Market", qty=size, time_in_force="GoodTillCancel", reduce_only=True, close_on_trigger=True)
                                    log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + symbol + " SHORT Force-Stopped: "+str(last_price)+"."
                                    print(log)
                                    with open("SL_forced.txt", "a") as myfile:
                                        myfile.write(log+'\n')
                                except Exception:
                                    pass

                # Otherwise, search Conditional Orders if Stop Loss already exists with 'qty'=position size AND 'trigger_price' at the required price
                full_static_sl_found = False
                
                try:
                    fetched_conditional_orders = session.query_conditional_order(symbol=symbol)
                except Exception:
                    pass
                if(fetched_conditional_orders):
                    for conditional_order in fetched_conditional_orders["result"]:
                        # Note: order side should be opposite of position size
                        if side == "Buy" and conditional_order['side'] == "Sell" and conditional_order['order_type'] == 'Market' and conditional_order['order_status'] == 'Untriggered': # Stop Loss for a Long
                            if symbol.endswith('USDT'): # USDT Perpetual
                                stop_price = float(conditional_order['trigger_price'])
                                stop_order_id = conditional_order['stop_order_id']
                                if stop_price < entry_price and conditional_order['close_on_trigger'] == True and conditional_order['reduce_only'] == True:
                                    position_leveraged_stop_loss = round((entry_price - (((stop_loss_cap_ratio/100) / leverage) * entry_price)), final_decimals_count)
                                    if (stop_price == position_leveraged_stop_loss or (stop_price > entry_price and last_price > entry_price)) and conditional_order['qty'] == size:
                                        # Stop Loss found at the static ratio OR in profit, keep it
                                        full_static_sl_found = True
                                    else:
                                        # Stop Loss found but not at the static price, remove it
                                        try:
                                            session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id) 
                                        except Exception:
                                            pass
                                        
                            else: # Inverse Perpetuals or Futures
                                stop_price = float(conditional_order['stop_px'])
                                stop_order_id = conditional_order['order_id']
                                position_leveraged_stop_loss = round((entry_price - (((stop_loss_cap_ratio/100) / leverage) * entry_price)), final_decimals_count)
                                if (stop_price == position_leveraged_stop_loss or (stop_price > entry_price and last_price > entry_price)) and conditional_order['qty'] == size:
                                    # Stop Loss found at the static ratio OR in profit, keep it
                                    full_static_sl_found = True
                                else:
                                    # Stop Loss found but not at the static price, remove it
                                    try:
                                        session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id) 
                                    except Exception:
                                        pass

                        elif side == "Sell" and conditional_order['side'] == "Buy" and conditional_order['order_type'] == 'Market' and conditional_order['order_status'] == 'Untriggered': # Stop Loss for a Short
                            if symbol.endswith('USDT'): # USDT Perpetual
                                stop_price = float(conditional_order['trigger_price'])
                                stop_order_id = conditional_order['stop_order_id']
                                if stop_price > entry_price and conditional_order['close_on_trigger'] == True and conditional_order['reduce_only'] == True:
                                    position_leveraged_stop_loss = round((entry_price + (((stop_loss_cap_ratio/100) / leverage) * entry_price)), final_decimals_count)
                                    if (stop_price == position_leveraged_stop_loss or (stop_price < entry_price and last_price < entry_price)) and conditional_order['qty'] == size:
                                        # Stop Loss found at the static ratio OR in profit, keep it
                                        full_static_sl_found = True
                                    else:
                                        # Stop Loss found but not at the static price, remove it
                                        try:
                                            session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id) 
                                        except Exception:
                                            pass
                            
                            else: # Inverse Perpetuals or Futures
                                stop_price = float(conditional_order['stop_px'])
                                stop_order_id = conditional_order['order_id']
                                position_leveraged_stop_loss = round((entry_price + (((stop_loss_cap_ratio/100) / leverage) * entry_price)), final_decimals_count)
                                if (stop_price == position_leveraged_stop_loss or (stop_price < entry_price and last_price < entry_price)) and conditional_order['qty'] == size:
                                    # Stop Loss found at the static ratio OR in profit, keep it
                                    full_static_sl_found = True
                                else:
                                    # Stop Loss found but not at the static price, remove it
                                    try:
                                        session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id) 
                                    except Exception:
                                        pass
                            
                if full_static_sl_found == False:
                    # We couldn't find a static Stop Loss, so add it
                    # Prepare set_trading_stop arguments to pass to API
                    set_trading_stop_args = {'symbol': symbol, 'side': side}
                    if tp_sl_mode == "Partial":
                        set_trading_stop_args['sl_size'] = size # If Partial Mode then we need to send full size to close full position
                    
                    if side == 'Buy':
                        position_leveraged_stop_loss = round((entry_price - (((stop_loss_cap_ratio/100) / leverage) * entry_price)), final_decimals_count)
                        if stop_loss == 0 or stop_loss < position_leveraged_stop_loss:
                            try:
                                set_trading_stop_args['stop_loss'] = position_leveraged_stop_loss
                                session.set_trading_stop(**set_trading_stop_args)
                                log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + symbol + " LONG Maximum Static Stop-Loss adjusted to: "+str(position_leveraged_stop_loss)+" (" + str(stop_loss_cap_ratio) + "%)."
                                print(log)
                                with open("SL_protected.txt", "a") as myfile:
                                    myfile.write(log+'\n')
                            except Exception:
                                pass
                    elif side == 'Sell':
                        position_leveraged_stop_loss = round((entry_price + (((stop_loss_cap_ratio/100) / leverage) * entry_price)), final_decimals_count)
                        if stop_loss == 0 or stop_loss > position_leveraged_stop_loss:
                            try:
                                set_trading_stop_args['stop_loss'] = position_leveraged_stop_loss
                                session.set_trading_stop(**set_trading_stop_args)
                                log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + symbol + " SHORT Maximum Static Stop-Loss adjusted to: "+str(position_leveraged_stop_loss)+" (" + str(stop_loss_cap_ratio) + "%)."
                                print(log)
                                with open("SL_protected.txt", "a") as myfile:
                                    myfile.write(log+'\n')
                            except Exception:
                                pass
                                
                                
            #######################################################
            # Enforce Stop Loss Range feature
            #######################################################
            
            if(enforce_sl_range):
                if symbol in override_sl_range_cap_ratio: # Look if any custom stop ratio for this symbol
                    stop_loss_cap_ratio = override_sl_range_cap_ratio[symbol]
                else:
                    stop_loss_cap_ratio = default_sl_range_cap_ratio

                # FIRST check if immediate market close is needed in case price already breached with no Stop Loss in place
                # Fetch latest tickers
                try:
                    fetched_latest_tickers = session.latest_information_for_symbol(symbol=symbol)['result']
                except Exception:
                    pass
                if(fetched_latest_tickers):
                    for ticker in fetched_latest_tickers:
                        if ticker['symbol'] == symbol:
                            last_price = float(ticker['last_price'])
                            
                        if side == 'Buy':
                            position_leveraged_stop_loss = round((entry_price - (((stop_loss_cap_ratio/100) / leverage) * entry_price)), final_decimals_count)
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
                            position_leveraged_stop_loss = round((entry_price + (((stop_loss_cap_ratio/100) / leverage) * entry_price)), final_decimals_count)
                            if last_price > position_leveraged_stop_loss:
                                try:
                                    session.place_active_order(symbol=symbol, side="Buy", order_type="Market", qty=size, time_in_force="GoodTillCancel", reduce_only=True, close_on_trigger=True)
                                    log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + symbol + " SHORT Force-Stopped: "+str(last_price)+"."
                                    print(log)
                                    with open("SL_forced.txt", "a") as myfile:
                                        myfile.write(log+'\n')
                                except Exception:
                                    pass

                # Otherwise, search Conditional Orders if Stop Loss already exists with 'qty'=position size AND 'trigger_price' within allowed range
                total_allowed_stop_loss_found = 0.0
                
                try:
                    fetched_conditional_orders = session.query_conditional_order(symbol=symbol)
                except Exception:
                    pass
                if(fetched_conditional_orders):
                    for conditional_order in fetched_conditional_orders["result"]:
                        # Note: order side should be opposite of position size
                        if side == "Buy" and conditional_order['side'] == "Sell" and conditional_order['order_type'] == 'Market' and conditional_order['order_status'] == 'Untriggered': # Stop Loss for a Long
                            if symbol.endswith('USDT'): # USDT Perpetual
                                stop_price = float(conditional_order['trigger_price'])
                                stop_order_id = conditional_order['stop_order_id']
                                if stop_price < entry_price and conditional_order['close_on_trigger'] == True and conditional_order['reduce_only'] == True:
                                    position_leveraged_stop_loss = round((entry_price - (((stop_loss_cap_ratio/100) / leverage) * entry_price)), final_decimals_count)
                                    if stop_price >= position_leveraged_stop_loss:
                                        # Stop Loss found inside the allowed range, keep it
                                        total_allowed_stop_loss_found += float(conditional_order['qty'])
                                    else:
                                        # Stop Loss found outside the allowed range, useless so remove it
                                        try:
                                            session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id) 
                                        except Exception:
                                            pass
                                        
                            else: # Inverse Perpetuals or Futures
                                stop_price = float(conditional_order['stop_px'])
                                stop_order_id = conditional_order['order_id']
                                position_leveraged_stop_loss = round((entry_price - (((stop_loss_cap_ratio/100) / leverage) * entry_price)), final_decimals_count)
                                if stop_price >= position_leveraged_stop_loss:
                                    # Stop Loss found inside the allowed range, keep it
                                    total_allowed_stop_loss_found += float(conditional_order['qty'])
                                else:
                                    # Stop Loss found outside the allowed range, useless so remove it
                                    try:
                                        session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id) 
                                    except Exception:
                                        pass

                        elif side == "Sell" and conditional_order['side'] == "Buy" and conditional_order['order_type'] == 'Market' and conditional_order['order_status'] == 'Untriggered': # Stop Loss for a Short
                            if symbol.endswith('USDT'): # USDT Perpetual
                                stop_price = float(conditional_order['trigger_price'])
                                stop_order_id = conditional_order['stop_order_id']
                                if stop_price > entry_price and conditional_order['close_on_trigger'] == True and conditional_order['reduce_only'] == True:
                                    position_leveraged_stop_loss = round((entry_price + (((stop_loss_cap_ratio/100) / leverage) * entry_price)), final_decimals_count)
                                    if stop_price <= position_leveraged_stop_loss:
                                        # Stop Loss found inside the allowed range, keep it
                                        total_allowed_stop_loss_found += float(conditional_order['qty'])
                                    else:
                                        # Stop Loss found outside the allowed range, useless so remove it
                                        try:
                                            session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id)
                                        except Exception:
                                            pass
                            
                            else: # Inverse Perpetuals or Futures
                                stop_price = float(conditional_order['stop_px'])
                                stop_order_id = conditional_order['order_id']
                                position_leveraged_stop_loss = round((entry_price + (((stop_loss_cap_ratio/100) / leverage) * entry_price)), final_decimals_count)
                                if stop_price <= position_leveraged_stop_loss:
                                    # Stop Loss found inside the allowed range, keep it
                                    total_allowed_stop_loss_found += float(conditional_order['qty'])
                                else:
                                    # Stop Loss found outside the allowed range, useless so remove it
                                    try:
                                        session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id)
                                    except Exception:
                                        pass
                            
                if total_allowed_stop_loss_found < size:
                    # We couldn't find enough Stop Losses in the allowed range, so add the remaining needed
                    # Prepare set_trading_stop arguments to pass to API
                    set_trading_stop_args = {'symbol': symbol, 'side': side}
                    if tp_sl_mode == "Partial":
                        set_trading_stop_args['sl_size'] = size # If Partial Mode then we need to send full size to close full position
                    
                    if side == 'Buy':
                        position_leveraged_stop_loss = round((entry_price - (((stop_loss_cap_ratio/100) / leverage) * entry_price)), final_decimals_count)
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
                        position_leveraged_stop_loss = round((entry_price + (((stop_loss_cap_ratio/100) / leverage) * entry_price)), final_decimals_count)
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
                
            #######################################################
            # Enforce Lock In Profits Stop Loss feature
            #######################################################
            
            if(enforce_lock_in_p_sl):
                # Fetch latest tickers
                try:
                    fetched_latest_tickers = session.latest_information_for_symbol(symbol=symbol)['result']
                except Exception:
                    pass
                if(fetched_latest_tickers):
                    for ticker in fetched_latest_tickers:
                        if ticker['symbol'] == symbol:
                            last_price = float(ticker['last_price'])
                    try:
                        fetched_conditional_orders = session.query_conditional_order(symbol=symbol)      
                    except Exception:
                        pass
                    if side == 'Buy':
                        for elem in sorted(default_lock_in_p_sl.items(), reverse=True): # Sort Descending (reverse order to find the best Take Profit levels to lock in)
                            lock_in_p_price_ratio = elem[0]
                            lock_in_p_sl_ratio = elem[1]
                            
                            position_leveraged_p_level = round((entry_price + (((lock_in_p_price_ratio/100) / leverage) * entry_price)), final_decimals_count)
                            position_leveraged_p_sl_level = round((entry_price + (((lock_in_p_sl_ratio/100) / leverage) * entry_price)), final_decimals_count)
                            if last_price >= position_leveraged_p_level:

                                # Sarch Conditional Orders if Stop Loss already exists with 'qty'=position size AND 'trigger_price' better than the Take Profit Level
                                total_in_profit_stop_loss_found = 0.0
                                
                                if(fetched_conditional_orders):
                                    for conditional_order in fetched_conditional_orders["result"]:
                                        # Note: order side should be opposite of position size
                                        if conditional_order['side'] == "Sell" and conditional_order['order_type'] == 'Market' and conditional_order['order_status'] == 'Untriggered': # Stop Loss for a Long
                                            if symbol.endswith('USDT'): # USDT Perpetual
                                                stop_price = float(conditional_order['trigger_price'])
                                                stop_order_id = conditional_order['stop_order_id']
                                                if stop_price < position_leveraged_p_level and conditional_order['close_on_trigger'] == True and conditional_order['reduce_only'] == True:
                                                    if stop_price >= position_leveraged_p_sl_level:
                                                        # Stop Loss found inside the allowed range, keep it
                                                        total_in_profit_stop_loss_found += float(conditional_order['qty'])
                                                    else:
                                                        # Stop Loss found outside the allowed range, useless so remove it
                                                        try:
                                                            session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id)      
                                                        except Exception:
                                                            pass
                                            else: # Inverse Perpetuals or Futures
                                                stop_price = float(conditional_order['stop_px'])
                                                stop_order_id = conditional_order['order_id']
                                                if stop_price >= position_leveraged_p_sl_level:
                                                    # Stop Loss found inside the allowed range, keep it
                                                    total_in_profit_stop_loss_found += float(conditional_order['qty'])
                                                else:
                                                    # Stop Loss found outside the allowed range, useless so remove it
                                                    try:
                                                        session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id)    
                                                    except Exception:
                                                        pass
                                
                                if total_in_profit_stop_loss_found < size:
                                    # We couldn't find enough Stop Losses in the allowed range, so add the remaining needed
                                    # Prepare set_trading_stop arguments to pass to API
                                    set_trading_stop_args = {'symbol': symbol, 'side': side}
                                    if tp_sl_mode == "Partial":
                                        set_trading_stop_args['sl_size'] = size # If Partial Mode then we need to send full size to close full position
                                    
                                    if stop_loss == 0 or stop_loss < position_leveraged_p_level:
                                        try:
                                            #session.place_conditional_order(symbol=symbol, order_type="Market", reduce_only=True, side= "Sell", qty=size, stop_px=position_leveraged_p_level,time_in_force="GoodTillCancel")
                                            set_trading_stop_args['stop_loss'] = position_leveraged_p_sl_level
                                            session.set_trading_stop(**set_trading_stop_args)
                                            log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + symbol + " LONG Stop-Loss adjusted IN PROFIT to: "+str(position_leveraged_p_sl_level)+" (" + str(lock_in_p_sl_ratio) + "%) after hitting "+ str(position_leveraged_p_level) +" (" + str(lock_in_p_price_ratio) + "% profit level)."
                                            print(log)
                                            with open("P_protected.txt", "a") as myfile:
                                                myfile.write(log+'\n')
                                            break
                                        except Exception:
                                            pass

                    elif side == 'Sell':
                        for elem in sorted(default_lock_in_p_sl.items(), reverse=True): # Sort Descending (reverse order to find the best Take Profit levels to lock in)
                            lock_in_p_price_ratio = elem[0]
                            lock_in_p_sl_ratio = elem[1]
                            
                            position_leveraged_p_level = round((entry_price - (((lock_in_p_price_ratio/100) / leverage) * entry_price)), final_decimals_count)
                            position_leveraged_p_sl_level = round((entry_price - (((lock_in_p_sl_ratio/100) / leverage) * entry_price)), final_decimals_count)
                            if last_price <= position_leveraged_p_level:
                
                                # Sarch Conditional Orders if Stop Loss already exists with 'qty'=position size AND 'trigger_price' better than the Take Profit Level
                                total_in_profit_stop_loss_found = 0.0
                                
                                if(fetched_conditional_orders):
                                    for conditional_order in fetched_conditional_orders["result"]:
                                        # Note: order side should be opposite of position size
                                        if conditional_order['side'] == "Buy" and conditional_order['order_type'] == 'Market' and conditional_order['order_status'] == 'Untriggered': # Stop Loss for a Short
                                            if symbol.endswith('USDT'): # USDT Perpetual
                                                stop_price = float(conditional_order['trigger_price'])
                                                stop_order_id = conditional_order['stop_order_id']
                                                if stop_price > position_leveraged_p_level and conditional_order['close_on_trigger'] == True and conditional_order['reduce_only'] == True:
                                                    if stop_price <= position_leveraged_p_sl_level:
                                                        # Stop Loss found inside the allowed range, keep it
                                                        total_in_profit_stop_loss_found += float(conditional_order['qty'])
                                                    else:
                                                        # Stop Loss found outside the allowed range, useless so remove it
                                                        try:
                                                            session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id)   
                                                        except Exception:
                                                            pass
                                            
                                            else: # Inverse Perpetuals or Futures
                                                stop_price = float(conditional_order['stop_px'])
                                                stop_order_id = conditional_order['order_id']
                                                if stop_price <= position_leveraged_p_sl_level:
                                                    # Stop Loss found inside the allowed range, keep it
                                                    total_in_profit_stop_loss_found += float(conditional_order['qty'])
                                                else:
                                                    # Stop Loss found outside the allowed range, useless so remove it
                                                    try:
                                                        session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id) 
                                                    except Exception:
                                                        pass

                                if total_in_profit_stop_loss_found < size:
                                    # We couldn't find enough Stop Losses in the allowed range, so add the remaining needed
                                    # Prepare set_trading_stop arguments to pass to API
                                    set_trading_stop_args = {'symbol': symbol, 'side': side}
                                    if tp_sl_mode == "Partial":
                                        set_trading_stop_args['sl_size'] = size # If Partial Mode then we need to send full size to close full position
                                    
                                    if stop_loss == 0 or stop_loss > position_leveraged_p_level:
                                        try:
                                            #session.place_conditional_order(symbol=symbol, order_type="Market", reduce_only=True, side= "Buy", qty=size, stop_px=position_leveraged_p_level,time_in_force="GoodTillCancel")
                                            set_trading_stop_args['stop_loss'] = position_leveraged_p_sl_level
                                            session.set_trading_stop(**set_trading_stop_args)
                                            log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + symbol + " SHORT Stop-Loss adjusted IN PROFIT to: "+str(position_leveraged_p_sl_level)+" (" + str(lock_in_p_sl_ratio) + "%) after hitting "+ str(position_leveraged_p_level) +" (" + str(lock_in_p_price_ratio) + "% profit level)."
                                            print(log)
                                            with open("P_protected.txt", "a") as myfile:
                                                myfile.write(log+'\n')
                                            break
                                        except Exception:
                                            pass
                
        sleep(1)
