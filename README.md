Author: Hadi Aladdin ([https://linktr.ee/hadialaddin](https://linktr.ee/hadialaddin))
Social Media: @hadialaddin

# ByBit Risk Monitor

An automated Risk Management Monitoring Bot for ByBit cryptocurrencies exchange that forces all open positions to adhere to a specific risk ratio, defined per asset. It supports both Mainnet and Testnet.

Simply, it automatically adds/modified a _**Stop Loss**_ for any position created or modified, making sure that the stop loss (after leverage, in case of using Margin) does not exceed a specific limit.

Use at your own risk.

## Demo

Watch this video for a live demo: 

## Installation

- Install the latest version of Python 3: [https://www.python.org/downloads/](https://www.python.org/downloads/)
- Open the terminal and run the following commands to install the required ByBit HTTP and WebSocket packages:
  * `pip install bybit`
  * `python BybitWebsocket/setup.py install`

NOTE: the WebSocket package used is slightly modified to pypass the Authentication error caused by having your server out of sync with the ByBit server time.

- Run the monitor bot using the command:
  * python monitor.py

You can run this Python script as a background process using **pm2** to auto reload if it crashes. Install pm2 ([https://pm2.keymetrics.io/docs/usage/quick-start/](https://pm2.keymetrics.io/docs/usage/quick-start/)) then:
To start the pm2 monitor process: `pm2 start monitor.py --interpreter=python`
To stop the pm2 monitor process: `pm2 stop monitor`


_NOTE: In case your server has an older version of Python, you can use "python3" to instead of "python" for all the commands above._

## Configuration

Edit the constants defined at the beginning of the monitor.py file to set your ByBit API credentials, as well as specific risk ratios for any specific asset. By default, all assets will have the defined `stop_loss_cap_ratio`.
