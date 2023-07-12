#!/usr/bin/python

# INSTALLATION
#
# Install Python 3.8+
# Install Pip3
#
# Then run in terminal:
#
#   pip3 install pybit
#   pip3 install wheel
#   pip3 install pandas
#   pip3 install pandas_ta
#   pip3 install matplotlib
#   pip3 install mysql-connector-python
#   pip3 install pydash
#   pip3 install pyyaml
#
# USAGE
#
# Edit config.yaml with your API keys and set the variables to your liking.
# Make more copies of config.yaml for other setups you want to run
#
#
# You can run this script multiple times, one in each terminal, with a different config file for each!
#
# At command line:
#
#   python3 crypto-genie.py config_file=config.yaml


import random
import string
import numpy as np
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
import math
import json
from types import SimpleNamespace
import logging
from time import sleep
import time
import calendar
from datetime import datetime, timedelta
from typing import Union
from decimal import Decimal
from pybit import HTTP, WebSocket
import mysql.connector
from pydash import _
import yaml
import sys
from sklearn.linear_model import LinearRegression

###### Terminal passed Arguments
args = {}
for arg in sys.argv[1:]:
    arg_key = arg.split('=')[0]
    arg_value = arg.split('=')[1]
    args[arg_key] = arg_value

# Load config parameters from given file or default config.yaml
if "config_file" in args:
    config_file = args['config_file']
else:
    config_file = "config.yaml"
    
config = {}
with open(config_file) as f:
    config = yaml.safe_load(f)


### CONFIG VARIABLES FROM CONFIG FILE
# MySQL Database
enable_db_features = config['enable_db_features']
db_host = config['db_host']
db_username = config['db_username']
db_password = config['db_password']
db_name = config['db_name']

# ByBit Exchange API
api_key = config['api_key']
api_secret = config['api_secret']
network = config['network']
log_label = config['log_label']

exchange_market_taker_fee = 0.075
exchange_market_maker_fee = -0.025

wait_time = config['wait_time']
recv_window = config['recv_window']
enforce_sl_static = config['enforce_sl_static']
default_sl_static_cap_ratio = config['default_sl_static_cap_ratio']
override_sl_static_cap_ratio = config['override_sl_static_cap_ratio'] or {}
enforce_tb_sl_static = config['enforce_tb_sl_static']
enforce_tb_sl_static_emergency_exit = config['enforce_tb_sl_static_emergency_exit']
enforce_tb_sl_static_range = config['enforce_tb_sl_static_range']
enforce_tb_sl_max_cum_loss = config['enforce_tb_sl_max_cum_loss']
enforce_tb_sl_db_stored = config['enforce_tb_sl_db_stored']
default_tb_initial_sl_static_cap_ratio = config['default_tb_initial_sl_static_cap_ratio']
default_tb_initial_sl_static_pos_size_ratio = config['default_tb_initial_sl_static_pos_size_ratio']
default_tb_sl_static_cap_ratio = config['default_tb_sl_static_cap_ratio']
default_tb_sl_static_pos_size_ratio = config['default_tb_sl_static_pos_size_ratio']
override_tb_sl_static = config['override_tb_sl_static'] or {}
enforce_tb_hedge = config['enforce_tb_hedge']
default_tb_hedge_cap_ratio = config['default_tb_hedge_cap_ratio']
default_tb_hedge_pos_size_ratio = config['default_tb_hedge_pos_size_ratio']
default_tb_hedge_balancer_cap_ratio = config['default_tb_hedge_balancer_cap_ratio']
default_tb_hedge_sl_static_cap_ratio = config['default_tb_hedge_sl_static_cap_ratio']
override_tb_hedge = config['override_tb_hedge'] or {}
enforce_sl_range = config['enforce_sl_range']
default_sl_range_cap_ratio = config['default_sl_range_cap_ratio']
override_sl_range_cap_ratio = config['override_sl_range_cap_ratio']
enforce_tp = config['enforce_tp']
enforce_tp_limit = config['enforce_tp_limit']
default_tp_tolerance_ratio = config['default_tp_tolerance_ratio']
default_tp = config['default_tp']
enforce_lock_in_p_sl = config['enforce_lock_in_p_sl']
default_lock_in_p_sl = config['default_lock_in_p_sl']
enforce_tp_dynamic = config['enforce_tp_dynamic']
tp_dynamic = config['tp_dynamic']
enforce_smart_dynamic_entries = config['enforce_smart_dynamic_entries']
smart_dynamic_entries = config['smart_dynamic_entries']
default_smart_dynamic_entries_wallet_balance_order_ratio = config['default_smart_dynamic_entries_wallet_balance_order_ratio']
default_smart_dynamic_entries_minimum_average_distance_multiplier = config['default_smart_dynamic_entries_minimum_average_distance_multiplier']
default_smart_dynamic_entries_price_chaser_minimum_ticks = config['default_smart_dynamic_entries_price_chaser_minimum_ticks']
default_smart_dynamic_entries_rsi_length = config['default_smart_dynamic_entries_rsi_length']
default_smart_dynamic_entries_level_1_from = config['default_smart_dynamic_entries_level_1_from']
default_smart_dynamic_entries_level_1_to = config['default_smart_dynamic_entries_level_1_to']
default_smart_dynamic_entries_level_1_max_effective_leverage = config['default_smart_dynamic_entries_level_1_max_effective_leverage']
default_smart_dynamic_entries_level_2_from = config['default_smart_dynamic_entries_level_2_from']
default_smart_dynamic_entries_level_2_to = config['default_smart_dynamic_entries_level_2_to']
default_smart_dynamic_entries_level_2_max_effective_leverage = config['default_smart_dynamic_entries_level_2_max_effective_leverage']
default_smart_dynamic_entries_level_3_from = config['default_smart_dynamic_entries_level_3_from']
default_smart_dynamic_entries_level_3_to = config['default_smart_dynamic_entries_level_3_to']
default_smart_dynamic_entries_level_3_max_effective_leverage = config['default_smart_dynamic_entries_level_3_max_effective_leverage']
default_smart_dynamic_entries_level_4_from = config['default_smart_dynamic_entries_level_4_from']
default_smart_dynamic_entries_level_4_max_effective_leverage = config['default_smart_dynamic_entries_level_4_max_effective_leverage']
enforce_db_exit_strategies = config['enforce_db_exit_strategies']

# Connect to Crypto Genie Database
if(enable_db_features):
    mydb = mysql.connector.connect(
      host=db_host,
      user=db_username,
      password=db_password,
      database=db_name
    )
    mydb.autocommit = True

def round_step_size(quantity: Union[float, Decimal], step_size: Union[float, Decimal], min_qty: Union[float, Decimal] = 0) -> float:
    """Rounds a given quantity to a specific step size
    :param quantity: required
    :param step_size: required
    :return: decimal
    """
    precision: int = int(round(-math.log(step_size, 10), 0))
    return float(round(quantity, precision)) if float(round(quantity, precision)) > min_qty else min_qty
    
def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

def close_enough_match(price1, price2, size1, size2, positionType=False):
    # price1 is the fixed target and price2 is the dynamic one being checked
    if positionType=="Buy":
        price_matches = price2 <= price1 # Price can be at the exact level or closer to entry
    elif positionType=="Sell":
        price_matches = price2 >= price1 # Price can be at the exact level or closer to entry
    else:
        price_matches = price2 == price1
    size_matches = size1 == size2 or math.floor(size1 * 10)/10.0 == size2 or math.floor(size1 * 100)/100.0 == size2 or math.floor(size1 * 1000)/1000.0 == size2 or math.floor(size1 * 10000)/10000.0 == size2
    return price_matches and size_matches

