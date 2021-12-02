import math
import json
from types import SimpleNamespace
import logging
from time import sleep
import time
from datetime import datetime
from typing import Union
from decimal import Decimal
from pybit import HTTP, WebSocket

###### Configurations (EDIT)
api_key = 'TYPE BYBIT API KEY HERE'
api_secret = 'TYPE BYBIT API SECRET HERE'
network = 'mainnet' # Set to 'mainnet' or 'testnet' depending on which Network you want to use (note: usually each network requires separate API credentials)
log_label = 'YOUR_NAME' # If you have multiple scripts running for different users, this label could be used to identify different ones
exchange_market_taker_fee = 0.075
exchange_market_maker_fee = -0.025

# Enforce Static Stop Loss at an exact ratio (not less not more) feature switch (True/False). Only exception is if position is in profit, it allows moving the SL to breakeven or profit.
# NOTE: It will always set the Stop Loss with Full (100%) position size. Set to "0.0" if you want to disable the feature for a specific asset in case the default is setup.
enforce_sl_static = False
# Maximum Stop Loss % allowed (ratio of price difference, after leverage)
default_sl_static_cap_ratio = 15.0
# Use this to set custom Stop Loss % for specific asset pairs (override the default), you can add more pairs as you desire by adding a comma at the end and a new symbol
override_sl_static_cap_ratio = {
  "BTCUSDT": 0.0,
  "SOLUSDT": 10.0,
  "ETHUSDT": 10.0,
  "XRPUSDT": 10.0
}

# Enforce Total Balance Static Stop Loss at an exact ratio (not less not more) feature switch (True/False). Only exception is if position is in profit, it allows moving the SL to breakeven or profit.
# NOTE: It will always set the Stop Loss with Full (100%) position size. Set to "0.0" if you want to disable the feature for a specific asset in case the default is setup.
enforce_tb_sl_static = True
# Maximum Stop Loss % allowed (ratio of price difference, after leverage)
default_tb_sl_static_cap_ratio = 2.5
# Use this to set custom Stop Loss % for specific asset pairs (override the default), you can add more pairs as you desire by adding a comma at the end and a new symbol
override_tb_sl_static_cap_ratio = {
  "BTCUSDT": 5.0,
  "SOLUSDT": 5.0,
  "ETHUSDT": 5.0,
  "XRPUSDT": 5.0
}

# Enforce Stop Loss Range feature switch (True/False). NOTE: You should only activate either the Static Stop Loss feature or this one, not both, to avoid issues.
# NOTE: It will always set the Stop Loss with Full (100%) position size.  Set to "0.0" if you want to disable the feature for a specific asset in case the default is setup. If "Tp/SL on Selected Position" is used on the exchange, it will make sure to set 100% as well (it will add the remaining of the Stop Losses needed to fully Stop the position)
enforce_sl_range = True
# Maximum Stop Loss % allowed (ratio of price difference, after leverage)
default_sl_range_cap_ratio = 15.0
# Use this to set custom Stop Loss % for specific asset pairs (override the default), you can add more pairs as you desire by adding a comma at the end and a new symbol
override_sl_range_cap_ratio = {
  "BTCUSDT": 0.0,
  "SOLUSDT": 10.0,
  "ETHUSDT": 10.0,
  "XRPUSDT": 10.0
}

# Enforce Take Profits feature switch (True/False)
# NOTE: Take profits are executed automatically as Market Orders at the price levels defined, and the quantity is calculated in real-time at the time of execution based on the position's size.
enforce_tp = True
# Tolerance ratio: good practice to add tolerance ratio which is how far away from the target the Bot would consider the level invalid and target the next level. This is a ratio of the ratio being targetted (eg. 1% tolerance means 1% of the distance between the Position Entry Price and the target Take Profit Level)
default_tp_tolerance_ratio = 1.0
# Structure is tp_price_ratio (after leverage) : tp_size_ratio WHERE tp_size_ratio <= 100 (quantity ratio of the position to close)
# NOTE: Order DOES NOT matter
default_tp = {
    15.0 : 50.0,
    50.0 : 25.0,
    100.0 : 25.0,
    150.0 : 50.0,
    200.0 : 100.0
}

