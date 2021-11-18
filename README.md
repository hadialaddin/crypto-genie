Author: Hadi Aladdin ([https://linktr.ee/hadialaddin](https://linktr.ee/hadialaddin))

Social Media: @hadialaddin

# Crypto Genie 🧞

Suite of Automated Monitors (Bots) to empower Day Traders and enable them to stick to their Trade Plans — Risk:Reward ratios.
Althoguh designed to automate most of the Risk:Reward aspects of day trading, this suite of tools acts as an assistant instead of auto-pilot.

Always verify any actions taken by these monitors, and manually manage your positions. Use at your own risk!

## Features

### Risk Management Monitor
Automated Risk Management Monitor for cryptocurrencies exchanges that forces all open positions to adhere to specific risk ratios, defined per asset. Simply, it automatically adds/modifies _**Stop Loss(s)**_ for any position created or modified, making sure that the maximum Stop Loss (after leverage, in case of using Margin) does not exceed a specific ratio. It also has an Emergency Enforced Market Stop Loss in case a position is open and the price already broke the allowed Stop Loss range.

NOTE: Updating the Leverage won't automatically update your stop loss for the respective position. You would need to change it upon updating so that it auto adjusts.

### Take Profits Monitor
Automated Take Profits Monitor that will ensure specific pre-defined quantities of the positions are taken at specific price levels, to avoid missing on potential gains that usually get lost if not taken.

### Lock In Profits Monitor
Automated Lock In Profits Monitor to ensure the Stop Loss moves from Loss to Breakeven or In-Profit to avoid incurring losses once a position satisfies the price level conditions.

## Demo

[![CryptoGenie Video Demo](https://i.ibb.co/Y2m03CD/You-Tube-Player-Image.png)](https://youtu.be/Alu4FlkTKi4 "CryptoGenie Video Demo")


- Video 1: [https://youtu.be/Alu4FlkTKi4](https://youtu.be/Alu4FlkTKi4)
- Video 2: [https://youtu.be/yhkY9F-Py1o](https://youtu.be/yhkY9F-Py1o)

## Installation

- Install the latest version of Python 3: [https://www.python.org/downloads/](https://www.python.org/downloads/)
- Open the terminal (Search for 'cmd' on Windows and open it as Administrator) and run the following command to install the required ByBit's PyBit package:
  * `pip3 install pybit`
     - If it didn't work, execute this command instead: `C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python36-32\Scripts\pip3 install pybit` where "Python36-32" should be replaced by the name of the folder pertaining to the installed Python version.

- Run the crypto-genie bot using the command:
  * `python crypto-genie.py`

You can run this Python script as a background process using **pm2** to auto reload if it crashes. Install pm2 ([https://pm2.keymetrics.io/docs/usage/quick-start/](https://pm2.keymetrics.io/docs/usage/quick-start/)) then:
To start the pm2 crypto-genie process: `pm2 start crypto-genie.py --interpreter=python3`
To stop the pm2 crypto-genie process: `pm2 stop crypto-genie`

_NOTE: In case your server has an older version of Python, you can use "python3" to instead of "python" for all the commands above._

## Supported Exchanges

- ByBit:
    - Pairs supported: **USDT Perpetual**, **Inverse Perpetual** and **Inverse Futures**
    - Networks supported: _**Mainnet**_ and _**Testnet**_
    - TP/SL Modes supported: **TP/SL on Entire Position**_ and _**TP/SL on Selected Position**_
    - Position Direction supported: _**One-Way Mode**_. Note that _**Hedge Mode**_ is only supported on the **USDT Perpetuals** for now due to ByBit's API limitations, so _**Hedge Mode**_ is not supported for **Inverse Perpetuals** and **Futures Perpetuals**, yet.

## Configuration

Edit the constants defined at the beginning of the crypto-genie.py file to set your Exchange API credentials, as well as specific risk ratios for any specific asset. By default, all assets will have the defined constants with the prefix `default_`.

## Contribute

I will do my best to evolve this project and add more features for Stop Loss and Take Profits to ease implementing trading strategies. If you have any ideas or feature suggestions, please contact me or go to the "Issues" tab above to create ones.