def round_to_tick(price,tick_size):
    decimals_count = str(tick_size)[::-1].find('.') # Tick Size number of decimals
    return round(round(float(price)/float(tick_size))*float(tick_size), decimals_count)


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
    session = HTTP(endpoint=sessionURL, api_key=api_key, api_secret=api_secret, recv_window=recv_window)
    tick_size = {}
    base_currency = {}
    quote_currency = {}
    max_leverage = {}
    qty_step = {}
    min_trading_qty = {}
    instruments = []
    symbols = session.query_symbol()["result"]
    for symbol in symbols:
        tick_size[symbol["name"]] = symbol["price_filter"]["tick_size"]
        base_currency[symbol["name"]] = symbol["base_currency"]
        quote_currency[symbol["name"]] = symbol["quote_currency"]
        max_leverage[symbol["name"]] = symbol["leverage_filter"]["max_leverage"]
        qty_step[symbol["name"]] = symbol["lot_size_filter"]["qty_step"]
        min_trading_qty[symbol["name"]] = symbol["lot_size_filter"]["min_trading_qty"]
        instruments.append(symbol["name"])
        '''
        # CUSTOM CODE TO SET LEVERAGE OF ALL PAIRS TO THE MAX 
        if symbol["name"].endswith('USDT'): # USDT Perpetual
            try:
                session.set_leverage(symbol=symbol["name"], buy_leverage=12.5, sell_leverage=12.5)
                print(symbol["name"] + " now set to Leverage 12.5")
            except Exception:
                pass
                
            try:
                session.set_leverage(symbol=symbol["name"], buy_leverage=25, sell_leverage=25)
                print(symbol["name"] + " now set to Leverage 25")
            except Exception:
                pass
                
            try:
                session.set_leverage(symbol=symbol["name"], buy_leverage=50, sell_leverage=50)
                print(symbol["name"] + " now set to Leverage 50")
            except Exception:
                pass
                
            try:
                session.set_leverage(symbol=symbol["name"], buy_leverage=100, sell_leverage=100)
                print(symbol["name"] + " now set to Leverage 100")
            except Exception:
                pass
                
        else: # Inverse Perpetuals or Futures
            try:
                session.set_leverage(symbol=symbol["name"], leverage=12.5)
                print(symbol["name"] + " now set to Leverage 12.5")
            except Exception:
                pass
                
            try:
                session.set_leverage(symbol=symbol["name"], leverage=25)
                print(symbol["name"] + " now set to Leverage 25")
            except Exception:
                pass
                
            try:
                session.set_leverage(symbol=symbol["name"], leverage=50)
                print(symbol["name"] + " now set to Leverage 50")
            except Exception:
                pass
                
            try:
                session.set_leverage(symbol=symbol["name"], leverage=100)
                print(symbol["name"] + " now set to Leverage 100")
            except Exception:
                pass
          '''      
                
    # print("Max Leverage changed for all pairs!")
    # sleep(3600) # Wait for an hour to manually exit the script

                
        
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
        if(enable_db_features):
            ### First check if Database has any actions ###
            # Any Scaled Orders requests in the Database queued?
            
            mycursor = mydb.cursor(dictionary=True)
            mycursor.execute("SELECT * FROM scaled_orders WHERE api_key='"+api_key+"' AND api_secret='"+api_secret+"'")
            myresult = mycursor.fetchall()
            for scaled_order in myresult:
                error = False
                # First check if Symbol exists on the Exchange
                if scaled_order['symbol'] not in instruments:
                    error = "Instrument not found on exchange"

                # Distribute an amount based on weighting
                if (int(scaled_order['orderCount']) < 2 or int(scaled_order['orderCount']) > 200):
                    error = "Number of orders must be between 2 and 200"

                if not error:
                    weights = map(lambda x: 100 / int(scaled_order['orderCount']), _.range(int(scaled_order['orderCount']))) # Get distribution weights
                    weightsList = list(weights)
                    distributedTotal = []
                    distributionSum = _.sum(weightsList)
                    for weight in weightsList:
                        if _.sum(distributedTotal) <  float(scaled_order['amount']):
                            val = round_step_size((weight * float(scaled_order['amount'])) / distributionSum,qty_step[scaled_order['symbol']],min_trading_qty[scaled_order['symbol']])
                            if _.sum(distributedTotal) + val <= float(scaled_order['amount']):
                                distributedTotal.append(val)
                            else:
                                val = round_step_size((float(scaled_order['amount']) - _.sum(distributedTotal)),qty_step[scaled_order['symbol']],min_trading_qty[scaled_order['symbol']])
                                distributedTotal.append(val)

                    priceDiff = float(scaled_order['priceUpper']) - float(scaled_order['priceLower'])
                    stepsPerPricePoint = priceDiff / (int(scaled_order['orderCount']) - 1)

                    # Generate the prices we're placing orders at
                    
                    final_decimals_count = str(tick_size[scaled_order['symbol']])[::-1].find('.') # Tick Size number of decimals - 1
                    
                    orderPrices = map(lambda i: float(scaled_order['priceLower']) if i is 0 else (float(scaled_order['priceUpper']) if i is int(scaled_order['orderCount']) - 1 else float(scaled_order['priceLower']) + stepsPerPricePoint * i), _.range(int(scaled_order['orderCount']))) # Get distribution weights
                    orderPrices = map(lambda price: round(float(price), final_decimals_count), orderPrices)
                    
                    orders = {}
                    minPrice = float('inf')
                    maxPrice = float('-inf')

                    orderPrices = list(orderPrices)
                    
                    for index in range(len(distributedTotal)):
                        minPrice = min(minPrice, orderPrices[index])
                        maxPrice = max(maxPrice, orderPrices[index])
                        
                        orders.update( {orderPrices[index] : distributedTotal[index]} )

                    # Verify that the generated orders match the specification
                    if (minPrice < float(scaled_order['priceLower'])):
                        error = "Order is lower than the specified lower price"
                    if (maxPrice > float(scaled_order['priceUpper'])):
                        error = "Order is higher than the specified upper price"

                    if not error:
                        # Now place the orders on exchange's order book
                        for order_price, order_amount in orders.items():
                            if scaled_order['orderExec'] == 'Open':
                                try:
                                    session.place_active_order(symbol=scaled_order['symbol'], side=scaled_order['side'], order_type=scaled_order['ordertype'], qty=order_amount, price=order_price, close_on_trigger=False, reduce_only=False, time_in_force="PostOnly")
                                    log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + scaled_order['symbol'] + " Scaled Open Order Placed: "+str(scaled_order['side'])+" "+str(scaled_order['ordertype'])+" "+str(order_amount)+" @ "+str(order_price)+"."
                                    print(log)
                                    with open("ScaledOrders.txt", "a") as myfile:
                                        myfile.write(log+'\n')
                                except Exception:
                                    pass
                            elif scaled_order['orderExec'] == 'Close':
                                try:
                                    session.place_active_order(symbol=scaled_order['symbol'], side=scaled_order['side'], order_type=scaled_order['ordertype'], qty=order_amount, price=order_price, close_on_trigger=True, reduce_only=True, time_in_force="PostOnly")
                                    log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + scaled_order['symbol'] + " Scaled Close Order Placed: "+str(scaled_order['side'])+" "+str(scaled_order['ordertype'])+" "+str(order_amount)+" @ "+str(order_price)+"."
                                    print(log)
                                    with open("ScaledOrders.txt", "a") as myfile:
                                        myfile.write(log+'\n')
                                except Exception:
                                    pass
                try:
                    mycursor.execute("DELETE FROM scaled_orders WHERE id="+str(scaled_order['id']))
                    mydb.commit()
                except Exception:
                    pass

        ### Now we work with active Positions ###
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
        
        # First we clear all
        # 1) TB SLs and Initial Total Balance SLs database (if exists). We loop through active positions, and DELETE from DB any position for pairs other than those (that are active and got Initial Total Balance Stop Loss executed for).
        # 2) Position Sessions that are not active anymore
        active_positions_string_excluded = ""
        active_positions_sessions_string_excluded = ""
        for position in fetched_sessions:
            symbol = position["symbol"]
            side = position["side"]
            active_positions_string_excluded += " AND NOT (symbol = '"+symbol+"' AND side = '"+side+"')"
            active_positions_sessions_string_excluded += " AND NOT (symbol = '"+symbol+"')"
        # Now we remove all DB entries for any positions other than the currently Active ones
        try:
            mycursor.execute("DELETE FROM positions_stops WHERE api_key = '"+api_key+"' AND api_secret = '"+api_secret+"' "+active_positions_string_excluded)
            mydb.commit()
        except Exception:
            pass

        try:
            mycursor.execute("DELETE FROM positions_tb_sl WHERE api_key = '"+api_key+"' AND api_secret = '"+api_secret+"' "+active_positions_string_excluded)
            mydb.commit()
        except Exception:
            pass
            
        try:
            mycursor.execute("DELETE FROM positions_sessions WHERE api_key = '"+api_key+"' AND api_secret = '"+api_secret+"' "+active_positions_sessions_string_excluded)
            mydb.commit()
        except Exception:
            pass            
            
        # Now we INSERT Positions Sessions that are active OR UPDATE their Total Balance value if a hedge already locked the full position value
        for position in fetched_sessions:
            symbol = position["symbol"]
            side = position["side"]
            long_pos_size = 0
            short_pos_size = 0
            long_pos_value = 0
            short_pos_value = 0
            
            hedge_found = False
            balanced_hedge_found = False
            if position['side'] == "Sell":
                opposite_side = "Buy"
                short_pos_size = position['size']
                short_pos_value = position['position_value']
            elif position['side'] == "Buy":
                opposite_side = "Sell"
                long_pos_size = position['size']
                long_pos_value = position['position_value']
            # Now we loop open positions to find is opposite position side exists and is balanced (same sizes)
            for position2 in fetched_sessions:
                if position2['symbol'] == position['symbol'] and position2['side'] == opposite_side:
                    if position['side'] == "Sell":
                        long_pos_size = position2['size']
                        long_pos_value = position2['position_value']
                    elif position['side'] == "Buy":
                        short_pos_size = position2['size']
                        short_pos_value = position2['position_value']
                    
                    hedge_found = True
                    if position2['size'] == position['size']:
                        balanced_hedge_found = True
                    
            # Fetch latest Balance value
            if quote_currency[symbol] == "USDT":
                equity = session.get_wallet_balance(coin="USDT")["result"]["USDT"]["equity"]
            else:
                equity = session.get_wallet_balance(coin=base_currency[symbol])["result"][base_currency[symbol]]["equity"]
            
            # Fetch last_price to store it realtime
            try:
                fetched_latest_tickers = session.latest_information_for_symbol(symbol=symbol)['result']
            except Exception:
                pass
            if(fetched_latest_tickers):
                for ticker in fetched_latest_tickers:
                    if ticker['symbol'] == symbol:
                        last_price = float(ticker['last_price'])
            
            if hedge_found:
                if balanced_hedge_found:
                    # Balanced hedge exists, so UPDATE the Balance of the session
                    try:
                        mycursor_add_positions_sessions = mydb.cursor(dictionary=True)
                        insert_sql = "INSERT INTO positions_sessions (api_key, api_secret, symbol, last_balanced_equity, realtime_equity, realtime_price, hedged, balanced_hedge, last_updated, current_long_pos_size, current_short_pos_size, current_long_pos_value, current_short_pos_value, current_balancer_hedge_price) VALUES (%s, %s, %s, %s, %s, %s, 1, 1, NOW(), %s, %s, %s, %s, NULL) ON DUPLICATE KEY UPDATE last_balanced_equity=%s, highest_equity = GREATEST(highest_equity, %s), hedged=1, balanced_hedge=1, last_updated=NOW(), realtime_equity=%s, realtime_price=%s, current_long_pos_size=%s, current_short_pos_size=%s, current_long_pos_value=%s, current_short_pos_value=%s, current_balancer_hedge_price=NULL;"
                        vals = (api_key, api_secret, symbol, equity, equity, last_price, long_pos_size, short_pos_size, long_pos_value, short_pos_value, equity, equity, equity, last_price, long_pos_size, short_pos_size, long_pos_value, short_pos_value)
                        mycursor_add_positions_sessions.execute(insert_sql, vals)
                        mydb.commit()
                    except Exception:
                        pass
                else:
                    # Just a hedge exists, so UPDATE just mark that
                    try:
                        mycursor_add_positions_sessions = mydb.cursor(dictionary=True)
                        insert_sql = "INSERT INTO positions_sessions (api_key, api_secret, symbol, hedged, last_updated, current_long_pos_size, current_short_pos_size, current_long_pos_value, current_short_pos_value, realtime_equity, realtime_price) VALUES (%s, %s, %s, 1, NOW(), %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE hedged=1, last_updated=NOW(), current_long_pos_size=%s, current_short_pos_size=%s, current_long_pos_value=%s, current_short_pos_value=%s, realtime_equity=%s, realtime_price=%s;"
                        vals = (api_key, api_secret, symbol, long_pos_size, short_pos_size, long_pos_value, short_pos_value, equity, last_price, long_pos_size, short_pos_size, long_pos_value, short_pos_value, equity, last_price)
                        mycursor_add_positions_sessions.execute(insert_sql, vals)
                        mydb.commit()
                    except Exception:
                        pass
                    
            else:
                # No Balanced hedge exists, so only INSERT new row to the database (if it doesn't exist)
                try:
                    mycursor_add_positions_sessions = mydb.cursor(dictionary=True)
                    insert_sql = "INSERT INTO positions_sessions (api_key, api_secret, symbol, initial_equity, highest_equity, realtime_equity, realtime_price, current_long_pos_size, current_short_pos_size, current_long_pos_value, current_short_pos_value) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE current_long_pos_size=%s, current_short_pos_size=%s, current_long_pos_value=%s, current_short_pos_value=%s, realtime_equity=%s, realtime_price=%s;"
                    vals = (api_key, api_secret, symbol, equity, equity, equity, last_price, long_pos_size, short_pos_size, long_pos_value, short_pos_value, long_pos_size, short_pos_size, long_pos_value, short_pos_value, equity, last_price)
                    mycursor_add_positions_sessions.execute(insert_sql, vals)
                    mydb.commit()
                except Exception:
                    pass
                    
        # Now we clear any Genie Hedges pending Conditional Orders (stored in the DB) left if opposite positions already closed manually OR positions of both sides exist and it is not a Balancer Hedge
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute("SELECT * FROM positions_hedges WHERE api_key='"+api_key+"' AND api_secret='"+api_secret+"'")
        myresult = mycursor.fetchall()
        for position_hedge in myresult:
            if position_hedge['order_link_id'].startswith('CryptoGenieHedge'):
                # Note: order side should be opposite of position side
                same_side_position_found = False
                opposite_side_position_found = False
                if position_hedge['side'] == "Sell":
                    conditional_opposite_side = "Buy"
                elif position_hedge['side'] == "Buy":
                    conditional_opposite_side = "Sell"
                # Now we loop open positions to find what position sides are open for this asset
                for position in fetched_sessions:
                    if position["symbol"] == position_hedge['symbol'] and position["side"] == position_hedge['side']:
                        same_side_position_found = True
                    if position["symbol"] == position_hedge['symbol'] and position["side"] == conditional_opposite_side:
                        opposite_side_position_found = True

                if not opposite_side_position_found or (opposite_side_position_found and same_side_position_found):
                    # Position opposite of Hedge not found, so we remove this Hedge conditional order
                    # OR If we found both sides positions open
                    try:
                        session.cancel_conditional_order(symbol=position_hedge['symbol'], stop_order_id=position_hedge['stop_order_id'])
                    except Exception:
                        pass
                        
                    try:
                        mycursor.execute("DELETE FROM positions_hedges WHERE stop_order_id='"+position_hedge['stop_order_id']+"' and api_key='"+api_key+"' AND api_secret='"+api_secret+"'")
                        mydb.commit()
                    except Exception:
                        pass

                                
        # Now we go through all positions to perform Genie's operations :-)
        for position in fetched_sessions:
            position_idx = ""
            mode = ""
            
            symbol = position["symbol"]
            side = position["side"]
            size = float(position["size"])
            position_value = float(position["position_value"])
            leverage = float(position["leverage"])
            stop_loss = float(position["stop_loss"])
            entry_price = float(position["entry_price"])
            # unrealised_pnl = float(position["unrealised_pnl"]) # We will not use this as the current API is not returning the real-time unrealised_pnl value properly, we will need to manually calculate it for each position
            final_decimals_count = str(tick_size[symbol])[::-1].find('.') # Tick Size number of decimals
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
                                position_leveraged_stop_loss = round_to_tick(entry_price - (((stop_loss_cap_ratio/100) / leverage) * entry_price), tick_size[symbol])
                                if last_price < position_leveraged_stop_loss:
                                    try:
                                        session.place_active_order(position_idx=position_idx, symbol=symbol, side="Sell", order_type="Market", qty=size, time_in_force="GoodTillCancel", reduce_only=True, close_on_trigger=True)
                                        log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " LONG Force-Stopped: "+str(last_price)+"."
                                        print(log)
                                        with open("SL_forced.txt", "a") as myfile:
                                            myfile.write(log+'\n')
                                    except Exception:
                                        pass
                            elif side == 'Sell':
                                position_leveraged_stop_loss = round_to_tick(entry_price + (((stop_loss_cap_ratio/100) / leverage) * entry_price), tick_size[symbol])
                                if last_price > position_leveraged_stop_loss:
                                    try:
                                        session.place_active_order(position_idx=position_idx, symbol=symbol, side="Buy", order_type="Market", qty=size, time_in_force="GoodTillCancel", reduce_only=True, close_on_trigger=True)
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
                            # Note: order side should be opposite of position side
                            if side == "Buy" and conditional_order['side'] == "Sell" and conditional_order['order_type'] == 'Market' and conditional_order['order_status'] == 'Untriggered': # Stop Loss for a Long
                                if symbol.endswith('USDT'): # USDT Perpetual
                                    stop_price = float(conditional_order['trigger_price'])
                                    stop_order_id = conditional_order['stop_order_id']
                                    if stop_price < entry_price and conditional_order['close_on_trigger'] == True and conditional_order['reduce_only'] == True:
                                        position_leveraged_stop_loss = round_to_tick(entry_price - (((stop_loss_cap_ratio/100) / leverage) * entry_price), tick_size[symbol])
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
                                    position_leveraged_stop_loss = round_to_tick(entry_price - (((stop_loss_cap_ratio/100) / leverage) * entry_price), tick_size[symbol])
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
                                        position_leveraged_stop_loss = round_to_tick(entry_price + (((stop_loss_cap_ratio/100) / leverage) * entry_price), tick_size[symbol])
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
                                    position_leveraged_stop_loss = round_to_tick(entry_price + (((stop_loss_cap_ratio/100) / leverage) * entry_price), tick_size[symbol])
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
                        set_trading_stop_args = {'position_idx': position_idx, 'symbol': symbol, 'side': side}
                        if tp_sl_mode == "Partial":
                            set_trading_stop_args['sl_size'] = size # If Partial Mode then we need to send full size to close full position
                        
                        if side == 'Buy':
                            position_leveraged_stop_loss = round_to_tick(entry_price - (((stop_loss_cap_ratio/100) / leverage) * entry_price), tick_size[symbol])
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
                            position_leveraged_stop_loss = round_to_tick(entry_price + (((stop_loss_cap_ratio/100) / leverage) * entry_price), tick_size[symbol])
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
                                position_leveraged_stop_loss = round_to_tick(entry_price - (((stop_loss_cap_ratio/100) / leverage) * entry_price), tick_size[symbol])
                                if last_price < position_leveraged_stop_loss:
                                    try:
                                        session.place_active_order(position_idx=position_idx, symbol=symbol, side="Sell", order_type="Market", qty=size, time_in_force="GoodTillCancel", reduce_only=True, close_on_trigger=True)
                                        log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " LONG Force-Stopped: "+str(last_price)+"."
                                        print(log)
                                        with open("SL_forced.txt", "a") as myfile:
                                            myfile.write(log+'\n')
                                    except Exception:
                                        pass
                            elif side == 'Sell':
                                position_leveraged_stop_loss = round_to_tick(entry_price + (((stop_loss_cap_ratio/100) / leverage) * entry_price), tick_size[symbol])
                                if last_price > position_leveraged_stop_loss:
                                    try:
                                        session.place_active_order(position_idx=position_idx, symbol=symbol, side="Buy", order_type="Market", qty=size, time_in_force="GoodTillCancel", reduce_only=True, close_on_trigger=True)
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
                            # Note: order side should be opposite of position side
                            if side == "Buy" and conditional_order['side'] == "Sell" and conditional_order['order_type'] == 'Market' and conditional_order['order_status'] == 'Untriggered': # Stop Loss for a Long
                                if symbol.endswith('USDT'): # USDT Perpetual
                                    stop_price = float(conditional_order['trigger_price'])
                                    stop_order_id = conditional_order['stop_order_id']
                                    if stop_price < entry_price and conditional_order['close_on_trigger'] == True and conditional_order['reduce_only'] == True:
                                        position_leveraged_stop_loss = round_to_tick((entry_price - (((stop_loss_cap_ratio/100) / leverage) * entry_price)), tick_size[symbol])
                                        if stop_price >= position_leveraged_stop_loss and float(conditional_order['qty']) == size:
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
                                    position_leveraged_stop_loss = round_to_tick((entry_price - (((stop_loss_cap_ratio/100) / leverage) * entry_price)), tick_size[symbol])
                                    
                                    if stop_price >= position_leveraged_stop_loss and float(conditional_order['qty']) == size:
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
                                        position_leveraged_stop_loss = round_to_tick((entry_price + (((stop_loss_cap_ratio/100) / leverage) * entry_price)), tick_size[symbol])
                                        if stop_price <= position_leveraged_stop_loss and float(conditional_order['qty']) == size:
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
                                    position_leveraged_stop_loss = round_to_tick((entry_price + (((stop_loss_cap_ratio/100) / leverage) * entry_price)), tick_size[symbol])
                                    if stop_price <= position_leveraged_stop_loss and float(conditional_order['qty']) == size:
                                        # Stop Loss found inside the allowed range, keep it
                                        total_allowed_stop_loss_found += float(conditional_order['qty'])
                                    else:
                                        # Stop Loss found outside the allowed range, useless so remove it
                                        try:
                                            session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id)
                                        except Exception:
                                            pass
                    if total_allowed_stop_loss_found < size:
                        # We couldn't find enough Stop Losses in the allowed range, so remove any conditional orders and add 1 Stop Loss conditional order with total size, at the correct level
                        # Prepare set_trading_stop arguments to pass to API
                        set_trading_stop_args = {'position_idx': position_idx, 'symbol': symbol, 'side': side}
                        if tp_sl_mode == "Partial":
                            set_trading_stop_args['sl_size'] = size # If Partial Mode then we need to send full size to close full position
                        
                        if side == 'Buy':
                            position_leveraged_stop_loss = round_to_tick(entry_price - (((stop_loss_cap_ratio/100) / leverage) * entry_price), tick_size[symbol])
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
                            position_leveraged_stop_loss = round_to_tick(entry_price + (((stop_loss_cap_ratio/100) / leverage) * entry_price), tick_size[symbol])
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
                                                    tp_price_ratio = float(elem[0])
                                                    tp_size_ratio = float(elem[1])
                                                    tp_price = round_to_tick(entry_price + (((tp_price_ratio/100) / leverage) * entry_price), tick_size[symbol])
                                                    tp_size = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])
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
                                                    tp_price_ratio = float(elem[0])
                                                    tp_size_ratio = float(elem[1])
                                                    tp_price = round_to_tick(entry_price + (((tp_price_ratio/100) / leverage) * entry_price), tick_size[symbol])
                                                    tp_size = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])
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
                                set_trading_stop_args = {'position_idx': position_idx, 'symbol': symbol, 'side': side}
                                
                                for elem in sorted(default_tp.items(), reverse=False): # Sort Ascending to find the nearest TP level
                                    tp_price_ratio = float(elem[0])
                                    tp_size_ratio = float(elem[1])
                                    
                                    set_trading_stop_args['take_profit'] = round_to_tick(entry_price + (((tp_price_ratio/100) / leverage) * entry_price), tick_size[symbol])
                                    set_trading_stop_args['tp_size'] = tp_size = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])
                                    
                                    if last_price < set_trading_stop_args['take_profit'] - (default_tp_tolerance_ratio/100) * (set_trading_stop_args['take_profit'] - entry_price):
                                        try:
                                            session.set_trading_stop(**set_trading_stop_args)
                                            log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " LONG Take-Profit Market placed: "+str(tp_size_ratio)+"% of Quantity ("+str(set_trading_stop_args['tp_size'])+") @ "+ str(tp_price_ratio) +"% in Profit ("+str(set_trading_stop_args['take_profit'])+")."
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
                                                    tp_price_ratio = float(elem[0])
                                                    tp_size_ratio = float(elem[1])
                                                    tp_price = round_to_tick(entry_price - (((tp_price_ratio/100) / leverage) * entry_price), tick_size[symbol])
                                                    tp_size = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])
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
                                                    tp_price_ratio = float(elem[0])
                                                    tp_size_ratio = float(elem[1])
                                                    tp_price = round_to_tick(entry_price - (((tp_price_ratio/100) / leverage) * entry_price), tick_size[symbol])
                                                    tp_size = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])
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
                                set_trading_stop_args = {'position_idx': position_idx, 'symbol': symbol, 'side': side}
                                
                                for elem in sorted(default_tp.items(), reverse=False): # Sort Ascending to find the nearest TP level
                                    tp_price_ratio = float(elem[0])
                                    tp_size_ratio = float(elem[1])
                                    
                                    set_trading_stop_args['take_profit'] = round_to_tick(entry_price - (((tp_price_ratio/100) / leverage) * entry_price), tick_size[symbol])
                                    set_trading_stop_args['tp_size'] = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])

                                    if last_price > set_trading_stop_args['take_profit'] + (default_tp_tolerance_ratio/100) * (entry_price - set_trading_stop_args['take_profit']):
                                        try:
                                            session.set_trading_stop(**set_trading_stop_args)
                                            log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " SHORT Take-Profit Market placed: "+str(tp_size_ratio)+"% of Quantity ("+str(set_trading_stop_args['tp_size'])+") @ "+ str(tp_price_ratio) +"% in Profit ("+str(set_trading_stop_args['take_profit'])+")."
                                            print(log)
                                            with open("TP.txt", "a") as myfile:
                                                myfile.write(log+'\n')
                                            break # No need to add more TPs, we only place 1 TP at a time
                                        except Exception:
                                            pass  
                
            if(enforce_tp_limit):
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
                                fetched_active_orders = session.query_active_order(symbol=symbol)
                            except Exception:
                                pass
                            if(fetched_active_orders):
                                for active_order in fetched_active_orders["result"]:
                                    if not tp_found: # If we found a valid TP, no need to iterate any more
                                        if symbol.endswith('USDT'): # USDT Perpetual
                                            limit_price = float(active_order['price'])
                                            order_id = active_order['order_id']

                                            if active_order['side'] == 'Sell' and limit_price > last_price and limit_price > entry_price and active_order['reduce_only'] == True:
                                                # Take Profit found, make sure it is one of the pre-defined ones and make sure its quantity is up to date as well
                                                for elem in default_tp.items():
                                                    tp_price_ratio = float(elem[0])
                                                    tp_size_ratio = float(elem[1])
                                                    tp_price = round_to_tick(entry_price + (((tp_price_ratio/100) / leverage) * entry_price), tick_size[symbol])
                                                    tp_size = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])
                                                    limit_size = round_step_size(active_order['qty'], qty_step[symbol],min_trading_qty[symbol])
                                                    if close_enough_match(tp_price, limit_price, tp_size, limit_size, "Buy"): # tp_price==limit_price and tp_size == limit_size # (tp_size==active_order['qty'] or math.floor(tp_size * 10)/10.0==active_order['qty'] or math.floor(tp_size * 100)/100.0==active_order['qty'] or math.floor(tp_size * 1000)/1000.0==active_order['qty'] or math.floor(tp_size * 10000)/10000.0==active_order['qty']):
                                                        # We found a valid pre-defined TP, keep it (note we check the floor in case the exchange did remove decimals upon creating the order)
                                                        tp_found = True
                                                if not tp_found:
                                                    # Invalid TP (or updated position size not reflected in the TP), REMOVE IT
                                                    try:
                                                        session.cancel_active_order(symbol=symbol, order_id=order_id) 
                                                    except Exception:
                                                        pass
                                        else: # Inverse Perpetuals or Futures
                                            limit_price = float(active_order['price'])
                                            order_id = active_order['order_id']
                                            if active_order['side'] == 'Sell' and limit_price > last_price and limit_price > entry_price:
                                                # Take Profit found, make sure it is one of the pre-defined ones and make sure its quantity is up to date as well
                                                for elem in default_tp.items():
                                                    tp_price_ratio = float(elem[0])
                                                    tp_size_ratio = float(elem[1])
                                                    tp_price = round_to_tick(entry_price + (((tp_price_ratio/100) / leverage) * entry_price), tick_size[symbol])
                                                    tp_size = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])
                                                    limit_size = round_step_size(active_order['qty'], qty_step[symbol],min_trading_qty[symbol])
                                                    if close_enough_match(tp_price, limit_price, tp_size, limit_size, "Buy"): # tp_price==limit_price and tp_size == limit_size # (tp_size==active_order['qty'] or math.floor(tp_size * 10)/10.0==active_order['qty'] or math.floor(tp_size * 100)/100.0==active_order['qty'] or math.floor(tp_size * 1000)/1000.0==active_order['qty'] or math.floor(tp_size * 10000)/10000.0==active_order['qty']):
                                                        # We found a valid pre-defined TP, keep it (note we check the floor in case the exchange did remove decimals upon creating the order)
                                                        tp_found = True
                                                if not tp_found:
                                                    # Invalid TP (or updated position size not reflected in the TP), REMOVE IT
                                                    try:
                                                        session.cancel_active_order(symbol=symbol, order_id=order_id) 
                                                    except Exception:
                                                        pass
                   
                            if not tp_found: # No TPs found, so add (this way we kind of avoid re-adding the same TP if price hit and found resistance at and retested it. so we don't TP the same level twice)
                                # We couldn't find any TPs, let's add the suitable one
                                # Prepare set_trading_stop arguments to pass to API
                                limit_tp_args = {'position_idx': position_idx, 'symbol': symbol, 'side': 'Sell', 'order_type': "Limit", 'time_in_force': "PostOnly", 'reduce_only': True, 'close_on_trigger': True }
                                
                                for elem in sorted(default_tp.items(), reverse=False): # Sort Ascending to find the nearest TP level
                                    tp_price_ratio = float(elem[0])
                                    tp_size_ratio = float(elem[1])
                                    
                                    limit_tp_args['price'] = round_to_tick(entry_price + (((tp_price_ratio/100) / leverage) * entry_price), tick_size[symbol])
                                    limit_tp_args['qty'] = tp_size = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])
                                    
                                    if last_price < limit_tp_args['price'] - (default_tp_tolerance_ratio/100) * (limit_tp_args['price'] - entry_price):
                                        try:
                                            session.place_active_order(**limit_tp_args)
                                            log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " LONG Take-Profit Limit placed: "+str(tp_size_ratio)+"% of Quantity ("+str(limit_tp_args['qty'])+") @ "+ str(tp_price_ratio) +"% in Profit ("+str(limit_tp_args['price'])+")."
                                            print(log)
                                            with open("TP.txt", "a") as myfile:
                                                myfile.write(log+'\n')
                                            break # No need to add more TPs, we only place 1 TP at a time
                                        except Exception as e:
                                            print(e)
                                            pass                 
                                
                        elif side == 'Sell':   
                            # Sarch Conditional Orders if Take Profits already exist
                            tp_found = False
                            
                            try:
                                fetched_active_orders = session.query_active_order(symbol=symbol)
                            except Exception:
                                pass
                            if(fetched_active_orders):
                                for active_order in fetched_active_orders["result"]:
                                    if not tp_found: # If we found a valid TP, no need to iterate any more
                                        if symbol.endswith('USDT'): # USDT Perpetual
                                            limit_price = float(active_order['price'])
                                            order_id = active_order['order_id']

                                            if active_order['side'] == 'Buy' and limit_price < last_price and limit_price < entry_price and active_order['reduce_only'] == True:
                                                # Take Profit found, make sure it is one of the pre-defined ones and make sure its quantity is up to date as well
                                                for elem in default_tp.items():
                                                    tp_price_ratio = float(elem[0])
                                                    tp_size_ratio = float(elem[1])
                                                    tp_price = round_to_tick(entry_price - (((tp_price_ratio/100) / leverage) * entry_price), tick_size[symbol])
                                                    tp_size = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])
                                                    limit_size = round_step_size(active_order['qty'], qty_step[symbol],min_trading_qty[symbol])
                                                    if close_enough_match(tp_price, limit_price, tp_size, limit_size, "Sell"): # tp_price==limit_price and tp_size == limit_size # (tp_size==active_order['qty'] or math.floor(tp_size * 10)/10.0==active_order['qty'] or math.floor(tp_size * 100)/100.0==active_order['qty'] or math.floor(tp_size * 1000)/1000.0==active_order['qty'] or math.floor(tp_size * 10000)/10000.0==active_order['qty']):
                                                        # We found a valid pre-defined TP, keep it (note we check the floor in case the exchange did remove decimals upon creating the order)
                                                        tp_found = True
                                                if not tp_found:
                                                    # Invalid TP (or updated position size not reflected in the TP), REMOVE IT
                                                    try:
                                                        session.cancel_active_order(symbol=symbol, order_id=order_id) 
                                                    except Exception:
                                                        pass
                                        else: # Inverse Perpetuals or Futures
                                            limit_price = float(active_order['price'])
                                            order_id = active_order['order_id']
                                            if active_order['side'] == 'Buy' and limit_price < last_price and limit_price < entry_price:
                                                # Take Profit found, make sure it is one of the pre-defined ones and make sure its quantity is up to date as well
                                                for elem in default_tp.items():
                                                    tp_price_ratio = float(elem[0])
                                                    tp_size_ratio = float(elem[1])
                                                    tp_price = round_to_tick(entry_price - (((tp_price_ratio/100) / leverage) * entry_price), tick_size[symbol])
                                                    tp_size = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])
                                                    limit_size = round_step_size(active_order['qty'], qty_step[symbol],min_trading_qty[symbol])
                                                    if close_enough_match(tp_price, limit_price, tp_size, limit_size, "Sell"): # tp_price==limit_price and tp_size == limit_size # (tp_size==active_order['qty'] or math.floor(tp_size * 10)/10.0==active_order['qty'] or math.floor(tp_size * 100)/100.0==active_order['qty'] or math.floor(tp_size * 1000)/1000.0==active_order['qty'] or math.floor(tp_size * 10000)/10000.0==active_order['qty']):
                                                        # We found a valid pre-defined TP, keep it (note we check the floor in case the exchange did remove decimals upon creating the order)
                                                        tp_found = True
                                                if not tp_found:
                                                    # Invalid TP (or updated position size not reflected in the TP), REMOVE IT
                                                    try:
                                                        session.cancel_active_order(symbol=symbol, order_id=order_id) 
                                                    except Exception:
                                                        pass
                   
                            if not tp_found: # No TPs found, so add (this way we kind of avoid re-adding the same TP if price hit and found resistance at and retested it. so we don't TP the same level twice)
                                # We couldn't find any TPs, let's add the suitable one
                                # Prepare set_trading_stop arguments to pass to API
                                limit_tp_args = {'position_idx': position_idx, 'symbol': symbol, 'side': 'Buy', 'order_type': "Limit", 'time_in_force': "PostOnly", 'reduce_only': True, 'close_on_trigger': True }
                                
                                for elem in sorted(default_tp.items(), reverse=False): # Sort Ascending to find the nearest TP level
                                    tp_price_ratio = float(elem[0])
                                    tp_size_ratio = float(elem[1])
                                    
                                    limit_tp_args['price'] = round_to_tick(entry_price - (((tp_price_ratio/100) / leverage) * entry_price), tick_size[symbol])
                                    limit_tp_args['qty'] = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])

                                    if last_price > limit_tp_args['price'] + (default_tp_tolerance_ratio/100) * (entry_price - limit_tp_args['price']):
                                        try:
                                            session.place_active_order(**limit_tp_args)
                                            log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " SHORT Take-Profit Limit placed: "+str(tp_size_ratio)+"% of Quantity ("+str(limit_tp_args['qty'])+") @ "+ str(tp_price_ratio) +"% in Profit ("+str(limit_tp_args['price'])+")."
                                            print(log)
                                            with open("TP.txt", "a") as myfile:
                                                myfile.write(log+'\n')
                                            break # No need to add more TPs, we only place 1 TP at a time
                                        except Exception as e:
                                            print(e)
                                            pass
            
            #######################################################
            # Enforce Take Profits at Dynamic Levels
            #######################################################
            
            if(enforce_tp_dynamic):
                # Fetch latest tickers
                try:
                    fetched_latest_tickers = session.latest_information_for_symbol(symbol=symbol)['result']
                except Exception:
                    pass
                if(fetched_latest_tickers):
                    for ticker in fetched_latest_tickers:
                        if ticker['symbol'] == symbol:
                            last_price = float(ticker['last_price'])     
                if symbol in tp_dynamic: # Look if any dynamic take profit is to be applied for the symbol
                    tp_dynamic_indicators = tp_dynamic[symbol]["indicators"]
                    tp_dynamic_maximum_ratio = tp_dynamic[symbol]["maximum_ratio"]
                    tp_dynamic_minimum_ratio = tp_dynamic[symbol]["minimum_ratio"]
                    tp_dynamic_tolerance_ratio = tp_dynamic[symbol]["tolerance_ratio"]
                    
                    # If for any reason the bot was off and the current price is past the maximum profit ratio, we need to close at current price (target or more profit) rather than still closing at less profit
                    if (side == "Buy" and last_price > entry_price + (entry_price * tp_dynamic_maximum_ratio/100)) or (side == "Sell" and last_price < entry_price - (entry_price * tp_dynamic_maximum_ratio/100)):
                        # Market Close the position as we already passed the maximum target profit ratio
                        try:
                            if side == "Buy":
                                session.place_active_order(position_idx=position_idx, symbol=symbol, side="Sell", order_type="Market", qty=size, time_in_force="GoodTillCancel", reduce_only=True, close_on_trigger=True)
                                log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " LONG Dynamic Take Profit Market Close at: "+str(round(last_price, final_decimals_count))+"."
                            elif side == "Sell":
                                session.place_active_order(position_idx=position_idx, symbol=symbol, side="Buy", order_type="Market", qty=size, time_in_force="GoodTillCancel", reduce_only=True, close_on_trigger=True)
                                log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + "SHORT Dynamic Take Profit Market Close at: "+str(round(last_price, final_decimals_count))+"."
                            print(log)
                            with open("TP.txt", "a") as myfile:
                                myfile.write(log+'\n')
                        except Exception:
                            pass
                    else:
                        # We will Take Profits at defined Dynamic Levels (indicators) for the defined Timeframes
                        for elem in tp_dynamic_indicators.items():
                            pagesize = 200
                            interval = int(elem[0])
                            # Pull the kline data for the interval (timeframe). Maximum allowed kline data is 200
                            now = datetime.utcnow()
                            unixtime = calendar.timegm(now.utctimetuple())
                            since = unixtime - 60 * interval * pagesize
                            response=session.query_kline(symbol=symbol, interval=str(interval), **{'from':since})['result']
                            df = pd.DataFrame(response)
                            break_direction = '' # Flag direction of break if any indicator was broken (used for executing Market Order Close)
                            limit_close_price_levels = [] # Used to store all price levels found for Limit Close Orders
                            market_close_price_levels = [] # Used to store all price levels found for Market Close Orders
                            for dynamic_level in elem[1].split(','): # Now we fetch the requested Dynamic Levels (indicators) for that interval
                                ordertype = dynamic_level.split('#')[1]
                                indicator = dynamic_level.split('#')[0].split('_')[0]
                                length = int(dynamic_level.split('#')[0].split('_')[1])
                                if indicator == 'ema':
                                    indicator_data = ta.ema(df['close'].astype(float, errors = 'raise'), length=length)
                                    if ordertype == 'Limit':
                                        if side == 'Buy' and 0 < (indicator_data.iloc[-1] - (indicator_data.iloc[-1] * (tp_dynamic_tolerance_ratio/100))) - entry_price < (entry_price * tp_dynamic_maximum_ratio/100):
                                            limit_close_price_levels.append(indicator_data.iloc[-1] - (indicator_data.iloc[-1] * (tp_dynamic_tolerance_ratio/100)))
                                        elif side == 'Sell' and 0 > (indicator_data.iloc[-1] + (indicator_data.iloc[-1] * (tp_dynamic_tolerance_ratio/100))) - entry_price > -1 * (entry_price * tp_dynamic_maximum_ratio/100):
                                            limit_close_price_levels.append(indicator_data.iloc[-1] + (indicator_data.iloc[-1] * (tp_dynamic_tolerance_ratio/100)))
                                    elif ordertype == 'Market':    
                                        market_close_price_levels.append(indicator_data.iloc[-1]) # Indicator Price Point to Take Profit at as Market Close Order
                                        price_indicator_diff = df['close'].astype(float, errors = 'raise').tail() - indicator_data.tail()
                                        if price_indicator_diff.iloc[-1] >= 0 - (indicator_data.iloc[-1] * (tp_dynamic_tolerance_ratio/100)) and price_indicator_diff.iloc[-2] < 0:
                                            break_direction = 'up'
                                        elif price_indicator_diff.iloc[-1] <= 0 + (indicator_data.iloc[-1] * (tp_dynamic_tolerance_ratio/100)) and price_indicator_diff.iloc[-2] > 0:
                                            break_direction = 'down'
                                elif indicator == 'bbands':
                                    indicator_data = ta.bbands(df['close'].astype(float, errors = 'raise'), length=length).filter(like='BBM') # Use Median of the Bollinger Band
                                    if ordertype == 'Limit':
                                        if side == 'Buy' and 0 < (indicator_data.iloc[-1][0] - (indicator_data.iloc[-1][0] * (tp_dynamic_tolerance_ratio/100))) - entry_price < (entry_price * tp_dynamic_maximum_ratio/100):
                                            limit_close_price_levels.append(indicator_data.iloc[-1][0] - (indicator_data.iloc[-1][0] * (tp_dynamic_tolerance_ratio/100)))
                                        elif side == 'Sell' and 0 > (indicator_data.iloc[-1][0] + (indicator_data.iloc[-1][0] * (tp_dynamic_tolerance_ratio/100))) - entry_price > -1 * (entry_price * tp_dynamic_maximum_ratio/100):
                                            limit_close_price_levels.append(indicator_data.iloc[-1][0] + (indicator_data.iloc[-1][0] * (tp_dynamic_tolerance_ratio/100)))  
                                    elif ordertype == 'Market':
                                        market_close_price_levels.append(indicator_data.iloc[-1][0]) # Indicator Price Point to Take Profit at as Market Close Order
                                        if (df['close'].astype(float, errors = 'raise').iloc[-1] - indicator_data.iloc[-1][0]) >= 0 - (indicator_data.iloc[-1][0] * (tp_dynamic_tolerance_ratio/100)) and ((df['close'].astype(float, errors = 'raise').iloc[-2] - indicator_data.iloc[-2][0])) < 0:
                                            break_direction = 'up'
                                        elif (df['close'].astype(float, errors = 'raise').iloc[-1] - indicator_data.iloc[-1][0]) <= 0 + (indicator_data.iloc[-1][0] * (tp_dynamic_tolerance_ratio/100)) and ((df['close'].astype(float, errors = 'raise').iloc[-2] - indicator_data.iloc[-2][0])) > 0:
                                            break_direction = 'down'
                                            
                                    indicator_data = ta.bbands(df['close'].astype(float, errors = 'raise'), length=length).filter(like='BBL') # Use Low of the Bollinger Band for Shorts taking profit
                                    if ordertype == 'Limit':
                                        if side == 'Sell' and 0 > (indicator_data.iloc[-1][0] + (indicator_data.iloc[-1][0] * (tp_dynamic_tolerance_ratio/100))) - entry_price > -1 * (entry_price * tp_dynamic_maximum_ratio/100):
                                            limit_close_price_levels.append(indicator_data.iloc[-1][0] + (indicator_data.iloc[-1][0] * (tp_dynamic_tolerance_ratio/100)))  
                                        '''
                                            elif side == 'Buy' and 0 < (indicator_data.iloc[-1][0] - (indicator_data.iloc[-1][0] * (tp_dynamic_tolerance_ratio/100))) - entry_price < (entry_price * tp_dynamic_maximum_ratio/100):
                                            limit_close_price_levels.append(indicator_data.iloc[-1][0] - (indicator_data.iloc[-1][0] * (tp_dynamic_tolerance_ratio/100)))
                                        '''
                                    elif ordertype == 'Market':
                                        market_close_price_levels.append(indicator_data.iloc[-1][0]) # Indicator Price Point to Take Profit at as Market Close Order
                                        if (df['close'].astype(float, errors = 'raise').iloc[-1] - indicator_data.iloc[-1][0]) >= 0 - (indicator_data.iloc[-1][0] * (tp_dynamic_tolerance_ratio/100)) and ((df['close'].astype(float, errors = 'raise').iloc[-2] - indicator_data.iloc[-2][0])) < 0:
                                            break_direction = 'up'
                                        elif (df['close'].astype(float, errors = 'raise').iloc[-1] - indicator_data.iloc[-1][0]) <= 0 + (indicator_data.iloc[-1][0] * (tp_dynamic_tolerance_ratio/100)) and ((df['close'].astype(float, errors = 'raise').iloc[-2] - indicator_data.iloc[-2][0])) > 0:
                                            break_direction = 'down'
                                            
                                    indicator_data = ta.bbands(df['close'].astype(float, errors = 'raise'), length=length).filter(like='BBU') # Use High of the Bollinger Band for Longs taking profit
                                    if ordertype == 'Limit':
                                        if side == 'Buy' and 0 < (indicator_data.iloc[-1][0] - (indicator_data.iloc[-1][0] * (tp_dynamic_tolerance_ratio/100))) - entry_price < (entry_price * tp_dynamic_maximum_ratio/100):
                                            limit_close_price_levels.append(indicator_data.iloc[-1][0] - (indicator_data.iloc[-1][0] * (tp_dynamic_tolerance_ratio/100)))
                                        '''
                                            elif side == 'Sell' and 0 > (indicator_data.iloc[-1][0] + (indicator_data.iloc[-1][0] * (tp_dynamic_tolerance_ratio/100))) - entry_price > -1 * (entry_price * tp_dynamic_maximum_ratio/100):
                                            limit_close_price_levels.append(indicator_data.iloc[-1][0] + (indicator_data.iloc[-1][0] * (tp_dynamic_tolerance_ratio/100)))  
                                        '''
                                    elif ordertype == 'Market':
                                        market_close_price_levels.append(indicator_data.iloc[-1][0]) # Indicator Price Point to Take Profit at as Market Close Order
                                        if (df['close'].astype(float, errors = 'raise').iloc[-1] - indicator_data.iloc[-1][0]) >= 0 - (indicator_data.iloc[-1][0] * (tp_dynamic_tolerance_ratio/100)) and ((df['close'].astype(float, errors = 'raise').iloc[-2] - indicator_data.iloc[-2][0])) < 0:
                                            break_direction = 'up'
                                        elif (df['close'].astype(float, errors = 'raise').iloc[-1] - indicator_data.iloc[-1][0]) <= 0 + (indicator_data.iloc[-1][0] * (tp_dynamic_tolerance_ratio/100)) and ((df['close'].astype(float, errors = 'raise').iloc[-2] - indicator_data.iloc[-2][0])) > 0:
                                            break_direction = 'down'
                                            
                        if len(limit_close_price_levels) == 0: # No Dynamic Levels found, add any default ratios if defined
                            if side == 'Buy':
                                limit_close_price_levels.append(entry_price + (entry_price * tp_dynamic_maximum_ratio/100))
                            elif side == 'Sell':
                                limit_close_price_levels.append(entry_price - (entry_price * tp_dynamic_maximum_ratio/100))
                        
                        if len(limit_close_price_levels) > 0: # Now we place Limit Close orders if any needed, and make sure quantity is updated to the Full Position Size
                            if side == 'Buy':
                                limit_close_price_levels = np.sort(limit_close_price_levels) # First we sort the Limit Close Targets Ascending to have the nearest (lowest) value at the first index, as the assumption is when you are Longing the indicator is above current price
                                for limit_close_price_level in limit_close_price_levels: # Loop through them to find the nearest, but also valid (profitable)
                                    if limit_close_price_level - entry_price > 0 and limit_close_price_level > last_price: # Only if the dynamic Limit Close is in Profit for the Entry Price of Position AND is above Current Price
                                        # First go through all Active Orders searching for Close Orders only:
                                        limit_close_order_ids = []
                                        try:
                                            fetched_active_orders = session.query_active_order(symbol=symbol)
                                        except Exception:
                                            pass
                                        if(fetched_active_orders):
                                            for active_order in fetched_active_orders["result"]:
                                                if symbol.endswith('USDT'): # USDT Perpetual
                                                    # Note: order side should be opposite of position side
                                                    if active_order['side'] == "Sell" and active_order['order_type'] == 'Limit' and active_order['reduce_only'] == True and active_order['close_on_trigger'] == True: # Active Limit Close Order for Long
                                                        # Count the Active Orders and record Order ID
                                                        limit_close_order_ids.append(active_order['order_id'])
                                                else: # Inverse Perpetuals or Futures
                                                    # Note: order side should be opposite of position side
                                                    if active_order['side'] == "Sell" and active_order['order_type'] == 'Limit': # Active Limit Close Order for Long
                                                        # Count the Active Orders and record Order ID
                                                        limit_close_order_ids.append(active_order['order_id'])        
                                                        
                                        if len(limit_close_order_ids) == 0:
                                            # Create the Limit Close Order
                                            try:
                                                session.place_active_order(position_idx=position_idx, symbol=symbol, side="Sell", order_type="Limit", qty=size, price=round(limit_close_price_level, final_decimals_count), time_in_force="PostOnly", reduce_only=True, close_on_trigger=True)
                                                log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " LONG Dynamic Take Profit Limit Close placed at: "+str(round(limit_close_price_level, final_decimals_count))+"."
                                                print(log)
                                                with open("TP.txt", "a") as myfile:
                                                    myfile.write(log+'\n')
                                            except Exception:
                                                pass
                                                
                                        elif len(limit_close_order_ids) == 1:
                                            # Update the existing Limit Close Order
                                            try:
                                                session.replace_active_order(position_idx=position_idx, symbol=symbol, order_id=limit_close_order_ids[0], p_r_qty=size , p_r_price=round(limit_close_price_level, final_decimals_count), time_in_force="PostOnly", reduce_only=True, close_on_trigger=True)
                                                log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " LONG Dynamic Take Profit Limit Close placed at: "+str(round(limit_close_price_level, final_decimals_count))+"."
                                                print(log)
                                                with open("TP.txt", "a") as myfile:
                                                    myfile.write(log+'\n')
                                            except Exception:
                                                pass
                                            
                                            
                                        elif len(limit_close_order_ids) > 1:
                                            # Cancel all Limit Close Orders
                                            for limit_close_order_id in limit_close_order_ids:
                                                try:
                                                    session.cancel_active_order(symbol=symbol, order_id=limit_close_order_id)
                                                except Exception:
                                                    pass
                                            # Create the Limit Close Order
                                            try:
                                                session.place_active_order(position_idx=position_idx, symbol=symbol, side="Sell", order_type="Limit", qty=size, price=round(limit_close_price_level, final_decimals_count), time_in_force="PostOnly", reduce_only=True, close_on_trigger=True)
                                                log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " LONG Dynamic Take Profit Limit Close placed at: "+str(round(limit_close_price_level, final_decimals_count))+"."
                                                print(log)
                                                with open("TP.txt", "a") as myfile:
                                                    myfile.write(log+'\n')
                                            except Exception:
                                                pass
                                        break
                        
                            elif side == 'Sell':
                                limit_close_price_levels = np.sort(limit_close_price_levels)[::-1] # First we sort the Limit Close Targets Descending to have the nearest (highest) value at the first index, as the assumption is when you are Shorting the indicator is below current price
                                for limit_close_price_level in limit_close_price_levels: # Loop through them to find the nearest, but also valid (profitable)
                                    if limit_close_price_level - entry_price < 0 and limit_close_price_level < last_price: # Only if the dynamic Limit Close is in Profit for the Entry Price of Position AND is above Current Price
                                        # First go through all Active Orders searching for Close Orders only:
                                        limit_close_order_ids = []
                                        try:
                                            fetched_active_orders = session.query_active_order(symbol=symbol)
                                        except Exception:
                                            pass
                                        if(fetched_active_orders):
                                            for active_order in fetched_active_orders["result"]:
                                                if symbol.endswith('USDT'): # USDT Perpetual
                                                    # Note: order side should be opposite of position side
                                                    if active_order['side'] == "Buy" and active_order['order_type'] == 'Limit' and active_order['reduce_only'] == True and active_order['close_on_trigger'] == True: # Active Limit Close Order for Short
                                                        # Count the Active Orders and record Order ID
                                                        limit_close_order_ids.append(active_order['order_id'])
                                                else: # Inverse Perpetuals or Futures
                                                    # Note: order side should be opposite of position side
                                                    if active_order['side'] == "Buy" and active_order['order_type'] == 'Limit': # Active Limit Close Order for Short
                                                        # Count the Active Orders and record Order ID
                                                        limit_close_order_ids.append(active_order['order_id'])        
                                                     
                                        if len(limit_close_order_ids) == 0:
                                            # Create the Limit Close Order
                                            try:
                                                session.place_active_order(position_idx=position_idx, symbol=symbol, side="Buy", order_type="Limit", qty=size, price=round(limit_close_price_level, final_decimals_count), time_in_force="PostOnly", reduce_only=True, close_on_trigger=True)
                                                log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " SHORT Dynamic Take Profit Limit Close placed at: "+str(round(limit_close_price_level, final_decimals_count))+"."
                                                print(log)
                                                with open("TP.txt", "a") as myfile:
                                                    myfile.write(log+'\n')
                                            except Exception:
                                                pass
                                                
                                        elif len(limit_close_order_ids) == 1:
                                            # Update the existing Limit Close Order
                                            try:
                                                session.replace_active_order(position_idx=position_idx, symbol=symbol, order_id=limit_close_order_ids[0], p_r_qty=size , p_r_price=round(limit_close_price_level, final_decimals_count), time_in_force="PostOnly", reduce_only=True, close_on_trigger=True)
                                                log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " SHORT Dynamic Take Profit Limit Close placed at: "+str(round(limit_close_price_level, final_decimals_count))+"."
                                                print(log)
                                                with open("TP.txt", "a") as myfile:
                                                    myfile.write(log+'\n')
                                            except Exception:
                                                pass
                                            
                                            
                                        elif len(limit_close_order_ids) > 1:
                                            # Cancel all Limit Close Orders
                                            for limit_close_order_id in limit_close_order_ids:
                                                try:
                                                    session.cancel_active_order(symbol=symbol, order_id=limit_close_order_id)
                                                except Exception:
                                                    pass
                                            # Create the Limit Close Order
                                            try:
                                                session.place_active_order(position_idx=position_idx, symbol=symbol, side="Buy", order_type="Limit", qty=size, price=round(limit_close_price_level, final_decimals_count), time_in_force="PostOnly", reduce_only=True, close_on_trigger=True)
                                                log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " SHORT Dynamic Take Profit Limit Close placed at: "+str(round(limit_close_price_level, final_decimals_count))+"."
                                                print(log)
                                                with open("TP.txt", "a") as myfile:
                                                    myfile.write(log+'\n')
                                            except Exception:
                                                pass
                                                
                                        break
                        
                        # Execute any Market close if any indicator is touched/broken
                        if side == 'Buy' and break_direction == 'up' and (last_price -  entry_price > 0): # profitable LONG position with price breaking a dynamic level up
                            try:
                                session.place_active_order(position_idx=position_idx, symbol=symbol, side="Sell", order_type="Market", qty=size, time_in_force="GoodTillCancel", reduce_only=True, close_on_trigger=True)
                                log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " LONG Dynamic Take Profit closing position at: "+str(last_price)+"."
                                print(log)
                                with open("TP.txt", "a") as myfile:
                                    myfile.write(log+'\n')
                            except Exception:
                                pass
                        elif side == 'Sell' and break_direction == 'down' and (last_price -  entry_price < 0): # profitable SHORT position with price breaking a dynamic level down
                            try:
                                session.place_active_order(position_idx=position_idx, symbol=symbol, side="Buy", order_type="Market", qty=size, time_in_force="GoodTillCancel", reduce_only=True, close_on_trigger=True)
                                log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " SHORT Dynamic Take Profit closing position at: "+str(last_price)+"."
                                print(log)
                                with open("TP.txt", "a") as myfile:
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
                            lock_in_p_price_ratio = float(elem[0])
                            lock_in_p_sl_ratio = float(elem[1])
                            
                            position_leveraged_p_level = round_to_tick(entry_price + (((lock_in_p_price_ratio/100) / leverage) * entry_price), tick_size[symbol])
                            position_leveraged_p_sl_level = round_to_tick(entry_price + (((lock_in_p_sl_ratio/100) / leverage) * entry_price), tick_size[symbol])
                            if last_price >= position_leveraged_p_level:

                                # Sarch Conditional Orders if Stop Loss already exists with 'qty'=position size AND 'trigger_price' better than the Take Profit Level
                                total_in_profit_stop_loss_found = 0.0
                                
                                if(fetched_conditional_orders):
                                    for conditional_order in fetched_conditional_orders["result"]:
                                        # Note: order side should be opposite of position side
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
                                    set_trading_stop_args = {'position_idx': position_idx, 'symbol': symbol, 'side': side}
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
                            lock_in_p_price_ratio = float(elem[0])
                            lock_in_p_sl_ratio = float(elem[1])
                            
                            position_leveraged_p_level = round_to_tick(entry_price - (((lock_in_p_price_ratio/100) / leverage) * entry_price), tick_size[symbol])
                            position_leveraged_p_sl_level = round_to_tick(entry_price - (((lock_in_p_sl_ratio/100) / leverage) * entry_price), tick_size[symbol])
                            if last_price <= position_leveraged_p_level:
                
                                # Sarch Conditional Orders if Stop Loss already exists with 'qty'=position size AND 'trigger_price' better than the Take Profit Level
                                total_in_profit_stop_loss_found = 0.0
                                
                                if(fetched_conditional_orders):
                                    for conditional_order in fetched_conditional_orders["result"]:
                                        # Note: order side should be opposite of position side
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
                                    set_trading_stop_args = {'position_idx': position_idx, 'symbol': symbol, 'side': side}
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
                                            
            
            #######################################################
            # Enforce Database Exit Strategies
            #######################################################
            
            if enforce_db_exit_strategies == True and enable_db_features == True:
                mycursor = mydb.cursor(dictionary=True)
                mycursor.execute("SELECT * FROM exit_strategies WHERE api_key='"+api_key+"' AND api_secret='"+api_secret+"' AND symbol='"+symbol+"'")
                myresult = mycursor.fetchall()
                for exit_strategy in myresult:
                    # Find the Exit Strategy for the position's symbol and implement
                    #######################################################
                    # Exit Strategies
                    #######################################################
                    exit_strategy_tps_long = {}
                    if exit_strategy['tp_target_long'] and exit_strategy['tp_target_long'] != '0' and exit_strategy['tp_target_long'] is not None and exit_strategy['tp_target_long'] != "":
                        exit_strategy_tps_long = ''.join(exit_strategy['tp_target_long'].split()).rstrip(';')
                        exit_strategy_tps_long = dict(x.split(":") for x in exit_strategy_tps_long.split(";"))
                        
                    exit_strategy_tps_short = {}
                    if exit_strategy['tp_target_short'] and exit_strategy['tp_target_short'] != '0' and exit_strategy['tp_target_short'] is not None and exit_strategy['tp_target_short'] != "":
                        exit_strategy_tps_short = ''.join(exit_strategy['tp_target_short'].split()).rstrip(';')
                        exit_strategy_tps_short = dict(x.split(":") for x in exit_strategy_tps_short.split(";"))
                        
                    exit_strategy_sls_long = {}
                    if exit_strategy['sl_target_long'] > 0 and exit_strategy['sl_amount'] > 0:
                        exit_strategy_sls_long = {
                          exit_strategy['sl_target_long']: exit_strategy['sl_amount']
                        }
                        
                    exit_strategy_sls_short = {}
                    if exit_strategy['sl_target_short'] > 0 and exit_strategy['sl_amount'] > 0:
                        exit_strategy_sls_short = {
                          exit_strategy['sl_target_short']: exit_strategy['sl_amount']
                        }
                    
                    exit_strategy_trailing_sls_long = {}
                    if exit_strategy['sl_trailing_targets_long'] and exit_strategy['sl_trailing_targets_long'] != '0' and exit_strategy['sl_trailing_targets_long'] is not None and exit_strategy['sl_trailing_targets_long'] != "":
                        exit_strategy_trailing_sls_long = ''.join(exit_strategy['sl_trailing_targets_long'].split()).rstrip(';')
                        exit_strategy_trailing_sls_long = dict(x.split(":") for x in exit_strategy_trailing_sls_long.split(";"))
                    
                    exit_strategy_trailing_sls_short = {}
                    if exit_strategy['sl_trailing_targets_short'] and exit_strategy['sl_trailing_targets_short'] != '0' and exit_strategy['sl_trailing_targets_short'] is not None and exit_strategy['sl_trailing_targets_short'] != "":
                        exit_strategy_trailing_sls_short = ''.join(exit_strategy['sl_trailing_targets_short'].split()).rstrip(';')
                        exit_strategy_trailing_sls_short = dict(x.split(":") for x in exit_strategy_trailing_sls_short.split(";"))
                    
                    
                    allow_tps = True # Flag used to allow TPs
                    allow_sls = True # Flag used to allow SLs
                    
                    # Check if the position was Hedged before and the TPs/SLs are not allowed after Hedging
                    myresult_position_session_general = mydb.cursor(dictionary=True)
                    myresult_position_session_general.execute("SELECT * FROM positions_sessions WHERE api_key='"+api_key+"' AND api_secret='"+api_secret+"' AND symbol='"+symbol+"'")
                    myresult_position_session = myresult_position_session_general.fetchall()
                    for this_position_session in myresult_position_session:
                        if this_position_session['hedged'] == 1 and exit_strategy['tp_after_hedge'] == 0:
                            allow_tps = False
                        if this_position_session['hedged'] == 1 and exit_strategy['sl_after_hedge'] == 0:
                            allow_sls = False
                    
                    ''' Setup the Take Profits '''
                    if allow_tps and (len(exit_strategy_tps_long) > 0 or len(exit_strategy_tps_short) > 0):
                        if exit_strategy['tp_target_type'] == 'ratio_post_leverage':
                            leverage_for_tp_calc = leverage
                        elif exit_strategy['tp_target_type'] == 'ratio_pre_leverage':
                            leverage_for_tp_calc = 1
                        
                        
                        ################################################################# 
                        #################################################################
                        ## TODO: CHECK IF FORCE MARKET EXIT is needed for TP 
                        #################################################################
                        ################################################################# 
                        #################################################################
                        
                        if exit_strategy['tp_type'] == 'marketorder':
                        
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
                                                            for elem in exit_strategy_tps_long.items():
                                                                tp_price_ratio = float(elem[0])
                                                                tp_size_ratio = float(elem[1])
                                                                tp_price = round_to_tick(entry_price + (((tp_price_ratio/100) / leverage_for_tp_calc) * entry_price), tick_size[symbol])
                                                                tp_size = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])
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
                                                            for elem in exit_strategy_tps_long.items():
                                                                tp_price_ratio = float(elem[0])
                                                                tp_size_ratio = float(elem[1])
                                                                tp_price = round_to_tick(entry_price + (((tp_price_ratio/100) / leverage_for_tp_calc) * entry_price), tick_size[symbol])
                                                                tp_size = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])
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
                                            set_trading_stop_args = {'position_idx': position_idx, 'symbol': symbol, 'side': side}
                                            
                                            for elem in sorted(exit_strategy_tps_long.items(), reverse=False): # Sort Ascending to find the nearest TP level
                                                tp_price_ratio = float(elem[0])
                                                tp_size_ratio = float(elem[1])
                                                
                                                set_trading_stop_args['take_profit'] = round_to_tick(entry_price + (((tp_price_ratio/100) / leverage_for_tp_calc) * entry_price), tick_size[symbol])
                                                set_trading_stop_args['tp_size'] = tp_size = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])
                                                
                                                if last_price < set_trading_stop_args['take_profit'] - (exit_strategy['tp_target_tolerance_ratio']/100) * (set_trading_stop_args['take_profit'] - entry_price):
                                                    try:
                                                        session.set_trading_stop(**set_trading_stop_args)
                                                        log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " LONG Take-Profit Market placed: "+str(tp_size_ratio)+"% of Quantity ("+str(set_trading_stop_args['tp_size'])+") @ "+ str(tp_price_ratio) +"% in Profit ("+str(set_trading_stop_args['take_profit'])+")."
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
                                                            for elem in exit_strategy_tps_short.items():
                                                                tp_price_ratio = float(elem[0])
                                                                tp_size_ratio = float(elem[1])
                                                                tp_price = round_to_tick(entry_price - (((tp_price_ratio/100) / leverage_for_tp_calc) * entry_price), tick_size[symbol])
                                                                tp_size = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])
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
                                                            for elem in exit_strategy_tps_short.items():
                                                                tp_price_ratio = float(elem[0])
                                                                tp_size_ratio = float(elem[1])
                                                                tp_price = round_to_tick(entry_price - (((tp_price_ratio/100) / leverage_for_tp_calc) * entry_price), tick_size[symbol])
                                                                tp_size = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])
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
                                            set_trading_stop_args = {'position_idx': position_idx, 'symbol': symbol, 'side': side}
                                            
                                            for elem in sorted(exit_strategy_tps_short.items(), reverse=False): # Sort Ascending to find the nearest TP level
                                                tp_price_ratio = float(elem[0])
                                                tp_size_ratio = float(elem[1])
                                                
                                                set_trading_stop_args['take_profit'] = round_to_tick(entry_price - (((tp_price_ratio/100) / leverage_for_tp_calc) * entry_price), tick_size[symbol])
                                                set_trading_stop_args['tp_size'] = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])

                                                if last_price > set_trading_stop_args['take_profit'] + (exit_strategy['tp_target_tolerance_ratio']/100) * (entry_price - set_trading_stop_args['take_profit']):
                                                    try:
                                                        session.set_trading_stop(**set_trading_stop_args)
                                                        log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " SHORT Take-Profit Market placed: "+str(tp_size_ratio)+"% of Quantity ("+str(set_trading_stop_args['tp_size'])+") @ "+ str(tp_price_ratio) +"% in Profit ("+str(set_trading_stop_args['take_profit'])+")."
                                                        print(log)
                                                        with open("TP.txt", "a") as myfile:
                                                            myfile.write(log+'\n')
                                                        break # No need to add more TPs, we only place 1 TP at a time
                                                    except Exception:
                                                        pass  
                                                        
                        elif exit_strategy['tp_type'] == 'limitorder' or exit_strategy['tp_type'] == 'limitorder_postonly':
                            if exit_strategy['tp_type'] == 'limitorder_postonly':
                                order_timeInForce = 'PostOnly'
                            elif exit_strategy['tp_type'] == 'limitorder':
                                order_timeInForce = 'GoodTillCancel'
                            
                            # Fetch latest tickers
                            try:
                                fetched_latest_tickers = session.latest_information_for_symbol(symbol=symbol)['result']
                            except Exception:
                                pass
                            if(fetched_latest_tickers):
                                for ticker in fetched_latest_tickers:
                                    if ticker['symbol'] == symbol:
                                        last_price = float(ticker['last_price'])    
                                        bid_price = float(ticker['bid_price'])  
                                        ask_price = float(ticker['ask_price'])  
                                       
                                    
                                    if exit_strategy['tp_all_or_none'] == 1:
                                        # Check and Add all TPs at once
                                        total_tp_found = 0.0
                                        tp_outside_maxrange_price = 0.0
                                        tp_outside_maxrange_found = False
                                        active_tps_order_id = []
                                        if side == 'Buy':
                                            # Search Active Orders if Take Profits already exist
                                            try:
                                                fetched_active_orders = session.query_active_order(symbol=symbol)
                                            except Exception:
                                                pass
                                            if(fetched_active_orders):
                                                # Fetch most recent position data to avoid discrepancies
                                                fetched_positions_recent = []
                                                if symbol.endswith('USDT'): # USDT Perpetual
                                                    try:
                                                        fetched_positions_recent = session.my_position(endpoint="/private/linear/position/list", symbol=symbol)['result'] # USDT Perpetual
                                                    except Exception:
                                                        pass
                                                    if(fetched_positions_recent):
                                                        for updated_position in fetched_positions_recent:
                                                            if updated_position['side'] == side and updated_position['size'] > 0: # We only want the specific side and active position (size>0)
                                                                size = float(updated_position["size"])
                                                                position_value = float(updated_position["position_value"])
                                                                leverage = float(updated_position["leverage"])
                                                                stop_loss = float(updated_position["stop_loss"])
                                                                entry_price = float(updated_position["entry_price"])
                                                elif symbol.endswith('USD'): # Inverse Perpetuals
                                                    try:
                                                        fetched_positions_recent = session.my_position(endpoint="/v2/private/position/list", symbol=symbol)['result'] # Inverse Perpetual
                                                    except Exception:
                                                        pass
                                                    if(fetched_positions_recent):
                                                        for updated_position in fetched_positions_recent:
                                                            if updated_position['side'] == side and updated_position['size'] > 0: # We only want the specific side and active position (size>0)
                                                                size = float(updated_position["size"])
                                                                position_value = float(updated_position["position_value"])
                                                                leverage = float(updated_position["leverage"])
                                                                stop_loss = float(updated_position["stop_loss"])
                                                                entry_price = float(updated_position["entry_price"])
                                                else: # Inverse Futures     
                                                    try:
                                                        fetched_positions_recent = session.my_position(endpoint="/futures/private/position/list", symbol=symbol)['result'] # Inverse Futures
                                                    except Exception:
                                                        pass
                                                    if(fetched_positions_recent):
                                                        for updated_position in fetched_positions_recent:
                                                            if updated_position['side'] == side and updated_position['size'] > 0: # We only want the specific side and active position (size>0)
                                                                size = float(updated_position["size"])
                                                                position_value = float(updated_position["position_value"])
                                                                leverage = float(updated_position["leverage"])
                                                                stop_loss = float(updated_position["stop_loss"])
                                                                entry_price = float(updated_position["entry_price"])
                                                
                                                for elem in sorted(exit_strategy_tps_long.items(), reverse=True): # Sort Descending to find the furthest TP level
                                                    tp_price_ratio_maxrange = float(elem[0])
                                                    tp_outside_maxrange_price = round_to_tick(entry_price + (((tp_price_ratio_maxrange/100) / leverage_for_tp_calc) * entry_price), tick_size[symbol])
                                                    #print('Max Range TP Price = ' + str(tp_outside_maxrange_price))
                                                    break
                                                    
                                                # Now we calculate total TPs
                                                for active_order in fetched_active_orders["result"]:
                                                    if symbol.endswith('USDT'): # USDT Perpetual
                                                        limit_price = float(active_order['price'])
                                                        # if active_order['side'] == 'Sell' and limit_price > last_price and limit_price > entry_price and active_order['reduce_only'] == True:
                                                        if active_order['side'] == 'Sell' and active_order['reduce_only'] == True:
                                                            # Take Profit found, add it to the total
                                                            total_tp_found += float(active_order['qty'])
                                                            active_tps_order_id.append(active_order['order_id'])
                                                            if limit_price > tp_outside_maxrange_price:
                                                                tp_outside_maxrange_found = True
                                                    else: # Inverse Perpetuals or Futures
                                                        limit_price = float(active_order['price'])
                                                        if active_order['side'] == 'Sell' and limit_price > last_price and limit_price > entry_price:
                                                            # Take Profit found, no need to do anything
                                                            total_tp_found += float(active_order['qty'])
                                                            active_tps_order_id.append(active_order['order_id'])
                                                            if limit_price > tp_outside_maxrange_price:
                                                                tp_outside_maxrange_found = True
                                            total_tp_found = round_step_size(total_tp_found,qty_step[symbol],min_trading_qty[symbol])
                                            if (exit_strategy['tp_enforce_all_time'] == 0 and total_tp_found == 0.0) or (exit_strategy['tp_enforce_all_time'] == 1 and total_tp_found < size) or (exit_strategy['tp_enforce_maxrange'] == 1 and tp_outside_maxrange_found == True):
                                                # No TPs found or not fully covering position size, so add ALL of them at once
                                                # First remove any active orders to clear all
                                                for active_tp_order_id in active_tps_order_id:
                                                    # Remove active order
                                                    try:
                                                        session.cancel_active_order(symbol=symbol, order_id=active_tp_order_id)
                                                    except Exception:
                                                        pass
                                                    
                                                # Prepare set_trading_stop arguments to pass to API
                                                limit_tp_args = {'position_idx': position_idx, 'symbol': symbol, 'side': 'Sell', 'order_type': "Limit", 'time_in_force': order_timeInForce, 'reduce_only': True, 'close_on_trigger': True }
                                                
                                                for elem in sorted(exit_strategy_tps_long.items(), reverse=False): # Sort Ascending to find the nearest TP level
                                                    tp_price_ratio = float(elem[0])
                                                    tp_size_ratio = float(elem[1])
                                                    
                                                    limit_tp_args['price'] = round_to_tick(entry_price + (((tp_price_ratio/100) / leverage_for_tp_calc) * entry_price), tick_size[symbol])
                                                    limit_tp_args['qty'] = tp_size = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])
                                                    
                                                    added_spread = 0.0
                                                    if ask_price >= limit_tp_args['price'] - (exit_strategy['tp_target_tolerance_ratio']/100) * (limit_tp_args['price'] - entry_price):
                                                        added_spread = ask_price - limit_tp_args['price']
                                                        limit_tp_args['price'] = limit_tp_args['price'] + added_spread

                                                    try:
                                                        session.place_active_order(**limit_tp_args)
                                                        log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " LONG Take-Profit Limit placed: "+str(tp_size_ratio)+"% of Quantity ("+str(limit_tp_args['qty'])+") @ "+ str(tp_price_ratio) +"% in Profit ("+str(limit_tp_args['price'])+")."
                                                        print(log)
                                                        with open("TP.txt", "a") as myfile:
                                                            myfile.write(log+'\n')
                                                    except Exception as e:
                                                        print(e)
                                                        pass     
                                                            
                                        elif side == 'Sell':   
                                            # Search Active Orders if Take Profits already exist
                                            try:
                                                fetched_active_orders = session.query_active_order(symbol=symbol)
                                            except Exception:
                                                pass
                                            if(fetched_active_orders):
                                                # Fetch most recent position data to avoid discrepancies
                                                fetched_positions_recent = []
                                                if symbol.endswith('USDT'): # USDT Perpetual
                                                    try:
                                                        fetched_positions_recent = session.my_position(endpoint="/private/linear/position/list", symbol=symbol)['result'] # USDT Perpetual
                                                    except Exception:
                                                        pass
                                                    if(fetched_positions_recent):
                                                        for updated_position in fetched_positions_recent:
                                                            if updated_position['side'] == side and updated_position['size'] > 0: # We only want the specific side and active position (size>0)
                                                                size = float(updated_position["size"])
                                                                position_value = float(updated_position["position_value"])
                                                                leverage = float(updated_position["leverage"])
                                                                stop_loss = float(updated_position["stop_loss"])
                                                                entry_price = float(updated_position["entry_price"])
                                                elif symbol.endswith('USD'): # Inverse Perpetuals
                                                    try:
                                                        fetched_positions_recent = session.my_position(endpoint="/v2/private/position/list", symbol=symbol)['result'] # Inverse Perpetual
                                                    except Exception:
                                                        pass
                                                    if(fetched_positions_recent):
                                                        for updated_position in fetched_positions_recent:
                                                            if updated_position['side'] == side and updated_position['size'] > 0: # We only want the specific side and active position (size>0)
                                                                size = float(updated_position["size"])
                                                                position_value = float(updated_position["position_value"])
                                                                leverage = float(updated_position["leverage"])
                                                                stop_loss = float(updated_position["stop_loss"])
                                                                entry_price = float(updated_position["entry_price"])
                                                else: # Inverse Futures     
                                                    try:
                                                        fetched_positions_recent = session.my_position(endpoint="/futures/private/position/list", symbol=symbol)['result'] # Inverse Futures
                                                    except Exception:
                                                        pass
                                                    if(fetched_positions_recent):
                                                        for updated_position in fetched_positions_recent:
                                                            if updated_position['side'] == side and updated_position['size'] > 0: # We only want the specific side and active position (size>0)
                                                                size = float(updated_position["size"])
                                                                position_value = float(updated_position["position_value"])
                                                                leverage = float(updated_position["leverage"])
                                                                stop_loss = float(updated_position["stop_loss"])
                                                                entry_price = float(updated_position["entry_price"])
                                                                
                                                for elem in sorted(exit_strategy_tps_short.items(), reverse=True): # Sort Descending to find the furthest TP level
                                                    tp_price_ratio_maxrange = float(elem[0])
                                                    tp_outside_maxrange_price = round_to_tick(entry_price - (((tp_price_ratio_maxrange/100) / leverage_for_tp_calc) * entry_price), tick_size[symbol])
                                                    #print('Max Range TP Price = ' + str(tp_outside_maxrange_price))
                                                    break
                                                                
                                                # Now we calculate total TPs
                                                for active_order in fetched_active_orders["result"]:
                                                    if symbol.endswith('USDT'): # USDT Perpetual
                                                        limit_price = float(active_order['price'])

                                                        # if active_order['side'] == 'Buy' and limit_price < last_price and limit_price < entry_price and active_order['reduce_only'] == True:
                                                        if active_order['side'] == 'Buy' and active_order['reduce_only'] == True:
                                                            # Take Profit found, no need to do anything
                                                            total_tp_found += float(active_order['qty'])
                                                            active_tps_order_id.append(active_order['order_id'])
                                                            if limit_price < tp_outside_maxrange_price:
                                                                tp_outside_maxrange_found = True
                                                    else: # Inverse Perpetuals or Futures
                                                        limit_price = float(active_order['price'])
                                                        if active_order['side'] == 'Buy' and limit_price < last_price and limit_price < entry_price:
                                                            # Take Profit found, no need to do anything
                                                            total_tp_found += float(active_order['qty'])
                                                            active_tps_order_id.append(active_order['order_id'])
                                                            if limit_price < tp_outside_maxrange_price:
                                                                tp_outside_maxrange_found = True
                                            total_tp_found = round_step_size(total_tp_found,qty_step[symbol],min_trading_qty[symbol])
                                            if (exit_strategy['tp_enforce_all_time'] == 0 and total_tp_found == 0.0) or (exit_strategy['tp_enforce_all_time'] == 1 and total_tp_found < size) or (exit_strategy['tp_enforce_maxrange'] == 1 and tp_outside_maxrange_found == True):
                                                # No TPs found or not fully covering position size, so add ALL of them at once
                                                # First remove any active orders to clear all
                                                for active_tp_order_id in active_tps_order_id:
                                                    # Remove active order
                                                    try:
                                                        session.cancel_active_order(symbol=symbol, order_id=active_tp_order_id)
                                                    except Exception:
                                                        pass
                                                    
                                                # Prepare set_trading_stop arguments to pass to API
                                                limit_tp_args = {'position_idx': position_idx, 'symbol': symbol, 'side': 'Buy', 'order_type': "Limit", 'time_in_force': order_timeInForce, 'reduce_only': True, 'close_on_trigger': True }
                                                
                                                for elem in sorted(exit_strategy_tps_short.items(), reverse=False): # Sort Ascending to find the nearest TP level
                                                    tp_price_ratio = float(elem[0])
                                                    tp_size_ratio = float(elem[1])
                                                    
                                                    limit_tp_args['price'] = round_to_tick(entry_price - (((tp_price_ratio/100) / leverage_for_tp_calc) * entry_price), tick_size[symbol])
                                                    limit_tp_args['qty'] = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])

                                                    added_spread = 0.0
                                                    if bid_price <= limit_tp_args['price'] - (exit_strategy['tp_target_tolerance_ratio']/100) * (limit_tp_args['price'] - entry_price):
                                                        added_spread = limit_tp_args['price'] - bid_price
                                                        limit_tp_args['price'] = limit_tp_args['price'] - added_spread

                                                    try:
                                                        session.place_active_order(**limit_tp_args)
                                                        log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " SHORT Take-Profit Limit placed: "+str(tp_size_ratio)+"% of Quantity ("+str(limit_tp_args['qty'])+") @ "+ str(tp_price_ratio) +"% in Profit ("+str(limit_tp_args['price'])+")."
                                                        print(log)
                                                        with open("TP.txt", "a") as myfile:
                                                            myfile.write(log+'\n')
                                                    except Exception as e:
                                                        print(e)
                                                        pass
                                        
                                    else:
                                        # Check and Add TPs one by one when levels are hit
                                        if side == 'Buy':
                                            # Sarch Conditional Orders if Take Profits already exist
                                            tp_found = False
                                            
                                            try:
                                                fetched_active_orders = session.query_active_order(symbol=symbol)
                                            except Exception:
                                                pass
                                            if(fetched_active_orders):
                                                # Fetch most recent position data to avoid discrepancies
                                                fetched_positions_recent = []
                                                if symbol.endswith('USDT'): # USDT Perpetual
                                                    try:
                                                        fetched_positions_recent = session.my_position(endpoint="/private/linear/position/list", symbol=symbol)['result'] # USDT Perpetual
                                                    except Exception:
                                                        pass
                                                    if(fetched_positions_recent):
                                                        for updated_position in fetched_positions_recent:
                                                            if updated_position['side'] == side and updated_position['size'] > 0: # We only want the specific side and active position (size>0)
                                                                size = float(updated_position["size"])
                                                                position_value = float(updated_position["position_value"])
                                                                leverage = float(updated_position["leverage"])
                                                                stop_loss = float(updated_position["stop_loss"])
                                                                entry_price = float(updated_position["entry_price"])
                                                elif symbol.endswith('USD'): # Inverse Perpetuals
                                                    try:
                                                        fetched_positions_recent = session.my_position(endpoint="/v2/private/position/list", symbol=symbol)['result'] # Inverse Perpetual
                                                    except Exception:
                                                        pass
                                                    if(fetched_positions_recent):
                                                        for updated_position in fetched_positions_recent:
                                                            if updated_position['side'] == side and updated_position['size'] > 0: # We only want the specific side and active position (size>0)
                                                                size = float(updated_position["size"])
                                                                position_value = float(updated_position["position_value"])
                                                                leverage = float(updated_position["leverage"])
                                                                stop_loss = float(updated_position["stop_loss"])
                                                                entry_price = float(updated_position["entry_price"])
                                                else: # Inverse Futures     
                                                    try:
                                                        fetched_positions_recent = session.my_position(endpoint="/futures/private/position/list", symbol=symbol)['result'] # Inverse Futures
                                                    except Exception:
                                                        pass
                                                    if(fetched_positions_recent):
                                                        for updated_position in fetched_positions_recent:
                                                            if updated_position['side'] == side and updated_position['size'] > 0: # We only want the specific side and active position (size>0)
                                                                size = float(updated_position["size"])
                                                                position_value = float(updated_position["position_value"])
                                                                leverage = float(updated_position["leverage"])
                                                                stop_loss = float(updated_position["stop_loss"])
                                                                entry_price = float(updated_position["entry_price"])

                                            
                                                for active_order in fetched_active_orders["result"]:
                                                    if not tp_found: # If we found a valid TP, no need to iterate any more
                                                        if symbol.endswith('USDT'): # USDT Perpetual
                                                            limit_price = float(active_order['price'])
                                                            order_id = active_order['order_id']

                                                            # if active_order['side'] == 'Sell' and limit_price > last_price and limit_price > entry_price and active_order['reduce_only'] == True:
                                                            if active_order['side'] == 'Sell' and active_order['reduce_only'] == True:
                                                                # Take Profit found, make sure it is one of the pre-defined ones and make sure its quantity is up to date as well
                                                                for elem in exit_strategy_tps_long.items():
                                                                    tp_price_ratio = float(elem[0])
                                                                    tp_size_ratio = float(elem[1])
                                                                    tp_price = round_to_tick(entry_price + (((tp_price_ratio/100) / leverage_for_tp_calc) * entry_price), tick_size[symbol])
                                                                    tp_size = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])
                                                                    limit_size = round_step_size(active_order['qty'], qty_step[symbol],min_trading_qty[symbol])
                                                                    if close_enough_match(tp_price, limit_price, tp_size, limit_size, "Buy"): # tp_price==limit_price and tp_size == limit_size # (tp_size==active_order['qty'] or math.floor(tp_size * 10)/10.0==active_order['qty'] or math.floor(tp_size * 100)/100.0==active_order['qty'] or math.floor(tp_size * 1000)/1000.0==active_order['qty'] or math.floor(tp_size * 10000)/10000.0==active_order['qty']):
                                                                        # We found a valid pre-defined TP, keep it (note we check the floor in case the exchange did remove decimals upon creating the order)
                                                                        tp_found = True
                                                                if not tp_found:
                                                                    # Invalid TP (or updated position size not reflected in the TP), REMOVE IT
                                                                    try:
                                                                        session.cancel_active_order(symbol=symbol, order_id=order_id) 
                                                                    except Exception:
                                                                        pass
                                                        else: # Inverse Perpetuals or Futures
                                                            limit_price = float(active_order['price'])
                                                            order_id = active_order['order_id']
                                                            if active_order['side'] == 'Sell' and limit_price > last_price and limit_price > entry_price:
                                                                # Take Profit found, make sure it is one of the pre-defined ones and make sure its quantity is up to date as well
                                                                for elem in exit_strategy_tps_long.items():
                                                                    tp_price_ratio = float(elem[0])
                                                                    tp_size_ratio = float(elem[1])
                                                                    tp_price = round_to_tick(entry_price + (((tp_price_ratio/100) / leverage_for_tp_calc) * entry_price), tick_size[symbol])
                                                                    tp_size = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])
                                                                    limit_size = round_step_size(active_order['qty'], qty_step[symbol],min_trading_qty[symbol])
                                                                    if close_enough_match(tp_price, limit_price, tp_size, limit_size, "Buy"): # tp_price==limit_price and tp_size == limit_size # (tp_size==active_order['qty'] or math.floor(tp_size * 10)/10.0==active_order['qty'] or math.floor(tp_size * 100)/100.0==active_order['qty'] or math.floor(tp_size * 1000)/1000.0==active_order['qty'] or math.floor(tp_size * 10000)/10000.0==active_order['qty']):
                                                                        # We found a valid pre-defined TP, keep it (note we check the floor in case the exchange did remove decimals upon creating the order)
                                                                        tp_found = True
                                                                if not tp_found:
                                                                    # Invalid TP (or updated position size not reflected in the TP), REMOVE IT
                                                                    try:
                                                                        session.cancel_active_order(symbol=symbol, order_id=order_id) 
                                                                    except Exception:
                                                                        pass
                                   
                                            if not tp_found: # No TPs found, so add (this way we kind of avoid re-adding the same TP if price hit and found resistance at and retested it. so we don't TP the same level twice)
                                                # We couldn't find any TPs, let's add the suitable one
                                                # Prepare set_trading_stop arguments to pass to API
                                                limit_tp_args = {'position_idx': position_idx, 'symbol': symbol, 'side': 'Sell', 'order_type': "Limit", 'time_in_force': order_timeInForce, 'reduce_only': True, 'close_on_trigger': True }
                                                
                                                for elem in sorted(exit_strategy_tps_long.items(), reverse=False): # Sort Ascending to find the nearest TP level
                                                    tp_price_ratio = float(elem[0])
                                                    tp_size_ratio = float(elem[1])
                                                    
                                                    limit_tp_args['price'] = round_to_tick(entry_price + (((tp_price_ratio/100) / leverage_for_tp_calc) * entry_price), tick_size[symbol])
                                                    limit_tp_args['qty'] = tp_size = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])
                                                    
                                                    if last_price < limit_tp_args['price'] - (exit_strategy['tp_target_tolerance_ratio']/100) * (limit_tp_args['price'] - entry_price):
                                                        try:
                                                            session.place_active_order(**limit_tp_args)
                                                            log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " LONG Take-Profit Limit placed: "+str(tp_size_ratio)+"% of Quantity ("+str(limit_tp_args['qty'])+") @ "+ str(tp_price_ratio) +"% in Profit ("+str(limit_tp_args['price'])+")."
                                                            print(log)
                                                            with open("TP.txt", "a") as myfile:
                                                                myfile.write(log+'\n')
                                                            break # No need to add more TPs, we only place 1 TP at a time
                                                        except Exception as e:
                                                            print(e)
                                                            break
                                                            pass                 
                                                
                                        elif side == 'Sell':   
                                            # Sarch Conditional Orders if Take Profits already exist
                                            tp_found = False
                                            
                                            try:
                                                fetched_active_orders = session.query_active_order(symbol=symbol)
                                            except Exception:
                                                pass
                                            if(fetched_active_orders):
                                                # Fetch most recent position data to avoid discrepancies
                                                fetched_positions_recent = []
                                                if symbol.endswith('USDT'): # USDT Perpetual
                                                    try:
                                                        fetched_positions_recent = session.my_position(endpoint="/private/linear/position/list", symbol=symbol)['result'] # USDT Perpetual
                                                    except Exception:
                                                        pass
                                                    if(fetched_positions_recent):
                                                        for updated_position in fetched_positions_recent:
                                                            if updated_position['side'] == side and updated_position['size'] > 0: # We only want the specific side and active position (size>0)
                                                                size = float(updated_position["size"])
                                                                position_value = float(updated_position["position_value"])
                                                                leverage = float(updated_position["leverage"])
                                                                stop_loss = float(updated_position["stop_loss"])
                                                                entry_price = float(updated_position["entry_price"])
                                                elif symbol.endswith('USD'): # Inverse Perpetuals
                                                    try:
                                                        fetched_positions_recent = session.my_position(endpoint="/v2/private/position/list", symbol=symbol)['result'] # Inverse Perpetual
                                                    except Exception:
                                                        pass
                                                    if(fetched_positions_recent):
                                                        for updated_position in fetched_positions_recent:
                                                            if updated_position['side'] == side and updated_position['size'] > 0: # We only want the specific side and active position (size>0)
                                                                size = float(updated_position["size"])
                                                                position_value = float(updated_position["position_value"])
                                                                leverage = float(updated_position["leverage"])
                                                                stop_loss = float(updated_position["stop_loss"])
                                                                entry_price = float(updated_position["entry_price"])
                                                else: # Inverse Futures     
                                                    try:
                                                        fetched_positions_recent = session.my_position(endpoint="/futures/private/position/list", symbol=symbol)['result'] # Inverse Futures
                                                    except Exception:
                                                        pass
                                                    if(fetched_positions_recent):
                                                        for updated_position in fetched_positions_recent:
                                                            if updated_position['side'] == side and updated_position['size'] > 0: # We only want the specific side and active position (size>0)
                                                                size = float(updated_position["size"])
                                                                position_value = float(updated_position["position_value"])
                                                                leverage = float(updated_position["leverage"])
                                                                stop_loss = float(updated_position["stop_loss"])
                                                                entry_price = float(updated_position["entry_price"])
                                                                
                                                for active_order in fetched_active_orders["result"]:
                                                    if not tp_found: # If we found a valid TP, no need to iterate any more
                                                        if symbol.endswith('USDT'): # USDT Perpetual
                                                            limit_price = float(active_order['price'])
                                                            order_id = active_order['order_id']

                                                            # if active_order['side'] == 'Buy' and limit_price < last_price and limit_price < entry_price and active_order['reduce_only'] == True:
                                                            if active_order['side'] == 'Buy' and active_order['reduce_only'] == True:
                                                                # Take Profit found, make sure it is one of the pre-defined ones and make sure its quantity is up to date as well
                                                                for elem in exit_strategy_tps_short.items():
                                                                    tp_price_ratio = float(elem[0])
                                                                    tp_size_ratio = float(elem[1])
                                                                    tp_price = round_to_tick(entry_price - (((tp_price_ratio/100) / leverage_for_tp_calc) * entry_price), tick_size[symbol])
                                                                    tp_size = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])
                                                                    limit_size = round_step_size(active_order['qty'], qty_step[symbol],min_trading_qty[symbol])
                                                                    if close_enough_match(tp_price, limit_price, tp_size, limit_size, "Sell"): # tp_price==limit_price and tp_size == limit_size # (tp_size==active_order['qty'] or math.floor(tp_size * 10)/10.0==active_order['qty'] or math.floor(tp_size * 100)/100.0==active_order['qty'] or math.floor(tp_size * 1000)/1000.0==active_order['qty'] or math.floor(tp_size * 10000)/10000.0==active_order['qty']):
                                                                        # We found a valid pre-defined TP, keep it (note we check the floor in case the exchange did remove decimals upon creating the order)
                                                                        tp_found = True
                                                                if not tp_found:
                                                                    # Invalid TP (or updated position size not reflected in the TP), REMOVE IT
                                                                    try:
                                                                        session.cancel_active_order(symbol=symbol, order_id=order_id) 
                                                                    except Exception:
                                                                        pass
                                                        else: # Inverse Perpetuals or Futures
                                                            limit_price = float(active_order['price'])
                                                            order_id = active_order['order_id']
                                                            if active_order['side'] == 'Buy' and limit_price < last_price and limit_price < entry_price:
                                                                # Take Profit found, make sure it is one of the pre-defined ones and make sure its quantity is up to date as well
                                                                for elem in exit_strategy_tps_short.items():
                                                                    tp_price_ratio = float(elem[0])
                                                                    tp_size_ratio = float(elem[1])
                                                                    tp_price = round_to_tick(entry_price - (((tp_price_ratio/100) / leverage_for_tp_calc) * entry_price), tick_size[symbol])
                                                                    tp_size = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])
                                                                    limit_size = round_step_size(active_order['qty'], qty_step[symbol],min_trading_qty[symbol])
                                                                    if close_enough_match(tp_price, limit_price, tp_size, limit_size, "Sell"): # tp_price==limit_price and tp_size == limit_size # (tp_size==active_order['qty'] or math.floor(tp_size * 10)/10.0==active_order['qty'] or math.floor(tp_size * 100)/100.0==active_order['qty'] or math.floor(tp_size * 1000)/1000.0==active_order['qty'] or math.floor(tp_size * 10000)/10000.0==active_order['qty']):
                                                                        # We found a valid pre-defined TP, keep it (note we check the floor in case the exchange did remove decimals upon creating the order)
                                                                        tp_found = True
                                                                if not tp_found:
                                                                    # Invalid TP (or updated position size not reflected in the TP), REMOVE IT
                                                                    try:
                                                                        session.cancel_active_order(symbol=symbol, order_id=order_id) 
                                                                    except Exception:
                                                                        pass
                                   
                                            if not tp_found: # No TPs found, so add (this way we kind of avoid re-adding the same TP if price hit and found resistance at and retested it. so we don't TP the same level twice)
                                                # We couldn't find any TPs, let's add the suitable one
                                                # Prepare set_trading_stop arguments to pass to API
                                                limit_tp_args = {'position_idx': position_idx, 'symbol': symbol, 'side': 'Buy', 'order_type': "Limit", 'time_in_force': order_timeInForce, 'reduce_only': True, 'close_on_trigger': True }
                                                
                                                for elem in sorted(exit_strategy_tps_short.items(), reverse=False): # Sort Ascending to find the nearest TP level
                                                    tp_price_ratio = float(elem[0])
                                                    tp_size_ratio = float(elem[1])
                                                    
                                                    limit_tp_args['price'] = round_to_tick(entry_price - (((tp_price_ratio/100) / leverage_for_tp_calc) * entry_price), tick_size[symbol])
                                                    limit_tp_args['qty'] = round_step_size(size * (tp_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])

                                                    if last_price > limit_tp_args['price'] + (exit_strategy['tp_target_tolerance_ratio']/100) * (entry_price - limit_tp_args['price']):
                                                        try:
                                                            session.place_active_order(**limit_tp_args)
                                                            log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " SHORT Take-Profit Limit placed: "+str(tp_size_ratio)+"% of Quantity ("+str(limit_tp_args['qty'])+") @ "+ str(tp_price_ratio) +"% in Profit ("+str(limit_tp_args['price'])+")."
                                                            print(log)
                                                            with open("TP.txt", "a") as myfile:
                                                                myfile.write(log+'\n')
                                                            break # No need to add more TPs, we only place 1 TP at a time
                                                        except Exception as e:
                                                            print(e)
                                                            break
                                                            pass
                   
                    ''' Setup the Stop Losses '''
                    if allow_sls and (len(exit_strategy_sls_long) > 0 or len(exit_strategy_sls_short) > 0):
                        if exit_strategy['sl_target_type'] == 'ratio_post_leverage':
                            leverage_for_sl_calc = leverage
                        elif exit_strategy['sl_target_type'] == 'ratio_pre_leverage':
                            leverage_for_sl_calc = 1
                        
                        if exit_strategy['sl_type'] == 'marketorder':
                            for elem in exit_strategy_sls_long.items():
                                sl_price_ratio_long = float(elem[0])
                                sl_size_ratio_long = float(elem[1])
                            stop_loss_cap_ratio_long = sl_price_ratio_long
                            
                            for elem in exit_strategy_sls_short.items():
                                sl_price_ratio_short = float(elem[0])
                                sl_size_ratio_short = float(elem[1])
                            stop_loss_cap_ratio_short = sl_price_ratio_short
                            
                            # NOTE: Currently the SL is only 100% of position size
                            # TODO: Take value as stored in DB to do ratios for SLs
                            
                            if stop_loss_cap_ratio_long != 0 or stop_loss_cap_ratio_short != 0:
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
                                            position_leveraged_stop_loss = round_to_tick(entry_price - (((stop_loss_cap_ratio_long/100) / leverage_for_sl_calc) * entry_price), tick_size[symbol])
                                            if last_price < position_leveraged_stop_loss:
                                                try:
                                                    session.place_active_order(position_idx=position_idx, symbol=symbol, side="Sell", order_type="Market", qty=size, time_in_force="GoodTillCancel", reduce_only=True, close_on_trigger=True)
                                                    log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " LONG Force-Stopped: "+str(last_price)+"."
                                                    print(log)
                                                    with open("SL_forced.txt", "a") as myfile:
                                                        myfile.write(log+'\n')
                                                except Exception:
                                                    pass
                                        elif side == 'Sell':
                                            position_leveraged_stop_loss = round_to_tick(entry_price + (((stop_loss_cap_ratio_short/100) / leverage_for_sl_calc) * entry_price), tick_size[symbol])
                                            if last_price > position_leveraged_stop_loss:
                                                try:
                                                    session.place_active_order(position_idx=position_idx, symbol=symbol, side="Buy", order_type="Market", qty=size, time_in_force="GoodTillCancel", reduce_only=True, close_on_trigger=True)
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
                                        # Note: order side should be opposite of position side
                                        if side == "Buy" and conditional_order['side'] == "Sell" and conditional_order['order_type'] == 'Market' and conditional_order['order_status'] == 'Untriggered': # Stop Loss for a Long
                                            if symbol.endswith('USDT'): # USDT Perpetual
                                                stop_price = float(conditional_order['trigger_price'])
                                                stop_order_id = conditional_order['stop_order_id']
                                                if stop_price < entry_price and conditional_order['close_on_trigger'] == True and conditional_order['reduce_only'] == True:
                                                    position_leveraged_stop_loss = round_to_tick((entry_price - (((stop_loss_cap_ratio_long/100) / leverage_for_sl_calc) * entry_price)), tick_size[symbol])
                                                    if stop_price >= position_leveraged_stop_loss and float(conditional_order['qty']) == size:
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
                                                position_leveraged_stop_loss = round_to_tick((entry_price - (((stop_loss_cap_ratio_long/100) / leverage_for_sl_calc) * entry_price)), tick_size[symbol])
                                                
                                                if stop_price >= position_leveraged_stop_loss and float(conditional_order['qty']) == size:
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
                                                    position_leveraged_stop_loss = round_to_tick((entry_price + (((stop_loss_cap_ratio_short/100) / leverage_for_sl_calc) * entry_price)), tick_size[symbol])
                                                    if stop_price <= position_leveraged_stop_loss and float(conditional_order['qty']) == size:
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
                                                position_leveraged_stop_loss = round_to_tick((entry_price + (((stop_loss_cap_ratio_short/100) / leverage_for_sl_calc) * entry_price)), tick_size[symbol])
                                                if stop_price <= position_leveraged_stop_loss and float(conditional_order['qty']) == size:
                                                    # Stop Loss found inside the allowed range, keep it
                                                    total_allowed_stop_loss_found += float(conditional_order['qty'])
                                                else:
                                                    # Stop Loss found outside the allowed range, useless so remove it
                                                    try:
                                                        session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id)
                                                    except Exception:
                                                        pass
                                if total_allowed_stop_loss_found < size:
                                    # We couldn't find enough Stop Losses in the allowed range, so remove any conditional orders and add 1 Stop Loss conditional order with total size, at the correct level
                                    # Prepare set_trading_stop arguments to pass to API
                                    set_trading_stop_args = {'position_idx': position_idx, 'symbol': symbol, 'side': side}
                                    if tp_sl_mode == "Partial":
                                        set_trading_stop_args['sl_size'] = size # If Partial Mode then we need to send full size to close full position
                                    
                                    if side == 'Buy':
                                        position_leveraged_stop_loss = round_to_tick(entry_price - (((stop_loss_cap_ratio_long/100) / leverage_for_sl_calc) * entry_price), tick_size[symbol])
                                        if stop_loss == 0 or stop_loss < position_leveraged_stop_loss:
                                            try:
                                                #session.place_conditional_order(symbol=symbol, order_type="Market", reduce_only=True, side= "Sell", qty=size, stop_px=position_leveraged_stop_loss,time_in_force="GoodTillCancel")
                                                set_trading_stop_args['stop_loss'] = position_leveraged_stop_loss
                                                session.set_trading_stop(**set_trading_stop_args)
                                                log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " LONG Maximum Stop-Loss adjusted to: "+str(position_leveraged_stop_loss)+" (" + str(stop_loss_cap_ratio_long) + "%)."
                                                print(log)
                                                with open("SL_protected.txt", "a") as myfile:
                                                    myfile.write(log+'\n')
                                            except Exception:
                                                pass
                                    elif side == 'Sell':
                                        position_leveraged_stop_loss = round_to_tick(entry_price + (((stop_loss_cap_ratio_short/100) / leverage_for_sl_calc) * entry_price), tick_size[symbol])
                                        if stop_loss == 0 or stop_loss > position_leveraged_stop_loss:
                                            try:
                                                #session.place_conditional_order(symbol=symbol, order_type="Market", reduce_only=True, side= "Buy", qty=size, stop_px=position_leveraged_stop_loss,time_in_force="GoodTillCancel")
                                                set_trading_stop_args['stop_loss'] = position_leveraged_stop_loss
                                                session.set_trading_stop(**set_trading_stop_args)
                                                log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " SHORT Maximum Stop-Loss adjusted to: "+str(position_leveraged_stop_loss)+" (" + str(stop_loss_cap_ratio_short) + "%)."
                                                print(log)
                                                with open("SL_protected.txt", "a") as myfile:
                                                    myfile.write(log+'\n')
                                            except Exception:
                                                pass
                   
                    ''' Enforce any Trailing Stops to Lock in Profit/Breakeven '''
                    if allow_sls and (len(exit_strategy_trailing_sls_long) > 0 or len(exit_strategy_trailing_sls_short) > 0):
                        if exit_strategy['sl_target_type'] == 'ratio_post_leverage':
                            leverage_for_sl_calc = leverage
                        elif exit_strategy['sl_target_type'] == 'ratio_pre_leverage':
                            leverage_for_sl_calc = 1
                        
                        if exit_strategy['sl_type'] == 'marketorder':
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
                                    for elem in sorted(exit_strategy_trailing_sls_long.items(), reverse=True): # Sort Descending (reverse order to find the best Take Profit levels to lock in)
                                        lock_in_p_price_ratio = float(elem[0])
                                        lock_in_p_sl_ratio = float(elem[1])
                                        
                                        position_leveraged_p_level = round_to_tick(entry_price + (((lock_in_p_price_ratio/100) / leverage_for_sl_calc) * entry_price), tick_size[symbol])
                                        position_leveraged_p_sl_level = round_to_tick(entry_price + (((lock_in_p_sl_ratio/100) / leverage_for_sl_calc) * entry_price), tick_size[symbol])
                                        if last_price >= position_leveraged_p_level:

                                            # Sarch Conditional Orders if Stop Loss already exists with 'qty'=position size AND 'trigger_price' better than the Take Profit Level
                                            total_in_profit_stop_loss_found = 0.0
                                            
                                            if(fetched_conditional_orders):
                                                for conditional_order in fetched_conditional_orders["result"]:
                                                    # Note: order side should be opposite of position side
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
                                                set_trading_stop_args = {'position_idx': position_idx, 'symbol': symbol, 'side': side}
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
                                    for elem in sorted(exit_strategy_trailing_sls_short.items(), reverse=True): # Sort Descending (reverse order to find the best Take Profit levels to lock in)
                                        lock_in_p_price_ratio = float(elem[0])
                                        lock_in_p_sl_ratio = float(elem[1])
                                        
                                        position_leveraged_p_level = round_to_tick(entry_price - (((lock_in_p_price_ratio/100) / leverage_for_sl_calc) * entry_price), tick_size[symbol])
                                        position_leveraged_p_sl_level = round_to_tick(entry_price - (((lock_in_p_sl_ratio/100) / leverage_for_sl_calc) * entry_price), tick_size[symbol])
                                        if last_price <= position_leveraged_p_level:
                            
                                            # Sarch Conditional Orders if Stop Loss already exists with 'qty'=position size AND 'trigger_price' better than the Take Profit Level
                                            total_in_profit_stop_loss_found = 0.0
                                            
                                            if(fetched_conditional_orders):
                                                for conditional_order in fetched_conditional_orders["result"]:
                                                    # Note: order side should be opposite of position side
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
                                                set_trading_stop_args = {'position_idx': position_idx, 'symbol': symbol, 'side': side}
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
                   
                    #######################################################
                    # Enforce Total Balance Static Stop Loss feature
                    #######################################################
                    
                    if enforce_tb_sl_static: # we don't use allow_sls flag because this is usually set on server side to be forced or modified on the Dashboard (but can't be stopped)
                        if symbol in override_tb_sl_static: # Look if any custom stop ratio for this symbol
                            initial_stop_loss_cap_ratio = override_tb_sl_static[symbol]["tb_initial_sl_static_cap_ratio"]
                            initial_stop_loss_pos_size_ratio = override_tb_sl_static[symbol]["tb_initial_sl_static_pos_size_ratio"]
                            stop_loss_cap_ratio = override_tb_sl_static[symbol]["tb_sl_static_cap_ratio"]
                            stop_loss_pos_size_ratio = override_tb_sl_static[symbol]["tb_sl_static_pos_size_ratio"]
                        else:
                            initial_stop_loss_cap_ratio = default_tb_initial_sl_static_cap_ratio
                            initial_stop_loss_pos_size_ratio = default_tb_initial_sl_static_pos_size_ratio
                            stop_loss_cap_ratio = default_tb_sl_static_cap_ratio
                            stop_loss_pos_size_ratio = default_tb_sl_static_pos_size_ratio
                            
                        # Now check if DB override exists for this symbol (Web Dashboard)
                        if side == "Buy":
                            if (exit_strategy['tb_initial_sl_static_cap_ratio_buy_override'] is not None and float(exit_strategy['tb_initial_sl_static_cap_ratio_buy_override']) != 0 and float(exit_strategy['tb_initial_sl_static_cap_ratio_buy_override']) <= initial_stop_loss_cap_ratio):
                                initial_stop_loss_cap_ratio = float(exit_strategy['tb_initial_sl_static_cap_ratio_buy_override'])
                            if (exit_strategy['tb_initial_sl_static_pos_size_ratio_buy_override'] is not None and float(exit_strategy['tb_initial_sl_static_pos_size_ratio_buy_override']) != 0 and float(exit_strategy['tb_initial_sl_static_pos_size_ratio_buy_override']) >= initial_stop_loss_pos_size_ratio):
                                initial_stop_loss_pos_size_ratio = float(exit_strategy['tb_initial_sl_static_pos_size_ratio_buy_override'])
                            if (exit_strategy['tb_sl_static_cap_ratio_buy_override'] is not None and float(exit_strategy['tb_sl_static_cap_ratio_buy_override']) != 0 and float(exit_strategy['tb_sl_static_cap_ratio_buy_override']) <= stop_loss_cap_ratio):
                                stop_loss_cap_ratio = float(exit_strategy['tb_sl_static_cap_ratio_buy_override'])
                            if (exit_strategy['tb_sl_static_pos_size_ratio_buy_override'] is not None and float(exit_strategy['tb_sl_static_pos_size_ratio_buy_override']) != 0 and float(exit_strategy['tb_sl_static_pos_size_ratio_buy_override']) >= stop_loss_pos_size_ratio):
                                stop_loss_pos_size_ratio = float(exit_strategy['tb_sl_static_pos_size_ratio_buy_override'])
                        elif side == "Sell":
                            if (exit_strategy['tb_initial_sl_static_cap_ratio_sell_override'] is not None and float(exit_strategy['tb_initial_sl_static_cap_ratio_sell_override']) != 0 and float(exit_strategy['tb_initial_sl_static_cap_ratio_sell_override']) <= initial_stop_loss_cap_ratio):
                                initial_stop_loss_cap_ratio = float(exit_strategy['tb_initial_sl_static_cap_ratio_sell_override'])
                            if (exit_strategy['tb_initial_sl_static_pos_size_ratio_sell_override'] is not None and float(exit_strategy['tb_initial_sl_static_pos_size_ratio_sell_override']) != 0 and float(exit_strategy['tb_initial_sl_static_pos_size_ratio_sell_override']) >= initial_stop_loss_pos_size_ratio):
                                initial_stop_loss_pos_size_ratio = float(exit_strategy['tb_initial_sl_static_pos_size_ratio_sell_override'])
                            if (exit_strategy['tb_sl_static_cap_ratio_sell_override'] is not None and float(exit_strategy['tb_sl_static_cap_ratio_sell_override']) != 0 and float(exit_strategy['tb_sl_static_cap_ratio_sell_override']) <= stop_loss_cap_ratio):
                                stop_loss_cap_ratio = float(exit_strategy['tb_sl_static_cap_ratio_sell_override'])
                            if (exit_strategy['tb_sl_static_pos_size_ratio_sell_override'] is not None and float(exit_strategy['tb_sl_static_pos_size_ratio_sell_override']) != 0 and float(exit_strategy['tb_sl_static_pos_size_ratio_sell_override']) >= stop_loss_pos_size_ratio):
                                stop_loss_pos_size_ratio = float(exit_strategy['tb_sl_static_pos_size_ratio_sell_override'])
                                
                        initial_equity = 0
                        # Pull from Database Position Session to check if exists
                        # NOTE: This table doesn't take into consideration 2 sides. So it assume One-Way for the TB SL application for now.
                        mycursor_position_session = mydb.cursor(dictionary=True)
                        mycursor_position_session.execute("SELECT * FROM positions_sessions WHERE api_key='"+api_key+"' AND api_secret='"+api_secret+"' AND symbol='"+symbol+"'")
                        myresult_position_session = mycursor_position_session.fetchall()
                        for this_position_session in myresult_position_session:
                            initial_equity = float(this_position_session['initial_equity'])
                            tb_sl_qty = float(this_position_session['tb_sl_qty'])
                            tb_sl_price = float(this_position_session['tb_sl_price'])
                                
                        if initial_stop_loss_cap_ratio != 0:
                            # First we execute Initial Total Balance Stop Loss as Market Order if needed and this position is a fresh one
                            # Check Database if this position still had no Initial Stop Loss executed on it (otherwise we don't)
                            mycursor_positions_stops = mydb.cursor(dictionary=True)
                            mycursor_positions_stops.execute("SELECT * FROM positions_stops WHERE api_key='"+api_key+"' AND api_secret='"+api_secret+"' AND symbol='"+symbol+"' AND side='"+side+"'")
                            myresult_positions_stops = mycursor_positions_stops.fetchall()
                            if mycursor_positions_stops.rowcount == 0:
                                # No Initial TB Stop Loss executed, Execute if reached the Initial TB and store it in the DB for this position to aviod doing it again in the future untill the position is fully closed
                                if quote_currency[symbol] == "USDT":
                                    wallet_balance = session.get_wallet_balance(coin="USDT")["result"]["USDT"]["wallet_balance"]
                                    highest_balance = wallet_balance if wallet_balance > initial_equity else initial_equity
                                    target_tb_loss_value = (wallet_balance - (highest_balance * (100 - initial_stop_loss_cap_ratio)/100)) if enforce_tb_sl_max_cum_loss else (wallet_balance * initial_stop_loss_cap_ratio/100)
                                    target_tb_sl_ratio = (target_tb_loss_value * 100) / position_value
                                else:
                                    wallet_balance = session.get_wallet_balance(coin=base_currency[symbol])["result"][base_currency[symbol]]["wallet_balance"]
                                    highest_balance = wallet_balance if wallet_balance > initial_equity else initial_equity
                                    target_tb_loss_value = (wallet_balance - (highest_balance * (100 - initial_stop_loss_cap_ratio)/100)) if enforce_tb_sl_max_cum_loss else (wallet_balance * initial_stop_loss_cap_ratio/100)
                                    target_tb_sl_ratio = (target_tb_loss_value * 100) / position_value

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
                                    if side == 'Buy':
                                        # unrealised_pnl_calculated is negative if in loss
                                        unrealised_pnl_calculated = size * ((mark_price -  entry_price))
                                        # Execute Market Stop Loss if needed and price exceeded the level
                                        if unrealised_pnl_calculated <= -1 * target_tb_loss_value:
                                            try:
                                                session.place_active_order(position_idx=position_idx, symbol=symbol, side="Sell", order_type="Market", qty=round_step_size(size * (initial_stop_loss_pos_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol]), time_in_force="GoodTillCancel", reduce_only=True, close_on_trigger=True)
                                                log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " LONG Initial Total Balance Force-Stopped with unrealised PnL of "+str(unrealised_pnl_calculated)+" at: "+str(last_price)+"."
                                                print(log)
                                                with open("SL_forced.txt", "a") as myfile:
                                                    myfile.write(log+'\n')
                                            except Exception:
                                                pass
                                                
                                            try:
                                                # Now add it to the Database
                                                mycursor_add_positions_stops = mydb.cursor(dictionary=True)
                                                insert_sql = "INSERT INTO positions_stops (api_key, api_secret, symbol, side, initial_sl_executed) VALUES (%s, %s, %s, %s, 1)"
                                                vals = (api_key, api_secret, symbol, side)
                                                mycursor_add_positions_stops.execute(insert_sql, vals)
                                                mydb.commit()
                                            except Exception:
                                                pass
                                                
                                            """
                                            try:
                                                # Now remove the Total Balance Stop Loss to auto refresh it with the new values needed
                                                fetched_conditional_orders = session.query_conditional_order(symbol=symbol)
                                            except Exception:
                                                pass
                                            if (fetched_conditional_orders):
                                                for conditional_order in fetched_conditional_orders["result"]:
                                                    # Note: order side should be opposite of position side
                                                    if conditional_order['side'] == "Sell" and conditional_order['order_type'] == 'Market' and conditional_order['order_status'] == 'Untriggered': # Stop Loss for a Long
                                                        stop_price = float(conditional_order['trigger_price'])
                                                        stop_order_id = conditional_order['stop_order_id']
                                                        if stop_price < entry_price and conditional_order['close_on_trigger'] == True and conditional_order['reduce_only'] == True:
                                                            try:
                                                                session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id) 
                                                            except Exception:
                                                                pass
                                            """
                                                                              
                                    elif side == 'Sell':
                                        # unrealised_pnl_calculated is negative if in loss
                                        unrealised_pnl_calculated = size * ((entry_price -  mark_price))
                                        if unrealised_pnl_calculated <= -1 * target_tb_loss_value:
                                            try:
                                                session.place_active_order(position_idx=position_idx, symbol=symbol, side="Buy", order_type="Market", qty=round_step_size(size * (initial_stop_loss_pos_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol]), time_in_force="GoodTillCancel", reduce_only=True, close_on_trigger=True)
                                                log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " SHORT Initial Total Balance Force-Stopped with unrealised PnL of "+str(unrealised_pnl_calculated)+" at: "+str(last_price)+"."
                                                print(log)
                                                with open("SL_forced.txt", "a") as myfile:
                                                    myfile.write(log+'\n')
                                            except Exception:
                                                pass
                                                
                                            try:
                                                # Now add it to the Database
                                                mycursor_add_positions_stops = mydb.cursor(dictionary=True)
                                                insert_sql = "INSERT INTO positions_stops (api_key, api_secret, symbol, side, initial_sl_executed) VALUES (%s, %s, %s, %s, 1)"
                                                vals = (api_key, api_secret, symbol, side)
                                                mycursor_add_positions_stops.execute(insert_sql, vals)
                                                mydb.commit()
                                            except Exception:
                                                pass
                                            
                                            """
                                            try:
                                                # Now remove the Total Balance Stop Loss to auto refresh it with the new values needed
                                                fetched_conditional_orders = session.query_conditional_order(symbol=symbol)
                                            except Exception:
                                                pass
                                            if (fetched_conditional_orders):
                                                for conditional_order in fetched_conditional_orders["result"]:
                                                    # Note: order side should be opposite of position side
                                                    if conditional_order['side'] == "Buy" and conditional_order['order_type'] == 'Market' and conditional_order['order_status'] == 'Untriggered': # Stop Loss for a Short
                                                        stop_price = float(conditional_order['trigger_price'])
                                                        stop_order_id = conditional_order['stop_order_id']
                                                        if stop_price > entry_price and conditional_order['close_on_trigger'] == True and conditional_order['reduce_only'] == True:
                                                            try:
                                                                session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id)
                                                            except Exception:
                                                                pass
                                            """
                                else:
                                    if side == 'Buy':
                                        # unrealised_pnl_calculated is negative if in loss
                                        unrealised_pnl_calculated = size * (((1.0/entry_price) -  (1.0/mark_price)))
                                        if unrealised_pnl_calculated <= -1 * target_tb_loss_value:
                                            try:
                                                session.place_active_order(position_idx=position_idx, symbol=symbol, side="Sell", order_type="Market", qty=round_step_size(size * (initial_stop_loss_pos_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol]), time_in_force="GoodTillCancel", reduce_only=True, close_on_trigger=True)
                                                log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " LONG Initial Total Balance Force-Stopped with unrealised PnL of "+str(unrealised_pnl_calculated)+" at: "+str(last_price)+"."
                                                print(log)
                                                with open("SL_forced.txt", "a") as myfile:
                                                    myfile.write(log+'\n')
                                            except Exception:
                                                pass
                                                
                                            try:
                                                # Now add it to the Database
                                                mycursor_add_positions_stops = mydb.cursor(dictionary=True)
                                                insert_sql = "INSERT INTO positions_stops (api_key, api_secret, symbol, side, initial_sl_executed) VALUES (%s, %s, %s, %s, 1)"
                                                vals = (api_key, api_secret, symbol, side)
                                                mycursor_add_positions_stops.execute(insert_sql, vals)
                                                mydb.commit()
                                            except Exception:
                                                pass
                                                
                                            """
                                            try:
                                                # Now remove the Total Balance Stop Loss to auto refresh it with the new values needed
                                                fetched_conditional_orders = session.query_conditional_order(symbol=symbol)
                                            except Exception:
                                                pass
                                            if (fetched_conditional_orders):
                                                for conditional_order in fetched_conditional_orders["result"]:
                                                    # Note: order side should be opposite of position side
                                                    if conditional_order['side'] == "Sell" and conditional_order['order_type'] == 'Market' and conditional_order['order_status'] == 'Untriggered': # Stop Loss for a Short
                                                        stop_price = float(conditional_order['stop_px'])
                                                        stop_order_id = conditional_order['stop_order_id']
                                                        if stop_price < entry_price and conditional_order['close_on_trigger'] == True and conditional_order['reduce_only'] == True:
                                                            try:
                                                                session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id)
                                                            except Exception:
                                                                pass
                                            """
                                                

                                    elif side == 'Sell':
                                        # unrealised_pnl_calculated is negative if in loss
                                        unrealised_pnl_calculated = size * (((1.0/mark_price) -  (1.0/entry_price)))
                                        if unrealised_pnl_calculated <= -1 * target_tb_loss_value:
                                            try:
                                                session.place_active_order(position_idx=position_idx, symbol=symbol, side="Buy", order_type="Market", qty=round_step_size(size * (initial_stop_loss_pos_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol]), time_in_force="GoodTillCancel", reduce_only=True, close_on_trigger=True)
                                                log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " SHORT Initial Total Balance Force-Stopped with unrealised PnL of "+str(unrealised_pnl_calculated)+" at: "+str(last_price)+"."
                                                print(log)
                                                with open("SL_forced.txt", "a") as myfile:
                                                    myfile.write(log+'\n')
                                            except Exception:
                                                pass
                                                
                                            try:
                                                # Now add it to the Database
                                                mycursor_add_positions_stops = mydb.cursor(dictionary=True)
                                                insert_sql = "INSERT INTO positions_stops (api_key, api_secret, symbol, side, initial_sl_executed) VALUES (%s, %s, %s, %s, 1)"
                                                vals = (api_key, api_secret, symbol, side)
                                                mycursor_add_positions_stops.execute(insert_sql, vals)
                                                mydb.commit()
                                            except Exception:
                                                pass
                        
                                            """
                                            try:
                                                # Now remove the Total Balance Stop Loss to auto refresh it with the new values needed
                                                fetched_conditional_orders = session.query_conditional_order(symbol=symbol)
                                            except Exception:
                                                pass
                                            if (fetched_conditional_orders):
                                                for conditional_order in fetched_conditional_orders["result"]:
                                                    # Note: order side should be opposite of position side
                                                    if conditional_order['side'] == "Buy" and conditional_order['order_type'] == 'Market' and conditional_order['order_status'] == 'Untriggered': # Stop Loss for a Short
                                                        stop_price = float(conditional_order['stop_px'])
                                                        stop_order_id = conditional_order['stop_order_id']
                                                        if stop_price > entry_price and conditional_order['close_on_trigger'] == True and conditional_order['reduce_only'] == True:
                                                            try:
                                                                session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id)
                                                            except Exception:
                                                                pass
                                            """
                        
                        if stop_loss_cap_ratio != 0:
                            # Now we place/execute the general Total Balance Stop Loss
                            if quote_currency[symbol] == "USDT":
                                wallet_balance = session.get_wallet_balance(coin="USDT")["result"]["USDT"]["wallet_balance"]
                                highest_balance = wallet_balance if wallet_balance > initial_equity else initial_equity
                                target_tb_loss_value = (wallet_balance - (highest_balance * (100 - stop_loss_cap_ratio)/100)) if enforce_tb_sl_max_cum_loss else (wallet_balance * stop_loss_cap_ratio/100)
                                target_tb_sl_ratio = (target_tb_loss_value * 100) / position_value
                            else:
                                wallet_balance = session.get_wallet_balance(coin=base_currency[symbol])["result"][base_currency[symbol]]["wallet_balance"]
                                highest_balance = wallet_balance if wallet_balance > initial_equity else initial_equity
                                target_tb_loss_value = (wallet_balance - (highest_balance * (100 - stop_loss_cap_ratio)/100)) if enforce_tb_sl_max_cum_loss else (wallet_balance * stop_loss_cap_ratio/100)
                                target_tb_sl_ratio = (target_tb_loss_value * 100) / position_value
                                
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
                                        
                            # 1) Check if immediate market close is needed in case Unrealised PnL already reached the specified Balance Stop Loss ratio
                            if(enforce_tb_sl_static_emergency_exit):
                                # First, fetch Wallet Balance
                                if quote_currency[symbol] == "USDT":
                                    if side == 'Buy':
                                        # unrealised_pnl_calculated is negative if in loss
                                        unrealised_pnl_calculated = size * ((mark_price -  entry_price))
                                        # Execute Market Stop Loss if needed and price exceeded the level
                                        if unrealised_pnl_calculated <= -1 * target_tb_loss_value:
                                            try:
                                                session.place_active_order(position_idx=position_idx, symbol=symbol, side="Sell", order_type="Market", qty=round_step_size(size * (stop_loss_pos_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol]), time_in_force="GoodTillCancel", reduce_only=True, close_on_trigger=True)
                                                log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " LONG Total Balance Force-Stopped with unrealised PnL of "+str(unrealised_pnl_calculated)+" at: "+str(last_price)+"."
                                                print(log)
                                                with open("SL_forced.txt", "a") as myfile:
                                                    myfile.write(log+'\n')
                                            except Exception:
                                                pass
                                                
                                            try:
                                                # Now update the Database
                                                mycursor_update_tb_sl_session = mydb.cursor(dictionary=True)
                                                update_sql = "UPDATE positions_sessions SET tb_sl_qty=%s, tb_sl_price=%s WHERE api_key=%s AND api_secret=%s AND symbol=%s;"
                                                vals = (round_step_size(size * (stop_loss_pos_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol]), last_price, api_key, api_secret, symbol)
                                                mycursor_update_tb_sl_session.execute(update_sql, vals)
                                                mydb.commit()
                                            except Exception:
                                                pass
                                                
                                    elif side == 'Sell':
                                        # unrealised_pnl_calculated is negative if in loss
                                        unrealised_pnl_calculated = size * ((entry_price -  mark_price))
                                        if unrealised_pnl_calculated <= -1 * target_tb_loss_value:
                                            try:
                                                session.place_active_order(position_idx=position_idx, symbol=symbol, side="Buy", order_type="Market", qty=round_step_size(size * (stop_loss_pos_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol]), time_in_force="GoodTillCancel", reduce_only=True, close_on_trigger=True)
                                                log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " SHORT Total Balance Force-Stopped with unrealised PnL of "+str(unrealised_pnl_calculated)+" at: "+str(last_price)+"."
                                                print(log)
                                                with open("SL_forced.txt", "a") as myfile:
                                                    myfile.write(log+'\n')
                                            except Exception:
                                                pass
                                                
                                            try:
                                                # Now update the Database
                                                mycursor_update_tb_sl_session = mydb.cursor(dictionary=True)
                                                update_sql = "UPDATE positions_sessions SET tb_sl_qty=%s, tb_sl_price=%s WHERE api_key=%s AND api_secret=%s AND symbol=%s;"
                                                vals = (round_step_size(size * (stop_loss_pos_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol]), last_price, api_key, api_secret, symbol)
                                                mycursor_update_tb_sl_session.execute(update_sql, vals)
                                                mydb.commit()
                                            except Exception:
                                                pass
                                else:
                                    if side == 'Buy':
                                        # unrealised_pnl_calculated is negative if in loss
                                        unrealised_pnl_calculated = size * (((1.0/entry_price) -  (1.0/mark_price)))
                                        if unrealised_pnl_calculated <= -1 * target_tb_loss_value:
                                            try:
                                                session.place_active_order(position_idx=position_idx, symbol=symbol, side="Sell", order_type="Market", qty=round_step_size(size * (stop_loss_pos_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol]), time_in_force="GoodTillCancel", reduce_only=True, close_on_trigger=True)
                                                log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " LONG Total Balance Force-Stopped with unrealised PnL of "+str(unrealised_pnl_calculated)+" at: "+str(last_price)+"."
                                                print(log)
                                                with open("SL_forced.txt", "a") as myfile:
                                                    myfile.write(log+'\n')
                                            except Exception:
                                                pass
                                                
                                            try:
                                                # Now update the Database
                                                mycursor_update_tb_sl_session = mydb.cursor(dictionary=True)
                                                update_sql = "UPDATE positions_sessions SET tb_sl_qty=%s, tb_sl_price=%s WHERE api_key=%s AND api_secret=%s AND symbol=%s;"
                                                vals = (round_step_size(size * (stop_loss_pos_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol]), last_price, api_key, api_secret, symbol)
                                                mycursor_update_tb_sl_session.execute(update_sql, vals)
                                                mydb.commit()
                                            except Exception:
                                                pass
                                    elif side == 'Sell':
                                        # unrealised_pnl_calculated is negative if in loss
                                        unrealised_pnl_calculated = size * (((1.0/mark_price) -  (1.0/entry_price)))
                                        if unrealised_pnl_calculated <= -1 * target_tb_loss_value:
                                            try:
                                                session.place_active_order(position_idx=position_idx, symbol=symbol, side="Buy", order_type="Market", qty=round_step_size(size * (stop_loss_pos_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol]), time_in_force="GoodTillCancel", reduce_only=True, close_on_trigger=True)
                                                log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " SHORT Total Balance Force-Stopped with unrealised PnL of "+str(unrealised_pnl_calculated)+" at: "+str(last_price)+"."
                                                print(log)
                                                with open("SL_forced.txt", "a") as myfile:
                                                    myfile.write(log+'\n')
                                            except Exception:
                                                pass
                                                
                                            try:
                                                # Now update the Database
                                                mycursor_update_tb_sl_session = mydb.cursor(dictionary=True)
                                                update_sql = "UPDATE positions_sessions SET tb_sl_qty=%s, tb_sl_price=%s WHERE api_key=%s AND api_secret=%s AND symbol=%s;"
                                                vals = (round_step_size(size * (stop_loss_pos_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol]), last_price, api_key, api_secret, symbol)
                                                mycursor_update_tb_sl_session.execute(update_sql, vals)
                                                mydb.commit()
                                            except Exception:
                                                pass
                                            
                            # 2) Place Stop Loss or adjust it
                            # Loop over all stops for this side position, and cancel every stop: Not matching the target total balance stop quantity OR out of allowed range
                            # Keep the ones otherwise and count their total size
                            
                            position_tb_sl_db = None
                            if enforce_tb_sl_db_stored:
                                # Fetch TB SL from DB for this position to take the one closer to price
                                mycursor_positions_tb_sl = mydb.cursor(dictionary=True)
                                mycursor_positions_tb_sl.execute("SELECT * FROM positions_tb_sl WHERE api_key='"+api_key+"' AND api_secret='"+api_secret+"' AND symbol='"+symbol+"' AND side='"+side+"'")
                                myresult_positions_tb_sl = mycursor_positions_tb_sl.fetchall()
                                for position_tb_sl in myresult_positions_tb_sl:
                                    position_tb_sl_db = float(position_tb_sl['tb_sl_price'])

                            
                            total_allowed_stop_loss_found = 0.0
                            try:
                                fetched_conditional_orders = session.query_conditional_order(symbol=symbol)
                            except Exception:
                                pass
                            if (fetched_conditional_orders):
                                for conditional_order in fetched_conditional_orders["result"]:
                                    # Note: order side should be opposite of position side
                                    if side == "Buy" and conditional_order['side'] == "Sell" and conditional_order['order_type'] == 'Market' and conditional_order['order_status'] == 'Untriggered': # Stop Loss for a Long
                                        if symbol.endswith('USDT'): # USDT Perpetual
                                            stop_price = float(conditional_order['trigger_price'])
                                            stop_order_id = conditional_order['stop_order_id']
                                            if conditional_order['close_on_trigger'] == True and conditional_order['reduce_only'] == True:
                                                position_stop_loss = round_to_tick(entry_price - ((target_tb_sl_ratio/100) * entry_price), tick_size[symbol])
                                                
                                                if enforce_tb_sl_db_stored and position_tb_sl_db is not None:
                                                    # Fetch TB SL from DB for this position to take the one closer to price
                                                    if position_tb_sl_db > position_stop_loss:
                                                        position_stop_loss = position_tb_sl_db
                                                        
                                                '''if enforce_tb_sl_db_stored:
                                                    # Store the Total Balance SL in the Database to prevent moving it further away in case position size changed
                                                    try:
                                                        mycursor_add_positions_tb_sl = mydb.cursor(dictionary=True)
                                                        insert_sql = "INSERT INTO positions_tb_sl (api_key, api_secret, symbol, side, tb_sl_price, order_count, locked, size, last_updated) VALUES(%s, %s, %s, %s, %s, 1, 1, %s, NOW()) ON DUPLICATE KEY UPDATE size=%s, tb_sl_price=%s, last_updated=NOW();"
                                                        vals = (api_key, api_secret, symbol, side, position_stop_loss, size, size, position_stop_loss)
                                                        mycursor_add_positions_tb_sl.execute(insert_sql, vals)
                                                        mydb.commit()
                                                    except Exception:
                                                        pass'''
                                                    
                                                if ((enforce_tb_sl_static_range and stop_price >= position_stop_loss) or (not enforce_tb_sl_static_range and stop_price == position_stop_loss)):
                                                    # Stop Loss found inside the allowed range, keep it
                                                    if (tb_sl_qty == round_step_size(size * (stop_loss_pos_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol]) and tb_sl_price == position_stop_loss):
                                                         # IF the size and price of TB SL were already updated before in the DB as in placed this TB SL before, then it is already valid and considered
                                                        if (float(conditional_order['qty']) == round_step_size(size * (stop_loss_pos_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])):
                                                            # AND correct exact size order found (so the SL not any conditional order within the allowed range)
                                                            total_allowed_stop_loss_found += float(conditional_order['qty'])
                                                    else:
                                                        # Position changed and a fresh TB SL is yet to be added so cancel whats on the chart to refresh
                                                        try:
                                                            session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id) 
                                                        except Exception:
                                                            pass
                                                else:
                                                    if conditional_order['close_on_trigger'] == True and conditional_order['reduce_only'] == True:
                                                        # Stop Loss found outside the allowed range, so remove it
                                                        try:
                                                            session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id) 
                                                        except Exception:
                                                            pass
                                                    
                                        else: # Inverse Perpetuals or Futures
                                            stop_price = float(conditional_order['stop_px'])
                                            stop_order_id = conditional_order['order_id']
                                            position_stop_loss = round_to_tick(entry_price - ((target_tb_sl_ratio/100) * entry_price), tick_size[symbol])
                                            
                                            if enforce_tb_sl_db_stored and position_tb_sl_db is not None:
                                                # Fetch TB SL from DB for this position to take the one closer to price
                                                if position_tb_sl_db > position_stop_loss:
                                                    position_stop_loss = position_tb_sl_db
                                            
                                            '''if enforce_tb_sl_db_stored:
                                                # Store the Total Balance SL in the Database to prevent moving it further away in case position size changed
                                                try:
                                                    mycursor_add_positions_tb_sl = mydb.cursor(dictionary=True)
                                                    insert_sql = "INSERT INTO positions_tb_sl (api_key, api_secret, symbol, side, tb_sl_price, order_count, locked, size, last_updated) VALUES(%s, %s, %s, %s, %s, 1, 1, %s, NOW()) ON DUPLICATE KEY UPDATE size=%s, tb_sl_price=%s, last_updated=NOW();"
                                                    vals = (api_key, api_secret, symbol, side, position_stop_loss, size, size, position_stop_loss)
                                                    mycursor_add_positions_tb_sl.execute(insert_sql, vals)
                                                    mydb.commit()
                                                except Exception:
                                                    pass'''
                                            
                                            if ((enforce_tb_sl_static_range and stop_price >= position_stop_loss) or (not enforce_tb_sl_static_range and stop_price == position_stop_loss)):
                                                # Stop Loss found inside the allowed range, keep it
                                                if (tb_sl_qty == round_step_size(size * (stop_loss_pos_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol]) and tb_sl_price == position_stop_loss):
                                                     # IF the size and price of TB SL were already updated before in the DB as in placed this TB SL before, then it is already valid and considered
                                                    if (float(conditional_order['qty']) == round_step_size(size * (stop_loss_pos_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])):
                                                        # AND correct exact size order found (so the SL not any conditional order within the allowed range)
                                                        total_allowed_stop_loss_found += float(conditional_order['qty'])
                                                else:
                                                    # Position changed and a fresh TB SL is yet to be added so cancel whats on the chart to refresh
                                                    try:
                                                        session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id) 
                                                    except Exception:
                                                        pass
                                            else:
                                                if conditional_order['close_on_trigger'] == True and conditional_order['reduce_only'] == True:
                                                    # Stop Loss found outside the allowed range, so remove it
                                                    try:
                                                        session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id) 
                                                    except Exception:
                                                        pass

                                    elif side == "Sell" and conditional_order['side'] == "Buy" and conditional_order['order_type'] == 'Market' and conditional_order['order_status'] == 'Untriggered': # Stop Loss for a Short
                                        if symbol.endswith('USDT'): # USDT Perpetual
                                            stop_price = float(conditional_order['trigger_price'])
                                            stop_order_id = conditional_order['stop_order_id']
                                            if conditional_order['close_on_trigger'] == True and conditional_order['reduce_only'] == True:
                                                position_stop_loss = round_to_tick(entry_price + ((target_tb_sl_ratio/100) * entry_price), tick_size[symbol])
                                                
                                                if enforce_tb_sl_db_stored and position_tb_sl_db is not None:
                                                    # Fetch TB SL from DB for this position to take the one closer to price
                                                    if position_tb_sl_db < position_stop_loss:
                                                        position_stop_loss = position_tb_sl_db
                                                
                                                '''if enforce_tb_sl_db_stored:
                                                    # Store the Total Balance SL in the Database to prevent moving it further away in case position size changed
                                                    try:
                                                        mycursor_add_positions_tb_sl = mydb.cursor(dictionary=True)
                                                        insert_sql = "INSERT INTO positions_tb_sl (api_key, api_secret, symbol, side, tb_sl_price, order_count, locked, size, last_updated) VALUES(%s, %s, %s, %s, %s, 1, 1, %s, NOW()) ON DUPLICATE KEY UPDATE size=%s, tb_sl_price=%s, last_updated=NOW();"
                                                        vals = (api_key, api_secret, symbol, side, position_stop_loss, size, size, position_stop_loss)
                                                        mycursor_add_positions_tb_sl.execute(insert_sql, vals)
                                                        mydb.commit()
                                                    except Exception:
                                                        pass'''
                                                
                                                if ((enforce_tb_sl_static_range and stop_price <= position_stop_loss) or (not enforce_tb_sl_static_range and stop_price == position_stop_loss)):
                                                    # Stop Loss found inside the allowed range, keep it
                                                    if (tb_sl_qty == round_step_size(size * (stop_loss_pos_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol]) and tb_sl_price == position_stop_loss):
                                                         # IF the size and price of TB SL were already updated before in the DB as in placed this TB SL before, then it is already valid and considered
                                                        if (float(conditional_order['qty']) == round_step_size(size * (stop_loss_pos_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])):
                                                            # AND correct exact size order found (so the SL not any conditional order within the allowed range)
                                                            total_allowed_stop_loss_found += float(conditional_order['qty'])
                                                    else:
                                                        # Position changed and a fresh TB SL is yet to be added so cancel whats on the chart to refresh
                                                        try:
                                                            session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id) 
                                                        except Exception:
                                                            pass
                                                else:
                                                    if conditional_order['close_on_trigger'] == True and conditional_order['reduce_only'] == True:
                                                        # Stop Loss found outside the allowed range, so remove it
                                                        try:
                                                            session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id) 
                                                        except Exception:
                                                            pass
                                        
                                        else: # Inverse Perpetuals or Futuresstop_price = float(conditional_order['stop_px'])
                                            stop_order_id = conditional_order['order_id']
                                            position_stop_loss = round_to_tick(entry_price + ((target_tb_sl_ratio/100) * entry_price), tick_size[symbol])
                                            
                                            if enforce_tb_sl_db_stored and position_tb_sl_db is not None:
                                                # Fetch TB SL from DB for this position to take the one closer to price
                                                if position_tb_sl_db < position_stop_loss:
                                                    position_stop_loss = position_tb_sl_db
                                            
                                            '''if enforce_tb_sl_db_stored:
                                                # Store the Total Balance SL in the Database to prevent moving it further away in case position size changed
                                                try:
                                                    mycursor_add_positions_tb_sl = mydb.cursor(dictionary=True)
                                                    insert_sql = "INSERT INTO positions_tb_sl (api_key, api_secret, symbol, side, tb_sl_price, order_count, locked, size, last_updated) VALUES(%s, %s, %s, %s, %s, 1, 1, %s, NOW()) ON DUPLICATE KEY UPDATE size=%s, tb_sl_price=%s, last_updated=NOW();"
                                                    vals = (api_key, api_secret, symbol, side, position_stop_loss, size, size, position_stop_loss)
                                                    mycursor_add_positions_tb_sl.execute(insert_sql, vals)
                                                    mydb.commit()
                                                except Exception:
                                                    pass'''
                                            
                                            if ((enforce_tb_sl_static_range and stop_price <= position_stop_loss) or (not enforce_tb_sl_static_range and stop_price == position_stop_loss)):
                                                # Stop Loss found inside the allowed range, keep it
                                                if (tb_sl_qty == round_step_size(size * (stop_loss_pos_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol]) and tb_sl_price == position_stop_loss):
                                                     # IF the size and price of TB SL were already updated before in the DB as in placed this TB SL before, then it is already valid and considered
                                                    if (float(conditional_order['qty']) == round_step_size(size * (stop_loss_pos_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])):
                                                        # AND correct exact size order found (so the SL not any conditional order within the allowed range)
                                                        total_allowed_stop_loss_found += float(conditional_order['qty'])
                                                else:
                                                    # Position changed and a fresh TB SL is yet to be added so cancel whats on the chart to refresh
                                                    try:
                                                        session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id) 
                                                    except Exception:
                                                        pass
                                            else:
                                                if conditional_order['close_on_trigger'] == True and conditional_order['reduce_only'] == True:
                                                    # Stop Loss found outside the allowed range, so remove it
                                                    try:
                                                        session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id) 
                                                    except Exception:
                                                        pass
                                                    
                            if total_allowed_stop_loss_found == 0.0:
                                # We couldn't find a Stop Loss in the allowed range, add 1 Stop Loss conditional order with target size, at the correct level
                                # Prepare set_trading_stop arguments to pass to API
                                set_trading_stop_args = {'position_idx': position_idx, 'symbol': symbol, 'side': side}
                                if tp_sl_mode == "Partial":
                                    set_trading_stop_args['sl_size'] = round_step_size(size * (stop_loss_pos_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol]) # If Partial Mode then we need to send size to close position
                                
                                if side == 'Buy':
                                    position_stop_loss = round_to_tick(entry_price - ((target_tb_sl_ratio/100) * entry_price), tick_size[symbol])
                                    
                                    if enforce_tb_sl_db_stored and position_tb_sl_db is not None:
                                        # Fetch TB SL from DB for this position to take the one closer to price
                                        if position_tb_sl_db > position_stop_loss:
                                            position_stop_loss = position_tb_sl_db
                                        
                                    if enforce_tb_sl_db_stored:
                                        # Store the Total Balance SL in the Database to prevent moving it further away in case position size changed
                                        try:
                                            mycursor_add_positions_tb_sl = mydb.cursor(dictionary=True)
                                            insert_sql = "INSERT INTO positions_tb_sl (api_key, api_secret, symbol, side, tb_sl_price, order_count, locked, size, last_updated) VALUES(%s, %s, %s, %s, %s, 2, 1, %s, NOW()) ON DUPLICATE KEY UPDATE size=%s, tb_sl_price=%s, last_updated=NOW();"
                                            vals = (api_key, api_secret, symbol, side, position_stop_loss, size, size, position_stop_loss)
                                            mycursor_add_positions_tb_sl.execute(insert_sql, vals)
                                            mydb.commit()
                                        except Exception:
                                            pass
                                            
                                    try:
                                        set_trading_stop_args['stop_loss'] = position_stop_loss
                                        session.set_trading_stop(**set_trading_stop_args)
                                        log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " LONG Total Balance Stop-Loss placed at: "+str(position_stop_loss)+" (" + str(stop_loss_pos_size_ratio) + "% of position size = " + str(set_trading_stop_args['sl_size']) + ", " + str(stop_loss_cap_ratio) + "% of total balance)."
                                        print(log)
                                        with open("SL_protected.txt", "a") as myfile:
                                            myfile.write(log+'\n')
                                    except Exception:
                                        pass
                                        
                                    try:
                                        # Now update the Database
                                        mycursor_update_tb_sl_session = mydb.cursor(dictionary=True)
                                        update_sql = "UPDATE positions_sessions SET tb_sl_qty=%s, tb_sl_price=%s WHERE api_key=%s AND api_secret=%s AND symbol=%s;"
                                        vals = (round_step_size(size * (stop_loss_pos_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol]), position_stop_loss, api_key, api_secret, symbol)
                                        mycursor_update_tb_sl_session.execute(update_sql, vals)
                                        mydb.commit()
                                    except Exception:
                                        pass
                                        
                                elif side == 'Sell':
                                    position_stop_loss = round_to_tick(entry_price + ((target_tb_sl_ratio/100) * entry_price), tick_size[symbol])
                                    
                                    if enforce_tb_sl_db_stored and position_tb_sl_db is not None:
                                        # Fetch TB SL from DB for this position to take the one closer to price
                                        if position_tb_sl_db < position_stop_loss:
                                            position_stop_loss = position_tb_sl_db
                                    
                                    if enforce_tb_sl_db_stored:
                                        # Store the Total Balance SL in the Database to prevent moving it further away in case position size changed
                                        try:
                                            mycursor_add_positions_tb_sl = mydb.cursor(dictionary=True)
                                            insert_sql = "INSERT INTO positions_tb_sl (api_key, api_secret, symbol, side, tb_sl_price, order_count, locked, size, last_updated) VALUES(%s, %s, %s, %s, %s, 2, 1, %s, NOW()) ON DUPLICATE KEY UPDATE size=%s, tb_sl_price=%s, last_updated=NOW();"
                                            vals = (api_key, api_secret, symbol, side, position_stop_loss, size, size, position_stop_loss)
                                            mycursor_add_positions_tb_sl.execute(insert_sql, vals)
                                            mydb.commit()
                                        except Exception:
                                            pass
                                    
                                    try:
                                        set_trading_stop_args['stop_loss'] = position_stop_loss
                                        session.set_trading_stop(**set_trading_stop_args)
                                        log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " SHORT Total Balance Stop-Loss placed at: "+str(position_stop_loss)+" (" + str(stop_loss_pos_size_ratio) + "% of position size = " + str(set_trading_stop_args['sl_size']) + ", " + str(stop_loss_cap_ratio) + "% of total balance)."
                                        print(log)
                                        with open("SL_protected.txt", "a") as myfile:
                                            myfile.write(log+'\n')
                                    except Exception:
                                        pass
                                        
                                    try:
                                        # Now update the Database
                                        mycursor_update_tb_sl_session = mydb.cursor(dictionary=True)
                                        update_sql = "UPDATE positions_sessions SET tb_sl_qty=%s, tb_sl_price=%s WHERE api_key=%s AND api_secret=%s AND symbol=%s;"
                                        vals = (round_step_size(size * (stop_loss_pos_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol]), position_stop_loss, api_key, api_secret, symbol)
                                        mycursor_update_tb_sl_session.execute(update_sql, vals)
                                        mydb.commit()
                                    except Exception:
                                        pass
                    

                    #######################################################
                    # Enforce Total Balance Hedge feature
                    #######################################################
                    
                    if(enforce_tb_hedge):
                        if symbol in override_tb_hedge: # Look if any custom hedge ratio for this symbol
                            hedge_cap_ratio = override_tb_hedge[symbol]["tb_hedge_cap_ratio"]
                            hedge_pos_size_ratio = override_tb_hedge[symbol]["tb_hedge_pos_size_ratio"]
                            hedge_balancer_cap_ratio = override_tb_hedge[symbol]["tb_hedge_balancer_cap_ratio"]
                            hedge_sl_static_cap_ratio = override_tb_hedge[symbol]["tb_hedge_sl_static_cap_ratio"]
                        else:
                            hedge_cap_ratio = default_tb_hedge_cap_ratio
                            hedge_pos_size_ratio = default_tb_hedge_pos_size_ratio
                            hedge_balancer_cap_ratio = default_tb_hedge_balancer_cap_ratio
                            hedge_sl_static_cap_ratio = default_tb_hedge_sl_static_cap_ratio
                            
                        # Now check if DB override exists for this symbol (Web Dashboard)
                        if side == "Buy":
                            if (exit_strategy['tb_hedge_cap_ratio_buy_override'] is not None and float(exit_strategy['tb_hedge_cap_ratio_buy_override']) != 0 and float(exit_strategy['tb_hedge_cap_ratio_buy_override']) <= hedge_cap_ratio) and (exit_strategy['tb_hedge_pos_size_ratio_buy_override'] is not None and float(exit_strategy['tb_hedge_pos_size_ratio_buy_override']) != 0 and float(exit_strategy['tb_hedge_pos_size_ratio_buy_override']) <= hedge_pos_size_ratio):
                                hedge_cap_ratio = float(exit_strategy['tb_hedge_cap_ratio_buy_override'])
                                hedge_pos_size_ratio = float(exit_strategy['tb_hedge_pos_size_ratio_buy_override'])
                        elif side == "Sell":
                            if (exit_strategy['tb_hedge_cap_ratio_sell_override'] is not None and float(exit_strategy['tb_hedge_cap_ratio_sell_override']) != 0 and float(exit_strategy['tb_hedge_cap_ratio_sell_override']) <= hedge_cap_ratio) and (exit_strategy['tb_hedge_pos_size_ratio_sell_override'] is not None and float(exit_strategy['tb_hedge_pos_size_ratio_sell_override']) != 0 and float(exit_strategy['tb_hedge_pos_size_ratio_sell_override']) <= hedge_pos_size_ratio):
                                hedge_cap_ratio = float(exit_strategy['tb_hedge_cap_ratio_sell_override'])
                                hedge_pos_size_ratio = float(exit_strategy['tb_hedge_pos_size_ratio_sell_override'])
                                
                        if (exit_strategy['tb_hedge_balancer_cap_ratio_override'] is not None and float(exit_strategy['tb_hedge_balancer_cap_ratio_override']) != 0 and float(exit_strategy['tb_hedge_balancer_cap_ratio_override']) <= hedge_balancer_cap_ratio):
                            hedge_balancer_cap_ratio = float(exit_strategy['tb_hedge_balancer_cap_ratio_override'])
                            
                        if (exit_strategy['tb_hedge_sl_static_cap_ratio_override'] is not None and float(exit_strategy['tb_hedge_sl_static_cap_ratio_override']) != 0 and float(exit_strategy['tb_hedge_sl_static_cap_ratio_override']) <= hedge_sl_static_cap_ratio):
                            hedge_sl_static_cap_ratio = float(exit_strategy['tb_hedge_sl_static_cap_ratio_override'])

                        if quote_currency[symbol] == "USDT":
                            wallet_balance = session.get_wallet_balance(coin="USDT")["result"]["USDT"]["wallet_balance"]
                            equity = session.get_wallet_balance(coin="USDT")["result"]["USDT"]["equity"]
                        else:
                            wallet_balance = session.get_wallet_balance(coin=base_currency[symbol])["result"][base_currency[symbol]]["wallet_balance"]
                            equity = session.get_wallet_balance(coin=base_currency[symbol])["result"][base_currency[symbol]]["equity"]
                            
                        
                        # Pull from Database Position Session to check if exists and whether it is Hedge Balanced before or not
                        mycursor_position_session = mydb.cursor(dictionary=True)
                        mycursor_position_session.execute("SELECT * FROM positions_sessions WHERE api_key='"+api_key+"' AND api_secret='"+api_secret+"' AND symbol='"+symbol+"'")
                        myresult_position_session = mycursor_position_session.fetchall()
                        for this_position_session in myresult_position_session:
                            if hedge_cap_ratio != 0:
                                if this_position_session['balanced_hedge'] == 1 and hedge_balancer_cap_ratio > 0:
                                    target_tb_hedge_balancer_loss_value = float(this_position_session['last_balanced_equity']) * hedge_balancer_cap_ratio/100
                                    if (equity < float(this_position_session['last_balanced_equity']) - target_tb_hedge_balancer_loss_value):
                                        # This position was Hedge Balanced before so we only execute Market Order Hedge Balancing on it from now on based on real-time Equity compared to the DB stored equity
                                        
                                        hedge_balancer_opposite_side_found = False
                                        
                                        target_hedge_qty = 0
                                        target_hedge_side = None
                                        if side == 'Buy':
                                            # First calculate size difference of opposite position (if it doesn't exist then assume it as 0)
                                            for hedge_position in fetched_sessions:
                                                if hedge_position["symbol"] == symbol and hedge_position["side"] == 'Sell':
                                                    # Found opposite position
                                                    hedge_balancer_opposite_side_found = True
                                                    if size > float(hedge_position['size']):
                                                        target_hedge_side = 'Sell'
                                                        target_hedge_qty = round_step_size(size - float(hedge_position['size']),qty_step[symbol],min_trading_qty[symbol]) # calculate size difference for Hedge Balancer
                                                    elif float(hedge_position['size']) > size:
                                                        target_hedge_side = 'Buy'
                                                        target_hedge_qty = round_step_size(float(hedge_position['size']) - size,qty_step[symbol],min_trading_qty[symbol]) # calculate size difference for Hedge Balancer
                                            if not hedge_balancer_opposite_side_found:
                                                # No opposite position found 
                                                target_hedge_side = 'Sell'
                                                target_hedge_qty = round_step_size(size,qty_step[symbol],min_trading_qty[symbol])
                                                
                                        elif side == 'Sell':
                                            # First calculate size difference of opposite position (if it doesn't exist then assume it as 0)
                                            for hedge_position in fetched_sessions:
                                                if hedge_position["symbol"] == symbol and hedge_position["side"] == 'Buy':
                                                    # Found opposite position
                                                    hedge_balancer_opposite_side_found = True
                                                    if size > float(hedge_position['size']):
                                                        target_hedge_side = 'Buy'
                                                        target_hedge_qty = round_step_size(size - float(hedge_position['size']),qty_step[symbol],min_trading_qty[symbol]) # calculate size difference for Hedge Balancer
                                                    elif float(hedge_position['size']) > size:
                                                        target_hedge_side = 'Sell'
                                                        target_hedge_qty = round_step_size(float(hedge_position['size']) - size,qty_step[symbol],min_trading_qty[symbol]) # calculate size difference for Hedge Balancer
                                            if not hedge_balancer_opposite_side_found:
                                                # No opposite position found 
                                                target_hedge_side = 'Buy'
                                                target_hedge_qty = round_step_size(size,qty_step[symbol],min_trading_qty[symbol])
                                            
                                        # Execute Hedge
                                        timestamp_now = int(datetime.now().timestamp())
                                        last_balance_hedge_forced_timestamp = None
                                        if this_position_session["last_balance_hedge_forced"] is not None:
                                            # last_balance_hedge_forced_timestamp = int(datetime.strptime(str(this_position_session["last_balance_hedge_forced"]), '%Y-%m-%d %H:%M:%S'))
                                            last_balance_hedge_forced_timestamp = int(time.mktime(this_position_session["last_balance_hedge_forced"].timetuple()))
                                        if target_hedge_qty > 0 and (this_position_session["last_balance_hedge_forced"] is None or this_position_session["last_balance_hedge_forced"] == "" or timestamp_now >= last_balance_hedge_forced_timestamp + 10): # Make sure we never Hedge Balance Forced before or last time we did is at least 10 seconds ago to avoid double execution of the market order
                                            try:
                                                session.place_active_order(symbol=symbol, side=target_hedge_side, order_type="Market", qty=target_hedge_qty, time_in_force="GoodTillCancel", reduce_only=False, close_on_trigger=False)
                                                
                                                # Now update the Database
                                                mycursor_add_positions_hedges = mydb.cursor(dictionary=True)
                                                update_sql = "UPDATE positions_sessions SET last_balance_hedge_forced=NOW() WHERE api_key=%s AND api_secret=%s AND symbol=%s;"
                                                vals = (api_key, api_secret, symbol)
                                                mycursor_add_positions_hedges.execute(update_sql, vals)
                                                mydb.commit()
                                                
                                                # Now Log it
                                                log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " Equity Balancer Force-Hedged with Equity at "+str(equity)+"."
                                                print(log)
                                                with open("HEDGE_forced.txt", "a") as myfile:
                                                    myfile.write(log+'\n')
                                            except Exception:
                                                pass
                                                
                                            '''
                                            TODO: Support feature to place Balancer Hedge on the chart
                                            - When hedge balancer mode, check current_long_pos_size, current_short_pos_size compare with Database:
                                                - if different than whats stored in the fields, recalculate based on equity and store current_long_pos_size, current_short_pos_size, current_balancer_hedge_price.
                                                - if the same, just enforce the old 'balancer_hedge_price'.
                                            '''
                                
                                elif this_position_session['balanced_hedge'] == 0:
                                    # This position is fresh and never Hedge Balanced before
                                    # 1) Place Hedge Conditional Order or adjust it
                                    # Loop over all Hedges for this side position, and cancel every hedge: Not matching the target total balance hedge quantity OR out of allowed range
                                    # Keep the ones otherwise and count their total size
                                    
                                    target_tb_hedge_loss_value = wallet_balance * hedge_cap_ratio/100
                                    target_tb_hedge_ratio = (target_tb_hedge_loss_value * 100) / position_value # Could be used to place Hedge order on chart
                                    
                                    total_allowed_hedge_found = 0.0
                                    
                                    # First we set the qty and Hedge Type for the conditional order we are looking for or want to place if it doesn't exist
                                    target_hedge_balancer_type = False
                                    target_hedge_qty = 0
                                    target_hedge_side = None
                                    target_hedge_price = None
                                    if side == 'Buy':
                                        # First check if opposite position does not exist to place as a Hedge, as otherwise it should be a Hedge Balancer
                                        for hedge_position in fetched_sessions:
                                            if hedge_position["symbol"] == symbol and hedge_position["side"] == 'Sell':
                                                # Found opposite position
                                                target_hedge_balancer_type = True
                                                if size > float(hedge_position['size']):
                                                    target_hedge_side = 'Sell'
                                                    target_hedge_qty = round_step_size((size - float(hedge_position['size'])) * (hedge_pos_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol]) # calculate size difference for Hedge Balancer
                                                elif float(hedge_position['size']) > size:
                                                    target_hedge_side = 'Buy'
                                                    target_hedge_qty = round_step_size((float(hedge_position['size']) - size) * (hedge_pos_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol]) # calculate size difference for Hedge Balancer
                                                
                                        if not target_hedge_balancer_type:
                                            target_hedge_qty = round_step_size((size) * (hedge_pos_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])
                                            target_hedge_side = 'Sell'
                                            
                                    elif side == 'Sell':
                                        # First check if opposite position does not exist to place as a Hedge, as otherwise it should be a Hedge Balancer
                                        for hedge_position in fetched_sessions:
                                            if hedge_position["symbol"] == symbol and hedge_position["side"] == 'Buy':
                                                # Found opposite position
                                                target_hedge_balancer_type = True
                                                if size > float(hedge_position['size']):
                                                    target_hedge_side = 'Buy'
                                                    target_hedge_qty = round_step_size((size - float(hedge_position['size'])) * (hedge_pos_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol]) # calculate size difference for Hedge Balancer
                                                elif float(hedge_position['size']) > size:
                                                    target_hedge_side = 'Sell'
                                                    target_hedge_qty = round_step_size((float(hedge_position['size']) - size) * (hedge_pos_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol]) # calculate size difference for Hedge Balancer
                                        
                                        if not target_hedge_balancer_type:
                                            target_hedge_qty = round_step_size((size) * (hedge_pos_size_ratio / 100),qty_step[symbol],min_trading_qty[symbol])
                                            target_hedge_side = 'Buy'

               

                                    # Now we search if the Hedge conditional order exists and is valid (if it is Not a Balancer, as that one gets executed as immediate Market Order)
                                    if not target_hedge_balancer_type:
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
                                                    
                                        if target_hedge_side == 'Sell':
                                            target_hedge_price = round_to_tick(entry_price - ((target_tb_hedge_ratio/100) * entry_price), tick_size[symbol])
                                        elif target_hedge_side == 'Buy':
                                            target_hedge_price = round_to_tick(entry_price + ((target_tb_hedge_ratio/100) * entry_price), tick_size[symbol])
                                            
                                        try:
                                            fetched_hedge_conditional_orders = session.query_conditional_order(symbol=symbol)
                                        except Exception:
                                            pass
                                        if (fetched_hedge_conditional_orders):
                                            for hedge_conditional_order in fetched_hedge_conditional_orders["result"]:
                                                if symbol.endswith('USDT'): # USDT Perpetual
                                                    hedge_price = float(hedge_conditional_order['trigger_price'])
                                                    stop_order_id = hedge_conditional_order['stop_order_id']    
                                                else: # Inverse Perpetuals or Futures
                                                    hedge_price = float(hedge_conditional_order['stop_px'])
                                                    stop_order_id = hedge_conditional_order['order_id']
                                                    
                                                    
                                                if hedge_conditional_order['order_link_id'].startswith('CryptoGenieHedge'):
                                                    if target_hedge_side == 'Sell':
                                                                        
                                                        if hedge_conditional_order['side'] == target_hedge_side and hedge_price < entry_price and hedge_price >= target_hedge_price and float(hedge_conditional_order['qty']) == target_hedge_qty and hedge_conditional_order['close_on_trigger'] == False and hedge_conditional_order['reduce_only'] == False and hedge_conditional_order['order_type'] == 'Market' and hedge_conditional_order['order_status'] == 'Untriggered':
                                                            # Valid Hedge found inside the allowed range and correct size, keep it
                                                            total_allowed_hedge_found += float(hedge_conditional_order['qty'])
                                                        else:
                                                            # Invalid Hedge found outside the allowed range or incorrect size, so remove it
                                                            try:
                                                                session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id) 
                                                            except Exception:
                                                                pass
                                                                
                                                            try:
                                                                mycursor.execute("DELETE FROM positions_hedges WHERE stop_order_id='"+stop_order_id+"' and api_key='"+api_key+"' AND api_secret='"+api_secret+"'")
                                                                mydb.commit()
                                                            except Exception:
                                                                pass
                                                                

                                                    elif target_hedge_side == 'Buy':
                                                                        
                                                        if hedge_conditional_order['side'] == target_hedge_side and hedge_price > entry_price and hedge_price <= target_hedge_price and float(hedge_conditional_order['qty']) == target_hedge_qty and hedge_conditional_order['close_on_trigger'] == False and hedge_conditional_order['reduce_only'] == False and hedge_conditional_order['order_type'] == 'Market' and hedge_conditional_order['order_status'] == 'Untriggered':
                                                            # Valid Hedge found inside the allowed range and correct size, keep it
                                                            total_allowed_hedge_found += float(hedge_conditional_order['qty'])
                                                        else:
                                                            # Invalid Hedge found outside the allowed range or incorrect size, so remove it
                                                            try:
                                                                session.cancel_conditional_order(symbol=symbol, stop_order_id=stop_order_id) 
                                                            except Exception:
                                                                pass
                                                                
                                                            try:
                                                                mycursor.execute("DELETE FROM positions_hedges WHERE stop_order_id='"+stop_order_id+"' and api_key='"+api_key+"' AND api_secret='"+api_secret+"'")
                                                                mydb.commit()
                                                            except Exception:
                                                                pass
                     
                                        if total_allowed_hedge_found == 0.0:
                                            # We couldn't find a Hedge in the allowed range, add 1 Hedge conditional order with target size, at the correct level
                                            # Place Hedge (conditional order)
                                            if target_hedge_qty > 0: 
                                                try:
                                                    hedge_order_result = session.place_conditional_order(order_link_id="CryptoGenieHedge#"+str(int(datetime.now().timestamp())), symbol=symbol, order_type="Market", reduce_only=False, close_on_trigger=False, side= ("Sell" if side == 'Buy' else "Buy"), qty=target_hedge_qty, trigger_by="MarkPrice", stop_px=target_hedge_price, base_price=last_price, time_in_force="GoodTillCancel")
                                                    #print(hedge_order_result)
                                                    log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " Total Balance Hedge placed at: "+str(target_hedge_price)+" (" + str(hedge_pos_size_ratio) + "% of position size = " + str(target_hedge_qty) + ", " + str(hedge_cap_ratio) + "% of total balance)."
                                                    print(log)
                                                    with open("HEDGE_protected.txt", "a") as myfile:
                                                        myfile.write(log+'\n')
                                                except Exception:
                                                    pass
                                                    
                                                try:
                                                    # Now add it to the Database
                                                    mycursor_add_positions_hedges = mydb.cursor(dictionary=True)
                                                    insert_sql = "INSERT INTO positions_hedges (api_key, api_secret, symbol, side, order_link_id, stop_order_id, price, size) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE order_link_id = %s, stop_order_id = %s, price=%s, size=%s, last_updated=NOW();"
                                                    vals = (api_key, api_secret, symbol, ("Sell" if side == 'Buy' else "Buy"), "CryptoGenieHedge#"+str(int(datetime.now().timestamp())), hedge_order_result["result"]["stop_order_id"], str(target_hedge_price), str(target_hedge_qty), "CryptoGenieHedge#"+str(int(datetime.now().timestamp())), hedge_order_result["result"]["stop_order_id"], str(target_hedge_price), str(target_hedge_qty))
                                                    mycursor_add_positions_hedges.execute(insert_sql, vals)
                                                    mydb.commit()
                                                except Exception:
                                                    pass
             
                            # Always check if Hedge SL is reached for the Hedging Session (since initial equity when we started the session) to force close both LONG and SHORT immediately
                            # To avoid the wrong tight total balance loss as account grows bigger (to protect gains), we will need to use the larger value between highest_equity and last_balanced_equity.
                            last_balanced_equity = 0 if this_position_session['last_balanced_equity'] is None else float(this_position_session['last_balanced_equity'])
                            highest_equity = 0 if this_position_session['highest_equity'] is None else float(this_position_session['highest_equity'])
                            target_tb_hedge_sl_loss_value = (highest_equity if highest_equity > last_balanced_equity else last_balanced_equity) * hedge_sl_static_cap_ratio/100
                            # print('Current Equity: ' + str(equity))
                            # print('target_tb_hedge_sl_loss_value = ' + str(target_tb_hedge_sl_loss_value))
                            # print('Calculation balanced used = ' + str((highest_equity if highest_equity > last_balanced_equity else last_balanced_equity) - target_tb_hedge_sl_loss_value))
                            if (equity < (highest_equity if highest_equity > last_balanced_equity else last_balanced_equity) - target_tb_hedge_sl_loss_value):
                                # Execute emergency market exit SL for both sides
                                for hedge_position in fetched_sessions:
                                    if hedge_position["symbol"] == symbol and hedge_position["side"] == 'Buy':
                                        # Found opposite position
                                        hedge_close_size = float(hedge_position['size'])
                                        target_hedge_side = 'Buy'
                                        
                                        try:
                                            session.place_active_order(position_idx=position_idx, symbol=symbol, side="Sell", order_type="Market", qty=hedge_close_size, time_in_force="GoodTillCancel", reduce_only=True, close_on_trigger=True)
                                            log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " LONG Total Balance Hedge Force-Stopped."
                                            print(log)
                                            with open("HEDGE_SL_forced.txt", "a") as myfile:
                                                myfile.write(log+'\n')
                                        except Exception:
                                            pass
                                            
                                            
                                    if hedge_position["symbol"] == symbol and hedge_position["side"] == 'Sell':
                                        # Found opposite position
                                        hedge_close_size = float(hedge_position['size'])
                                        target_hedge_side = 'Sell'
                                        
                                        try:
                                            session.place_active_order(position_idx=position_idx, symbol=symbol, side="Buy", order_type="Market", qty=hedge_close_size, time_in_force="GoodTillCancel", reduce_only=True, close_on_trigger=True)
                                            log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + symbol + " SHORT Total Balance Hedge Force-Stopped."
                                            print(log)
                                            with open("HEDGE_SL_forced.txt", "a") as myfile:
                                                myfile.write(log+'\n')
                                        except Exception:
                                            pass
                                # Clear the Hedge Session from the Database immediatly
                                try:
                                    mycursor.execute("DELETE FROM positions_sessions WHERE api_key = '"+api_key+"' AND api_secret = '"+api_secret+"' AND symbol = "+symbol)
                                    mydb.commit()
                                except Exception:
                                    pass    
             
        #######################################################
        # Enforce Smart Dynamic Entries using Crypto Genie's smart algorithm
        #######################################################
        
        if enforce_smart_dynamic_entries == True and enable_db_features == True:
            for smart_dynamic_entries_symbol, smart_dynamic_entries_indicator in smart_dynamic_entries.items(): # Do this for all the coins and their defined indicators/timeframe
                '''
                We need to measure the Fibonacci Retracement for various time windows to find key Swing Highs and Swing Lows without loosing sight of bigger time window ones in case a spike happens.
                The higher the timeframe, the stronger the weight is in terms of position sizing. Also, each level will have: Fib 100% level (invalidates the wave and could be a Stop Loss line) + 2 zones: 'Zone 1' (the golden pocket) and 'Zone 2'. Zone 2 is stronger than Zone 1. We only Open Orders at these zones, nowhere else.
                The Order Size at each Timewindow is based on the Weight of it, as follows:
                Genie Zone Strength (GZS) = Timewindow # + Fib Zone Range Max (the deeper the retrace, the higher the value gets)
                Genie Zone Strength Index (GZSI) = GZS / Max(GZS)
                So we need to pull the kline data to cover each window. NOTE: ByBit max window is 200 units
                NOTE: We consider a Zone invalid once price has broken its further border. So we lookback from current price back towards the index of the recent pivot where the Retracement was drawn to find that out.
                '''
                final_decimals_count = str(tick_size[smart_dynamic_entries_symbol])[::-1].find('.') # Tick Size number of decimals
                pagesize = 200
                now = datetime.utcnow()
                unixtime = calendar.timegm(now.utctimetuple())
                since1min = unixtime - 60 * 1 * pagesize
                since5min = unixtime - 60 * 5 * pagesize
                since15min = unixtime - 60 * 15 * pagesize
                since60min = unixtime - 60 * 60 * pagesize
                since240min = unixtime - 60 * 240 * pagesize
                since720min = unixtime - 60 * 720 * pagesize
                response1min=session.query_kline(symbol=smart_dynamic_entries_symbol, interval=1, **{'from':since1min})['result']
                response5min=session.query_kline(symbol=smart_dynamic_entries_symbol, interval=5, **{'from':since5min})['result']
                response15min=session.query_kline(symbol=smart_dynamic_entries_symbol, interval=15, **{'from':since15min})['result']
                response60min=session.query_kline(symbol=smart_dynamic_entries_symbol, interval=60, **{'from':since60min})['result']
                response240min=session.query_kline(symbol=smart_dynamic_entries_symbol, interval=240, **{'from':since240min})['result']
                response720min=session.query_kline(symbol=smart_dynamic_entries_symbol, interval=720, **{'from':since720min})['result']
                df1min = pd.DataFrame(response1min)
                df5min = pd.DataFrame(response5min)
                df15min = pd.DataFrame(response15min)
                df60min = pd.DataFrame(response60min)
                df240min = pd.DataFrame(response240min)
                df720min = pd.DataFrame(response720min)

                # First we find the Swing High and Swing Low of the various timeframes. We will loop and measure them all
                all_timewindows_fib_levels = {}
                timewindow = 0
                # while timewindow <= 12:
                #     if timewindow == 0:
                #         df = df5min.tail(48)
                #         chartTitle = smart_dynamic_entries_symbol + ': Last 4 hours'
                #     elif timewindow == 1:
                #         df = df5min.tail(60)
                #         chartTitle = smart_dynamic_entries_symbol + ': Last 5 hours'
                #     elif timewindow == 2:
                #         df = df5min.tail(72)
                #         chartTitle = smart_dynamic_entries_symbol + ': Last 6 hours'
                #     elif timewindow == 3:
                #         df = df5min.tail(84)
                #         chartTitle = smart_dynamic_entries_symbol + ': Last 7 hours'
                #     elif timewindow == 4:
                #         df = df5min.tail(96)
                #         chartTitle = smart_dynamic_entries_symbol + ': Last 8 hours'
                #     elif timewindow == 5:
                #         df = df5min.tail(192)
                #         chartTitle = smart_dynamic_entries_symbol + ': Last 16 hours'
                #     elif timewindow == 6:
                #         df = df15min.tail(96)
                #         chartTitle = smart_dynamic_entries_symbol + ': Last 1 day'
                #     elif timewindow == 7:
                #         df = df15min.tail(192)
                #         chartTitle = smart_dynamic_entries_symbol + ': Last 2 days'
                #     elif timewindow == 8:
                #         df = df60min.tail(168)
                #         chartTitle = smart_dynamic_entries_symbol + ': Last 1 week'
                #     elif timewindow == 9:
                #         df = df240min.tail(84)
                #         chartTitle = smart_dynamic_entries_symbol + ': Last 2 weeks'
                #     elif timewindow == 10:
                #         df = df240min.tail(180)
                #         chartTitle = smart_dynamic_entries_symbol + ': Last 1 month'
                #     elif timewindow == 11:
                #         df = df720min.tail(120)
                #         chartTitle = smart_dynamic_entries_symbol + ': Last 2 months'
                #     elif timewindow == 12:
                #         df = df720min.tail(180)
                #         chartTitle = smart_dynamic_entries_symbol + ': Last 3 months'
                
                while timewindow <= 22:
                    if timewindow == 0:
                        df = df1min.tail(30)
                        chartTitle = smart_dynamic_entries_symbol + ': Last 30 minutes'
                    elif timewindow == 1:
                        df = df1min.tail(45)
                        chartTitle = smart_dynamic_entries_symbol + ': Last 45 minutes'
                    elif timewindow == 2:
                        df = df1min.tail(60)
                        chartTitle = smart_dynamic_entries_symbol + ': Last 1 hour'
                    elif timewindow == 3:
                        df = df1min.tail(120)
                        chartTitle = smart_dynamic_entries_symbol + ': Last 2 hours'
                    elif timewindow == 4:
                        df = df1min.tail(180)
                        chartTitle = smart_dynamic_entries_symbol + ': Last 3 hours'
                    elif timewindow == 5:
                        df = df5min.tail(48)
                        chartTitle = smart_dynamic_entries_symbol + ': Last 4 hours'
                    elif timewindow == 6:
                        df = df5min.tail(60)
                        chartTitle = smart_dynamic_entries_symbol + ': Last 5 hours'
                    elif timewindow == 7:
                        df = df5min.tail(72)
                        chartTitle = smart_dynamic_entries_symbol + ': Last 6 hours'
                    elif timewindow == 8:
                        df = df5min.tail(84)
                        chartTitle = smart_dynamic_entries_symbol + ': Last 7 hours'
                    elif timewindow == 9:
                        df = df5min.tail(96)
                        chartTitle = smart_dynamic_entries_symbol + ': Last 8 hours'
                    elif timewindow == 10:
                        df = df5min.tail(108)
                        chartTitle = smart_dynamic_entries_symbol + ': Last 9 hours'
                    elif timewindow == 11:
                        df = df5min.tail(120)
                        chartTitle = smart_dynamic_entries_symbol + ': Last 10 hours'
                    elif timewindow == 12:
                        df = df5min.tail(132)
                        chartTitle = smart_dynamic_entries_symbol + ': Last 11 hours'
                    elif timewindow == 13:
                        df = df5min.tail(144)
                        chartTitle = smart_dynamic_entries_symbol + ': Last 12 hours'
                    elif timewindow == 14:
                        df = df5min.tail(156)
                        chartTitle = smart_dynamic_entries_symbol + ': Last 13 hours'
                    elif timewindow == 15:
                        df = df5min.tail(168)
                        chartTitle = smart_dynamic_entries_symbol + ': Last 14 hours'
                    elif timewindow == 16:
                        df = df5min.tail(180)
                        chartTitle = smart_dynamic_entries_symbol + ': Last 15 hours'
                    elif timewindow == 17:
                        df = df5min.tail(192)
                        chartTitle = smart_dynamic_entries_symbol + ': Last 16 hours'
                    elif timewindow == 18:
                        df = df15min.tail(96)
                        chartTitle = smart_dynamic_entries_symbol + ': Last 1 day'
                    elif timewindow == 19:
                        df = df15min.tail(192)
                        chartTitle = smart_dynamic_entries_symbol + ': Last 2 days'
                    elif timewindow == 20:
                        df = df60min.tail(168)
                        chartTitle = smart_dynamic_entries_symbol + ': Last 1 week'
                    elif timewindow == 21:
                        df = df240min.tail(84)
                        chartTitle = smart_dynamic_entries_symbol + ': Last 2 weeks'
                    elif timewindow == 22:
                        df = df240min.tail(180)
                        chartTitle = smart_dynamic_entries_symbol + ': Last 1 month'
                
                        
                    df.reset_index(drop=True, inplace=True)
                        
                    highest_swing = -1
                    lowest_swing = -1
                    for i in range(1,df.shape[0]-1):
                      if df['high'][i] > df['high'][i-1] and df['high'][i] > df['high'][i+1] and (highest_swing == -1 or df['high'][i] > df['high'][highest_swing]):
                        highest_swing = i

                      if df['low'][i] < df['low'][i-1] and df['low'][i] < df['low'][i+1] and (lowest_swing == -1 or df['low'][i] < df['low'][lowest_swing]):
                        lowest_swing = i
                    fib_ratios = [0.616, 0.66, 0.786 , 0.818, 1]
                    colors = ["#00ce09","#00ce09","#20cde3","#20cde3", "#787b86"]
                    chart_levels = []

                    max_level = df['high'][highest_swing]
                    min_level = df['low'][lowest_swing]

                    # Now we draw the Fibonacci Retracement of the Swings
                    if highest_swing > lowest_swing: # Uptrend
                        timewindow_order_side = 'Buy'
                        for fib_ratio in fib_ratios:
                            # Check from current price till highest_swing if price ever went below the further border of the Zone, mark it as inactive
                            current_fib_zone_active = True
                            df_recent = df.tail(df.shape[0]-1 - highest_swing)['close']
                            if (fib_ratio == fib_ratios[0] or fib_ratio == fib_ratios[1]) and df_recent[df_recent < (max_level - (max_level-min_level)*fib_ratios[1])].count() > 0:
                                current_fib_zone_active = False
                            elif (fib_ratio == fib_ratios[2] or fib_ratio == fib_ratios[3]) and df_recent[df_recent < (max_level - (max_level-min_level)*fib_ratios[3])].count() > 0:
                                current_fib_zone_active = False
                            chart_levels.append( {'fib_ratio': fib_ratio, 'price_level': max_level - (max_level-min_level)*fib_ratio, 'active': current_fib_zone_active} )
                        
                    else: # Downtrend
                        timewindow_order_side = 'Sell'
                        for fib_ratio in fib_ratios:
                            # Check from current price till lowest_swing if price ever went above the further border of the Zone, mark it as inactive
                            current_fib_zone_active = True
                            df_recent = df.tail(df.shape[0]-1 - lowest_swing)['close']
                            if (fib_ratio == fib_ratios[0] or fib_ratio == fib_ratios[1]) and df_recent[df_recent > (min_level + (max_level-min_level)*fib_ratios[1])].count() > 0:
                                current_fib_zone_active = False
                            elif (fib_ratio == fib_ratios[2] or fib_ratio == fib_ratios[3]) and df_recent[df_recent > (min_level + (max_level-min_level)*fib_ratios[3])].count() > 0:
                                current_fib_zone_active = False
                            chart_levels.append( {'fib_ratio': fib_ratio, 'price_level': min_level + (max_level-min_level)*fib_ratio, 'active': current_fib_zone_active} )
                    
                    # Add this Timewindow levels to the All Timewindows list
                    all_timewindows_fib_levels[timewindow] = {'timewindow_order_side': timewindow_order_side, 'chart_levels': chart_levels}
                    
                    '''
                    # Now Plot
                    plt.rcParams['figure.figsize'] = [12, 7]
                    plt.rc('font', size=14)
                    plt.ylabel(quote_currency[smart_dynamic_entries_symbol])
                    plt.title(chartTitle)
                    plt.plot(df['close'], color='black')
                    start_date = df.index[min(highest_swing,lowest_swing)]
                    end_date = df.shape[0]-1

                    i=0
                    for chart_level in chart_levels:
                      color = colors[i]
                      if not chart_level['active']:
                        color = "#787b86"
                      plt.hlines(chart_level['price_level'],start_date, end_date,label="{:.1f}%".format(float(chart_level['fib_ratio'])*100),colors=color, linestyles="dashed")
                      i += 1
                    plt.savefig('chart_timewindow'+str(timewindow)+'.png')
                    plt.clf()
                    '''
                    
                    
                    timewindow += 1 # Move to next Timewindow
                
                gzsi_buy = 0 # Are we in a Buying zone on any timeframe? Store the strongest gzsi for it across all timeframes (if more than one)
                gzsi_sell = 0 # Are we in a Selling zone on any timeframe? Store the strongest gzsi for it across all timeframes (if more than one)
                for current_timewindow in reversed(range(len(all_timewindows_fib_levels))): # We give priority over bigger timeframe levels as they have more weight, so we go reversed
                    fib_0_price_level = ""
                    fib_0_active = True
                    fib_1_price_level = ""
                    fib_1_active = True
                    fib_2_price_level = ""
                    fib_2_active = True
                    fib_3_price_level = ""
                    fib_3_active = True
                    fib_4_price_level = ""
                    fib_4_active = True
                    for current_chart_levels in all_timewindows_fib_levels[current_timewindow]["chart_levels"]:
                        if current_chart_levels['fib_ratio'] == fib_ratios[0]:
                            fib_0_price_level = current_chart_levels['price_level']
                            fib_0_active = current_chart_levels['active']
                        elif current_chart_levels['fib_ratio'] == fib_ratios[1]:
                            fib_1_price_level = current_chart_levels['price_level']
                            fib_1_active = current_chart_levels['active']
                        elif current_chart_levels['fib_ratio'] == fib_ratios[2]:
                            fib_2_price_level = current_chart_levels['price_level']
                            fib_2_active = current_chart_levels['active']
                        elif current_chart_levels['fib_ratio'] == fib_ratios[3]:
                            fib_3_price_level = current_chart_levels['price_level']
                            fib_3_active = current_chart_levels['active']
                        elif current_chart_levels['fib_ratio'] == fib_ratios[4]:
                            fib_4_price_level = current_chart_levels['price_level']
                            fib_4_active = current_chart_levels['active']
                    
                    # Fib Retracement could be from Bottom to Top or Top to Bottom, so levels could be flipped, thus we use min and max to make it easier to find the range
                    if fib_1_active and (min(fib_0_price_level, fib_1_price_level) < df['close'].iloc[-1] < max(fib_0_price_level, fib_1_price_level)):
                        # Current Price is in Zone 1, and it is still Active (not broken yet), signal acceleration of Order Sizing and more room for Leverage
                        gzs = current_timewindow + fib_ratios[1]
                        gzsi = gzs / len(all_timewindows_fib_levels)
                        if all_timewindows_fib_levels[current_timewindow]["timewindow_order_side"] == 'Buy':
                            gzsi_buy = gzsi
                        elif all_timewindows_fib_levels[current_timewindow]["timewindow_order_side"] == 'Sell':
                            gzsi_sell = gzsi
                    elif fib_3_active and (min(fib_2_price_level, fib_3_price_level) < df['close'].iloc[-1] < max(fib_2_price_level, fib_3_price_level)): 
                        # Current Price is in Zone 2, and it is still Active (not broken yet)), signal acceleration of Order Sizing and more room for Leverage
                        gzs = current_timewindow + fib_ratios[3]
                        gzsi = gzs / len(all_timewindows_fib_levels)
                        if all_timewindows_fib_levels[current_timewindow]["timewindow_order_side"] == 'Buy':
                            gzsi_buy = gzsi
                        elif all_timewindows_fib_levels[current_timewindow]["timewindow_order_side"] == 'Sell':
                            gzsi_sell = gzsi
                        
                    # TODO: If current price passed the fib_0_price_level then take some losses as wave is invalidated
                
                # Now, we will implement Mean Reversion strategy using the defined moving indicator: we will execute Open Orders when we are relatively extended away from the indicator
                # And now with the Fibonacci Zones we will be able to accelerate the Open Orders if we are also in one of the zones of interest (Confluence: Extended away from the indicator AND in a Fibonacci Retracement Zone)
                mean_reversion_interval = int(list(smart_dynamic_entries_indicator.items())[0][0])
                # Pull the kline data for the interval (timeframe). Maximum allowed kline data is pagesize
                now = datetime.utcnow()
                unixtime = calendar.timegm(now.utctimetuple())
                since = unixtime - 60 * mean_reversion_interval * pagesize
                response=session.query_kline(symbol=smart_dynamic_entries_symbol, interval=str(mean_reversion_interval), **{'from':since})['result']
                df = pd.DataFrame(response)
                dynamic_level = list(smart_dynamic_entries_indicator.items())[0][1]
                ordertype = dynamic_level.split('#')[1]
                indicator = dynamic_level.split('#')[0].split('_')[0]
                length = int(dynamic_level.split('#')[0].split('_')[1])
                if indicator == 'ema':
                    indicator_data = ta.ema(df['close'].astype(float, errors = 'raise'), length=length)
                    current_indicator_value = indicator_data.iloc[-1]
                elif indicator == 'bbands':
                    indicator_data = ta.bbands(df['close'].astype(float, errors = 'raise'), length=length).filter(like='BBM').iloc[:, 0] # Use Median of the Bollinger Band
                    current_indicator_value = indicator_data.iloc[-1]

                # Genie Index
                price_diff = df['close'] - indicator_data
                indicator_data_distance_ratio = (price_diff.abs() / indicator_data) # Ratio away from the EMA
                
                indicator_data_distance_ratio_average = indicator_data_distance_ratio.mean()*100 # We find the Mean of the distance ratios
                genie_index = ta.rsi(indicator_data_distance_ratio, default_smart_dynamic_entries_rsi_length)
                current_genie_index = genie_index.iloc[-1]
                
                # Are we looking for Buy or Sell?
                if float(price_diff.iloc[-1]) > 0: # Price is above the indicator, looking for SHORT entries
                    side = 'Sell'
                elif float(price_diff.iloc[-1]) < 0: # Price is below the indicator, looking for LONG entries
                    side = 'Buy'
                
                # Setup the GZSI based on the order side we are interested in
                gzsi_used = 0
                if side == 'Buy':
                    gzsi_used = gzsi_buy
                elif side == 'Sell':
                    gzsi_used = gzsi_sell
                
                # Fetch latest tickers
                try:
                    fetched_latest_tickers = session.latest_information_for_symbol(symbol=smart_dynamic_entries_symbol)['result']
                except Exception:
                    pass
                    
                if(fetched_latest_tickers):
                    for ticker in fetched_latest_tickers:
                        if ticker['symbol'] == smart_dynamic_entries_symbol:
                            last_price = float(ticker['last_price'])
                            mark_price = float(ticker['mark_price'])
                
                # Fetch Wallet Balance and calculate order size
                if quote_currency[smart_dynamic_entries_symbol] == "USDT":
                    wallet_balance = session.get_wallet_balance(coin="USDT")["result"]["USDT"]["wallet_balance"]
                    available_balance = session.get_wallet_balance(coin="USDT")["result"]["USDT"]["available_balance"]
                    order_size = wallet_balance * default_smart_dynamic_entries_wallet_balance_order_ratio * (current_genie_index/default_smart_dynamic_entries_level_1_from) # We are doing this Genie Index multiplier as a way to accelerate buying (order size) as we enter more extended ratios
                    order_size = order_size * (1 + gzsi_used)  # We also use the gzsi (if there is one for the order size we are interested in) to accelerate Open Orders the more we are in stronger zones
                    order_size = order_size / last_price # Convert it into the Base Currency
                    order_size = round_step_size(order_size,qty_step[smart_dynamic_entries_symbol],min_trading_qty[smart_dynamic_entries_symbol])
                else:
                    wallet_balance = session.get_wallet_balance(coin=base_currency[smart_dynamic_entries_symbol])["result"][base_currency[smart_dynamic_entries_symbol]]["wallet_balance"]
                    available_balance = session.get_wallet_balance(coin=base_currency[smart_dynamic_entries_symbol])["result"][base_currency[smart_dynamic_entries_symbol]]["available_balance"]
                    order_size = wallet_balance * default_smart_dynamic_entries_wallet_balance_order_ratio * (current_genie_index/default_smart_dynamic_entries_level_1_from) # We are doing this Genie Index multiplier as a way to accelerate buying (order size) as we enter more extended ratios
                    order_size = order_size * (1 + gzsi_used)  # We also use the gzsi (if there is one for the order size we are interested in) to accelerate Open Orders the more we are in stronger zones
                    order_size = order_size * last_price # Convert it into the Base Currency
                    order_size = round_step_size(order_size,qty_step[smart_dynamic_entries_symbol],min_trading_qty[smart_dynamic_entries_symbol])

                # Calculate unrealised_pnl of the position


                
                # Now we check the Effective Leverage
                effective_leverage = 0 # If no position available, it means this is zero
                
                # Do we have an already active position for the side we are looking to add to?
                entry_price = False
                for position in fetched_sessions:
                    entry_price = float(position["entry_price"])
                    if position["symbol"] == smart_dynamic_entries_symbol and position["side"] == side:
                        # Find the Effective Leverage for the active position of the symbol
                        if side == 'Buy':
                            # unrealised_pnl_calculated is negative if in loss
                            unrealised_pnl_calculated = size * ((mark_price -  entry_price))
                        elif side == 'Sell':
                            # unrealised_pnl_calculated is negative if in loss
                            unrealised_pnl_calculated = size * ((entry_price -  mark_price))

                        if unrealised_pnl_calculated >= 0: # If unrealised profits exist, we use it in the Effective Leverage calculation, otherwise no
                            effective_leverage = position['position_value'] / ((position['position_value']/position['leverage']) + available_balance + unrealised_pnl_calculated)
                        else:
                            effective_leverage= position['position_value'] / ((position['position_value']/position['leverage']) + available_balance)
                
                # Now we check if we can execute orders within defined ranges according to the strategy
                '''
                print('Distance Ratio: '+str(indicator_data_distance_ratio.iloc[-1] * 100))
                print('Distance Ratio Average: '+str(indicator_data_distance_ratio_average/2))
                if indicator_data_distance_ratio.iloc[-1] * 100 > indicator_data_distance_ratio_average/2:
                    print('Passed')
                print('Genie Index: '+str(current_genie_index))
                
                # Now Plot
                plt.rcParams['figure.figsize'] = [12, 7]
                plt.rc('font', size=14)
                plt.title("Price")
                plt.plot(df['close'], color='black', label = "Price")
                plt.plot(indicator_data, color='orange', label = "EMA")
                plt.savefig('./charts/'+smart_dynamic_entries_symbol+'_price.png')
                plt.clf()
                
                # Now Plot
                plt.rcParams['figure.figsize'] = [12, 7]
                plt.rc('font', size=14)
                plt.title("EMA Distance Ratio")
                plt.plot(indicator_data_distance_ratio *100, color='blue')
                plt.savefig('./charts/'+smart_dynamic_entries_symbol+'_ratio.png')
                plt.clf()
                
                # Now Plot
                plt.rcParams['figure.figsize'] = [12, 7]
                plt.rc('font', size=14)
                plt.title("Genie Index")
                plt.plot(genie_index, color='red')
                plt.savefig('./charts/'+smart_dynamic_entries_symbol+'_genie.png')
                plt.clf()
                
                
                # print(smart_dynamic_entries_symbol + " -> " + 'Mean: ' + str(indicator_data_distance_ratio_average) + ', Genie Index: ' + str(current_genie_index) + ', Buy GZSI: ' + str(gzsi_buy) + ', Sell GZSI: ' + str(gzsi_sell) + ', Used GZSI: ' + str(gzsi_used))
                '''
                # Execute Orders to add to active position (or open a new one) as needed
                # We will do it in the form of multiple Limit (PostOnly) orders
                # IF an active order already exists in the Order Book with our Bot custom Order ID:
                #   IF price retraced, we chase the price (replace order)
                # ELSE:
                #   Add new order
                # Otherwise, by default, no order should be placed on the order book if we are outside the Genie Index zones (remove any pending ones)
                # TODO: instead of 1 order, spray 10 by finding the minimum contract size for the asset then using that to calculate 1/10 of total desired order size each time

                # Select the latest Order Linked ID stored in the Database (if it exists)                     
                mycursor = mydb.cursor(dictionary=True)
                mycursor.execute("SELECT * FROM linked_orders WHERE api_key='"+api_key+"' AND api_secret='"+api_secret+"' AND symbol='"+smart_dynamic_entries_symbol+"' AND side='"+side+"'")
                linked_orders_result = mycursor.fetchall()

                target_effective_leverage = -1
                if default_smart_dynamic_entries_level_1_from <= current_genie_index < default_smart_dynamic_entries_level_1_to:
                    target_effective_leverage = default_smart_dynamic_entries_level_1_max_effective_leverage * (1 + gzsi_used)
                elif default_smart_dynamic_entries_level_2_from <= current_genie_index < default_smart_dynamic_entries_level_2_to:
                    target_effective_leverage = default_smart_dynamic_entries_level_2_max_effective_leverage * (1 + gzsi_used)
                elif default_smart_dynamic_entries_level_3_from <= current_genie_index < default_smart_dynamic_entries_level_3_to:
                    target_effective_leverage = default_smart_dynamic_entries_level_3_max_effective_leverage * (1 + gzsi_used)
                elif current_genie_index >= default_smart_dynamic_entries_level_4_from:
                    target_effective_leverage = default_smart_dynamic_entries_level_4_max_effective_leverage * (1 + gzsi_used)
                
                if target_effective_leverage != -1:
                    # We are in a Genie Index zone of interest
                    if indicator_data_distance_ratio.iloc[-1] * 100 > (indicator_data_distance_ratio_average * default_smart_dynamic_entries_minimum_average_distance_multiplier) and effective_leverage < target_effective_leverage:
                        # We are indeed ready to start executing Orders as the current Effective Leverage has room to add more
                        if ordertype == 'Market':
                            # Market order execute immediately
                            try:
                                session.place_active_order(symbol=smart_dynamic_entries_symbol, side=side, order_type="Market", qty=order_size, time_in_force="GoodTillCancel", reduce_only=False, close_on_trigger=False)
                                log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + smart_dynamic_entries_symbol + " Auto Trader Bot placing "+ordertype+" Open Order -> Genie Index @ " + str(current_genie_index) + " and GZSI @ " + str(gzsi_used) + ": "+ side + " " + str(order_size) + " Effective Leverage: " + str(effective_leverage) + "."
                                print(log)
                                with open("Genie_AutoTrader.txt", "a") as myfile:
                                    myfile.write(log+'\n')
                            except Exception:
                                pass
                        elif ordertype == 'Limit':
                            if side == 'Buy':
                                chaser_price=round_to_tick(last_price - (float(tick_size[smart_dynamic_entries_symbol]) * default_smart_dynamic_entries_price_chaser_minimum_ticks), tick_size[smart_dynamic_entries_symbol])
                            elif side == 'Sell':
                                chaser_price=round_to_tick(last_price + (float(tick_size[smart_dynamic_entries_symbol]) * default_smart_dynamic_entries_price_chaser_minimum_ticks), tick_size[smart_dynamic_entries_symbol])
                            if mycursor.rowcount == 0:
                                # No Linked Order exists in the Database, Create a new order with a new order_link_id and store it in the Database
                                # Generate order_link_id
                                order_link_id = "cg_"+str(int(time.time()))+"_"+get_random_string(10)
                                try:
                                    session.place_active_order(symbol=smart_dynamic_entries_symbol, order_link_id=order_link_id, side=side, order_type="Limit", qty=order_size, price=chaser_price, time_in_force="PostOnly", reduce_only=False, close_on_trigger=False)
                                    log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + smart_dynamic_entries_symbol + " Auto Trader Bot placing "+ordertype+" Open Order -> Genie Index @ " + str(current_genie_index) + " and GZSI @ " + str(gzsi_used) + ": "+ side + " " + str(order_size) + " Effective Leverage: " + str(effective_leverage) + "."
                                    print(log)
                                    with open("Genie_AutoTrader.txt", "a") as myfile:
                                        myfile.write(log+'\n')
                                except Exception:
                                    pass
                                else:
                                    # No exception occured
                                    # Now add it to the Database
                                    insert_sql = "INSERT INTO linked_orders (order_link_id, api_key, api_secret, symbol, side, order_type, price, qty, time_in_force) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'PostOnly')"
                                    vals = (order_link_id, api_key, api_secret, smart_dynamic_entries_symbol, side, ordertype, chaser_price, order_size)
                                    try:
                                        mycursor.execute(insert_sql, vals)
                                        mydb.commit()
                                    except Exception:
                                        pass
                            else:
                                # Linked Order exists in Database
                                for linked_order in linked_orders_result:
                                    # Check if order exists on the Order Book and check if price retraced from existing order price, and if yes replace it with a new one
                                    try:
                                        fetched_active_order = session.query_active_order(symbol=smart_dynamic_entries_symbol, order_link_id=linked_order['order_link_id'])
                                    except Exception:
                                        pass
                                    else:
                                        # No exception occured
                                        if(fetched_active_order["result"]["order_status"] == 'Cancelled' or fetched_active_order["result"]["order_status"] == 'Filled'):
                                            try:
                                                mycursor.execute("DELETE FROM linked_orders WHERE order_link_id='"+linked_order['order_link_id']+"'")
                                                mydb.commit()
                                            except Exception:
                                                pass
                                        else:
                                            active_order = fetched_active_order["result"]
                                            # Order already exists in the Order Book, check if price retraced to chase otherwise do nothing
                                            if (side == "Buy" and active_order['price'] < chaser_price) or (side == "Sell" and active_order['price'] > chaser_price):
                                                # Replace it with the new ticker price (chase the retrace)
                                                try:
                                                    session.replace_active_order(symbol=smart_dynamic_entries_symbol, order_link_id=linked_order['order_link_id'], p_r_qty=order_size , p_r_price=chaser_price)
                                                    log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + (log_label + ": " if log_label != "" else "") + smart_dynamic_entries_symbol + " Auto Trader Bot replacing "+ordertype+" Open Order -> Genie Index @ " + str(current_genie_index) + " and GZSI @ " + str(gzsi_used) + ": "+ side + " " + str(order_size) + " Effective Leverage: " + str(effective_leverage) + "."
                                                    print(log)
                                                    with open("Genie_AutoTrader.txt", "a") as myfile:
                                                        myfile.write(log+'\n')
                                                except Exception as replace_order_error:
                                                    pass
                                                else:
                                                    # No exception occured
                                                    # Now add it to the Database
                                                    try:
                                                        mycursor.execute("UPDATE linked_orders SET price='"+str(chaser_price)+"', qty='"+str(order_size)+"' WHERE order_link_id='"+linked_order['order_link_id']+"'")
                                                        mydb.commit()
                                                    except Exception:
                                                        pass
                else:
                    # We are not in any Genie Index zone of interest
                    if ordertype == 'Limit':
                        #  Cancel any existing Limit Chaser Order (if any)
                        for linked_order in linked_orders_result:
                            try:
                                session.cancel_active_order(symbol=smart_dynamic_entries_symbol, order_link_id=linked_order['order_link_id'])
                            except Exception as cancel_order_error:
                                pass
                            else:
                                # No exception occured
                                try:
                                    mycursor.execute("DELETE FROM linked_orders WHERE order_link_id='"+linked_order['order_link_id']+"'")
                                    mydb.commit()
                                except Exception:
                                    pass



        '''
        # Executable Drawings Prototype
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute("SELECT * FROM executable_drawings WHERE api_key='"+api_key+"' AND api_secret='"+api_secret+"'")
        myresult = mycursor.fetchall()
        for executable_drawing in myresult:
            if executable_drawing['type'] == 1:
                # Ray
                X = [[float(executable_drawing['x1'])], [float(executable_drawing['x2'])]]  # timestamps of the 2 points connecting the Ray
                y = [[float(executable_drawing['y1'])], [float(executable_drawing['y2'])]]  # prices of the 2 points connecting the Ray

                model = LinearRegression()
                model.fit(X, y)

                X_predict = [[int(datetime.now().timestamp())]]  # Find out current timestamp's Price value
                y_predict = model.predict(X_predict)
                print("Ray intersetion: " + str(y_predict))
        '''

        sleep(wait_time)