Author: Hadi Aladdin ([https://linktr.ee/hadialaddin](https://linktr.ee/hadialaddin))

Social Media: @hadialaddin

# ByBit Risk Monitor Bot

An automated Risk Management Monitoring Bot for ByBit cryptocurrencies exchange that forces all open positions to adhere to a specific risk ratio, defined per asset. It supports **USDT Perpetual**, **Inverse Perpetual** and **Inverse Futures** all on _**Mainnet**_ and _**Testnet**_ but only for _**One-Way Mode**_ not _**Hedge Mode**_.

Simply, it automatically adds/modified a _**Stop Loss**_ for any position created or modified, making sure that the stop loss (after leverage, in case of using Margin) does not exceed a specific limit. For now, it supports _**TP/SL on Entire Position**_ mode, not _**TP/SL on Selected Position**_, and for all pairs.

NOTE: Updating the Leverage won't automatically update your stop loss for the respective position. You would need to change it upon updating so that it auto adjusts. Use at your own risk.

## Demo

Watch this video for a live demo: 

## Installation

- Install the latest version of Python 3: [https://www.python.org/downloads/](https://www.python.org/downloads/)
- Open the terminal and run the following command to install the required ByBit's PyBit package:
  * `pip install pybit`

- Run the monitor bot using the command:
  * `python monitor.py`

You can run this Python script as a background process using **pm2** to auto reload if it crashes. Install pm2 ([https://pm2.keymetrics.io/docs/usage/quick-start/](https://pm2.keymetrics.io/docs/usage/quick-start/)) then:
To start the pm2 monitor process: `pm2 start monitor.py --interpreter=python`
To stop the pm2 monitor process: `pm2 stop monitor`


_NOTE: In case your server has an older version of Python, you can use "python3" to instead of "python" for all the commands above._

## Configuration

Edit the constants defined at the beginning of the monitor.py file to set your ByBit API credentials, as well as specific risk ratios for any specific asset. By default, all assets will have the defined `stop_loss_cap_ratio`.