# Enforce Lock In Profits Stop Loss feature switch (True/False)
# IMPORTANT NOTE: This feature will make sure to place a 100% Stop Loss at the desired levels and move it as needed, to fully close the position in profit.
enforce_lock_in_p_sl = True
# Default Lock In Profits Stop Loss levels (when price level ratio is hit, position's SL moved to defined price ratio). Note it is a Hard SL meaning you can't loose once you hit those profit levels.
# Structure is lock_in_p_price_ratio (after leverage): lock_in_p_sl_ratio
# NOTE: Order DOES matter. Make sure the order is in Ascending OR Descending on the left and right sides to avoid issues
default_lock_in_p_sl = {
    15.0 : 3.0,
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

def round_step_size(quantity: Union[float, Decimal], step_size: Union[float, Decimal]) -> float:
    """Rounds a given quantity to a specific step size
    :param quantity: required
    :param step_size: required
    :return: decimal
    """
    precision: int = int(round(-math.log(step_size, 10), 0))
    return float(round(quantity, precision))

###### ByBit Base Endpoints (only edit if they don't match the currently published ones by ByBit at: https://bybit-exchange.github.io/docs/linear/#t-websocket
wsURL_USDT_mainnet = "wss://stream.bybit.com/realtime_private"
wsURL_USDT_testnet = "wss://stream-testnet.bybit.com/realtime_private"
wsURL_Inverse_mainnet = "wss://stream.bybit.com/realtime"
wsURL_Inverse_testnet = "wss://stream-testnet.bybit.com/realtime"
sessionURL_mainnet = "https://api.bybit.com"
sessionURL_testnet = "https://api-testnet.bybit.com"
######

if network == 'testnet':
    wsURL_USDT = wsURL_USDT_testnet
    wsURL_Inverse = wsURL_Inverse_testnet
    sessionURL = sessionURL_testnet
elif network == 'mainnet':
    wsURL_USDT = wsURL_USDT_mainnet
    wsURL_Inverse = wsURL_Inverse_mainnet
    sessionURL = sessionURL_mainnet

if __name__ == "__main__":
    session = HTTP(endpoint=sessionURL, api_key=api_key, api_secret=api_secret)
    tick_size = {}
    base_currency = {}
    quote_currency = {}
    qty_step = {}
    symbols = session.query_symbol()["result"]
    for symbol in symbols:
        tick_size[symbol["name"]] = symbol["price_filter"]["tick_size"]
        base_currency[symbol["name"]] = symbol["base_currency"]
        quote_currency[symbol["name"]] = symbol["quote_currency"]
        qty_step[symbol["name"]] = symbol["lot_size_filter"]["qty_step"]
        
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
        fetched_positions = []
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
            # unrealised_pnl = float(position["unrealised_pnl"]) # We will not use this as the current API is not returning the real-time unrealised_pnl value properly, we will need to manually calculate it for each position
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
                
                if stop_loss_cap_ratio != 0:
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
                                        log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " LONG Force-Stopped: "+str(last_price)+"."
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
                                        log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " SHORT Force-Stopped: "+str(last_price)+"."
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
                                    log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " LONG Maximum Static Stop-Loss adjusted to: "+str(position_leveraged_stop_loss)+" (" + str(stop_loss_cap_ratio) + "%)."
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
                                    log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " SHORT Maximum Static Stop-Loss adjusted to: "+str(position_leveraged_stop_loss)+" (" + str(stop_loss_cap_ratio) + "%)."
                                    print(log)
                                    with open("SL_protected.txt", "a") as myfile:
                                        myfile.write(log+'\n')
                                except Exception:
                                    pass
                                
                                
            #######################################################
            # Enforce Total Balance Static Stop Loss feature
            #######################################################
            
            if(enforce_tb_sl_static):
                if symbol in override_tb_sl_static_cap_ratio: # Look if any custom stop ratio for this symbol
                    stop_loss_cap_ratio = override_tb_sl_static_cap_ratio[symbol]
                else:
                    stop_loss_cap_ratio = default_tb_sl_static_cap_ratio

                if stop_loss_cap_ratio != 0:
                    # Check if immediate market close is needed in case Unrealised PnL already reached the specified Balance Stop Loss ratio
                    # Fetch latest tickers
                    try:
                        fetched_latest_tickers = session.latest_information_for_symbol(symbol=symbol)['result']
                    except Exception:
                        pass
                    if(fetched_latest_tickers):
                        for ticker in fetched_latest_tickers:
                            if ticker['symbol'] == symbol:
                                last_price = float(ticker['last_price'])
                                mark_price = float(ticker['mark_price'])
                                
                            # First, fetch Wallet Balance
                            if quote_currency[symbol] == "USDT":
                                wallet_balance = session.get_wallet_balance(coin="USDT")["result"]["USDT"]["wallet_balance"]
                                if side == 'Buy':
                                    # unrealised_pnl_calculated is negative if in loss
                                    unrealised_pnl_calculated = size * ((mark_price -  entry_price))
                                    if unrealised_pnl_calculated <= (-1 * (wallet_balance * stop_loss_cap_ratio/100)):
                                        try:
                                            session.place_active_order(symbol=symbol, side="Sell", order_type="Market", qty=size, time_in_force="GoodTillCancel", reduce_only=True, close_on_trigger=True)
                                            log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " LONG Balance Static Force-Stopped with unrealised PnL of "+str(unrealised_pnl_calculated)+" at: "+str(last_price)+"."
                                            print(log)
                                            with open("SL_forced.txt", "a") as myfile:
                                                myfile.write(log+'\n')
                                        except Exception:
                                            pass
                                elif side == 'Sell':
                                    # unrealised_pnl_calculated is negative if in loss
                                    unrealised_pnl_calculated = size * ((entry_price -  mark_price))
                                    if unrealised_pnl_calculated <= (-1 * (wallet_balance * stop_loss_cap_ratio/100)):
                                        try:
                                            session.place_active_order(symbol=symbol, side="Buy", order_type="Market", qty=size, time_in_force="GoodTillCancel", reduce_only=True, close_on_trigger=True)
                                            log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " SHORT Balance Static Force-Stopped with unrealised PnL of "+str(unrealised_pnl_calculated)+" at: "+str(last_price)+"."
                                            print(log)
                                            with open("SL_forced.txt", "a") as myfile:
                                                myfile.write(log+'\n')
                                        except Exception:
                                            pass
                            else:
                                wallet_balance = session.get_wallet_balance(coin=base_currency[symbol])["result"][base_currency[symbol]]["wallet_balance"]
                                if side == 'Buy':
                                    # unrealised_pnl_calculated is negative if in loss
                                    unrealised_pnl_calculated = size * (((1.0/entry_price) -  (1.0/mark_price)))
                                    if unrealised_pnl_calculated <= (-1 * (wallet_balance * stop_loss_cap_ratio/100)):
                                        try:
                                            session.place_active_order(symbol=symbol, side="Sell", order_type="Market", qty=size, time_in_force="GoodTillCancel", reduce_only=True, close_on_trigger=True)
                                            log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " LONG Balance Static Force-Stopped with unrealised PnL of "+str(unrealised_pnl_calculated)+" at: "+str(last_price)+"."
                                            print(log)
                                            with open("SL_forced.txt", "a") as myfile:
                                                myfile.write(log+'\n')
                                        except Exception:
                                            pass
                                elif side == 'Sell':
                                    # unrealised_pnl_calculated is negative if in loss
                                    unrealised_pnl_calculated = size * (((1.0/mark_price) -  (1.0/entry_price)))
                                    if unrealised_pnl_calculated <= (-1 * (wallet_balance * stop_loss_cap_ratio/100)):
                                        try:
                                            session.place_active_order(symbol=symbol, side="Buy", order_type="Market", qty=size, time_in_force="GoodTillCancel", reduce_only=True, close_on_trigger=True)
                                            log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " SHORT Balance Static Force-Stopped with unrealised PnL of "+str(unrealised_pnl_calculated)+" at: "+str(last_price)+"."
                                            print(log)
                                            with open("SL_forced.txt", "a") as myfile:
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

                if stop_loss_cap_ratio != 0:
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
                                        log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " LONG Force-Stopped: "+str(last_price)+"."
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
                                        log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " SHORT Force-Stopped: "+str(last_price)+"."
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
                                    log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " LONG Maximum Stop-Loss adjusted to: "+str(position_leveraged_stop_loss)+" (" + str(stop_loss_cap_ratio) + "%)."
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
                                    log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " SHORT Maximum Stop-Loss adjusted to: "+str(position_leveraged_stop_loss)+" (" + str(stop_loss_cap_ratio) + "%)."
                                    print(log)
                                    with open("SL_protected.txt", "a") as myfile:
                                        myfile.write(log+'\n')
                                except Exception:
                                    pass
                                
            #######################################################                    
            # Enforce Take Profits feature
            #######################################################  
                                
            if(enforce_tp):
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
                            # Sarch Conditional Orders if Take Profits already exist
                            tp_found = False
                            
                            try:
                                fetched_conditional_orders = session.query_conditional_order(symbol=symbol)
                            except Exception:
                                pass
                            if(fetched_conditional_orders):
                                for conditional_order in fetched_conditional_orders["result"]:
                                    if not tp_found: # If we found a valid TP, no need to iterate any more
                                        if symbol.endswith('USDT'): # USDT Perpetual
                                            stop_price = float(conditional_order['trigger_price'])
                                            stop_order_id = conditional_order['stop_order_id']

                                            if conditional_order['side'] == 'Sell' and stop_price > last_price and stop_price > entry_price and conditional_order['close_on_trigger'] == True and conditional_order['reduce_only'] == True:
                                                # Take Profit found, make sure it is one of the pre-defined ones and make sure its quantity is up to date as well
                                                for elem in default_tp.items():
                                                    tp_price_ratio = elem[0]
                                                    tp_size_ratio = elem[1]
                                                    tp_price = round((entry_price + (((tp_price_ratio/100) / leverage) * entry_price)), final_decimals_count)
                                                    tp_size = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol])
                                                    if tp_price==stop_price and (tp_size==conditional_order['qty'] or math.floor(tp_size * 10)/10.0==conditional_order['qty'] or math.floor(tp_size * 100)/100.0==conditional_order['qty'] or math.floor(tp_size * 1000)/1000.0==conditional_order['qty'] or math.floor(tp_size * 10000)/10000.0==conditional_order['qty']):
                                                        # We found a valid pre-defined TP, keep it (note we check the floor in case the exchange did remove decimals upon creating the order)
                                                        tp_found = True
                                                if not tp_found:
                                                    # Invalid TP (or updated position size not reflected in the TP), REMOVE IT
                                                    try:
                                                        session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id) 
                                                    except Exception:
                                                        pass
                                        else: # Inverse Perpetuals or Futures
                                            stop_price = float(conditional_order['stop_px'])
                                            stop_order_id = conditional_order['order_id']
                                            if conditional_order['side'] == 'Sell' and stop_price > last_price and stop_price > entry_price:
                                                # Take Profit found, make sure it is one of the pre-defined ones and make sure its quantity is up to date as well
                                                for elem in default_tp.items():
                                                    tp_price_ratio = elem[0]
                                                    tp_size_ratio = elem[1]
                                                    tp_price = round((entry_price + (((tp_price_ratio/100) / leverage) * entry_price)), final_decimals_count)
                                                    tp_size = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol])
                                                    if tp_price==stop_price and (tp_size==conditional_order['qty'] or math.floor(tp_size * 10)/10.0==conditional_order['qty'] or math.floor(tp_size * 100)/100.0==conditional_order['qty'] or math.floor(tp_size * 1000)/1000.0==conditional_order['qty'] or math.floor(tp_size * 10000)/10000.0==conditional_order['qty']):
                                                        # We found a valid pre-defined TP, keep it (note we check the floor in case the exchange did remove decimals upon creating the order)
                                                        tp_found = True
                                                if not tp_found:
                                                    # Invalid TP (or updated position size not reflected in the TP), REMOVE IT
                                                    try:
                                                        session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id) 
                                                    except Exception:
                                                        pass
                   
                            if not tp_found: # No TPs found, so add (this way we kind of avoid re-adding the same TP if price hit and found resistance at and retested it. so we don't TP the same level twice)
                                # We couldn't find any TPs, let's add the suitable one
                                # Prepare set_trading_stop arguments to pass to API
                                set_trading_stop_args = {'symbol': symbol, 'side': side}
                                
                                for elem in sorted(default_tp.items(), reverse=False): # Sort Ascending to find the nearest TP level
                                    tp_price_ratio = elem[0]
                                    tp_size_ratio = elem[1]
                                    
                                    set_trading_stop_args['take_profit'] = round((entry_price + (((tp_price_ratio/100) / leverage) * entry_price)), final_decimals_count)
                                    set_trading_stop_args['tp_size'] = tp_size = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol])
                                    
                                    if last_price < set_trading_stop_args['take_profit'] - (default_tp_tolerance_ratio/100) * (set_trading_stop_args['take_profit'] - entry_price):
                                        try:
                                            session.set_trading_stop(**set_trading_stop_args)
                                            log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " LONG Take-Profit placed: "+str(tp_size_ratio)+"% of Quantity ("+str(set_trading_stop_args['tp_size'])+") @ "+ str(tp_price_ratio) +"% in Profit ("+str(set_trading_stop_args['take_profit'])+")."
                                            print(log)
                                            with open("TP.txt", "a") as myfile:
                                                myfile.write(log+'\n')
                                            break # No need to add more TPs, we only place 1 TP at a time
                                        except Exception:
                                            pass                 
                                
                        elif side == 'Sell':   
                            # Sarch Conditional Orders if Take Profits already exist
                            tp_found = False
                            
                            try:
                                fetched_conditional_orders = session.query_conditional_order(symbol=symbol)
                            except Exception:
                                pass
                            if(fetched_conditional_orders):
                                for conditional_order in fetched_conditional_orders["result"]:
                                    if not tp_found: # If we found a valid TP, no need to iterate any more
                                        if symbol.endswith('USDT'): # USDT Perpetual
                                            stop_price = float(conditional_order['trigger_price'])
                                            stop_order_id = conditional_order['stop_order_id']

                                            if conditional_order['side'] == 'Buy' and stop_price < last_price and stop_price < entry_price and conditional_order['close_on_trigger'] == True and conditional_order['reduce_only'] == True:
                                                # Take Profit found, make sure it is one of the pre-defined ones and make sure its quantity is up to date as well
                                                for elem in default_tp.items():
                                                    tp_price_ratio = elem[0]
                                                    tp_size_ratio = elem[1]
                                                    tp_price = round((entry_price - (((tp_price_ratio/100) / leverage) * entry_price)), final_decimals_count)
                                                    tp_size = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol])
                                                    if tp_price==stop_price and (tp_size==conditional_order['qty'] or math.floor(tp_size * 10)/10.0==conditional_order['qty'] or math.floor(tp_size * 100)/100.0==conditional_order['qty'] or math.floor(tp_size * 1000)/1000.0==conditional_order['qty'] or math.floor(tp_size * 10000)/10000.0==conditional_order['qty']):
                                                        # We found a valid pre-defined TP, keep it (note we check the floor in case the exchange did remove decimals upon creating the order)
                                                        tp_found = True
                                                if not tp_found:
                                                    # Invalid TP (or updated position size not reflected in the TP), REMOVE IT
                                                    try:
                                                        session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id) 
                                                    except Exception:
                                                        pass
                                        else: # Inverse Perpetuals or Futures
                                            stop_price = float(conditional_order['stop_px'])
                                            stop_order_id = conditional_order['order_id']
                                            if conditional_order['side'] == 'Buy' and stop_price < last_price and stop_price < entry_price:
                                                # Take Profit found, make sure it is one of the pre-defined ones and make sure its quantity is up to date as well
                                                for elem in default_tp.items():
                                                    tp_price_ratio = elem[0]
                                                    tp_size_ratio = elem[1]
                                                    tp_price = round((entry_price - (((tp_price_ratio/100) / leverage) * entry_price)), final_decimals_count)
                                                    tp_size = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol])
                                                    if tp_price==stop_price and (tp_size==conditional_order['qty'] or math.floor(tp_size * 10)/10.0==conditional_order['qty'] or math.floor(tp_size * 100)/100.0==conditional_order['qty'] or math.floor(tp_size * 1000)/1000.0==conditional_order['qty'] or math.floor(tp_size * 10000)/10000.0==conditional_order['qty']):
                                                        # We found a valid pre-defined TP, keep it (note we check the floor in case the exchange did remove decimals upon creating the order)
                                                        tp_found = True
                                                if not tp_found:
                                                    # Invalid TP (or updated position size not reflected in the TP), REMOVE IT
                                                    try:
                                                        session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id) 
                                                    except Exception:
                                                        pass
                   
                            if not tp_found: # No TPs found, so add (this way we kind of avoid re-adding the same TP if price hit and found resistance at and retested it. so we don't TP the same level twice)
                                # We couldn't find any TPs, let's add the suitable one
                                # Prepare set_trading_stop arguments to pass to API
                                set_trading_stop_args = {'symbol': symbol, 'side': side}
                                
                                for elem in sorted(default_tp.items(), reverse=False): # Sort Ascending to find the nearest TP level
                                    tp_price_ratio = elem[0]
                                    tp_size_ratio = elem[1]
                                    
                                    set_trading_stop_args['take_profit'] = round((entry_price - (((tp_price_ratio/100) / leverage) * entry_price)), final_decimals_count)
                                    set_trading_stop_args['tp_size'] = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol])
                                    
                                    if last_price > set_trading_stop_args['take_profit'] + (default_tp_tolerance_ratio/100) * (entry_price - set_trading_stop_args['take_profit']):
                                        try:
                                            session.set_trading_stop(**set_trading_stop_args)
                                            log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " SHORT Take-Profit placed: "+str(tp_size_ratio)+"% of Quantity ("+str(set_trading_stop_args['tp_size'])+") @ "+ str(tp_price_ratio) +"% in Profit ("+str(set_trading_stop_args['take_profit'])+")."
                                            print(log)
                                            with open("TP.txt", "a") as myfile:
                                                myfile.write(log+'\n')
                                            break # No need to add more TPs, we only place 1 TP at a time
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
                                            log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " LONG Stop-Loss adjusted IN PROFIT to: "+str(position_leveraged_p_sl_level)+" (" + str(lock_in_p_sl_ratio) + "%) after hitting "+ str(position_leveraged_p_level) +" (" + str(lock_in_p_price_ratio) + "% profit level)."
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
                                            log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " SHORT Stop-Loss adjusted IN PROFIT to: "+str(position_leveraged_p_sl_level)+" (" + str(lock_in_p_sl_ratio) + "%) after hitting "+ str(position_leveraged_p_level) +" (" + str(lock_in_p_price_ratio) + "% profit level)."
                                            print(log)
                                            with open("P_protected.txt", "a") as myfile:
                                                myfile.write(log+'\n')
                                            break
                                        except Exception:
                                            pass
                
        sleep(0.5)
