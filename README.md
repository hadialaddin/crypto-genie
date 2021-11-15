Author: Hadi Aladdin ([https://linktr.ee/hadialaddin](https://linktr.ee/hadialaddin))

Social Media: @hadialaddin

# ByBit Risk Management Monitor Bot

An automated Risk Management Monitor Bot for ByBit cryptocurrencies exchange that forces all open positions to adhere to a specific risk ratio, defined per asset. It supports **USDT Perpetual**, **Inverse Perpetual** and **Inverse Futures** all on _**Mainnet**_ and _**Testnet**_.

Simply, it automatically adds/modifies a _**Stop Loss**_ for any position created or modified, making sure that the stop loss (after leverage, in case of using Margin) does not exceed a specific limit. It supports _**TP/SL on Entire Position**_ and _**TP/SL on Selected Position**_ modes, as well as _**One-Way Mode**_. Note that _**Hedge Mode**_ is only supported on the **USDT Perpetuals** for now due to ByBit's API limitations, so _**Hedge Mode**_ is not supported for **Inverse Perpetuals** and **Futures Perpetuals**, yet.

NOTE: Updating the Leverage won't automatically update your stop loss for the respective position. You would need to change it upon updating so that it auto adjusts. Use at your own risk.

## Demo

Watch this video for a live demo: [https://youtu.be/yhkY9F-Py1o](https://youtu.be/yhkY9F-Py1o)

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

Edit the constants defined at the beginning of the monitor.py file to set your ByBit API credentials, as well as specific risk ratios for any specific asset. By default, all assets will have the defined constants with the prefix `default_`.

## Contribute

I will do my best to evolve this project and add more features for Stop Loss and Take Profits to ease implementing trading strategies. If you have any ideas or feature suggestions, please contact me or go to the "Issues" tab above to create ones.
