Author: Hadi Aladdin ([https://linktr.ee/hadialaddin](https://linktr.ee/hadialaddin))

Social Media: @hadialaddin

# Crypto Genie 🧞

Suite of Automated Monitors (Bots) to empower Day Traders and enable them to stick to their Trade Plans — Risk:Reward ratios.
Althoguh designed to automate most of the Risk:Reward aspects of day trading, this suite of tools acts as an assistant instead of auto-pilot.

## Disclaimer

This software is for educational purposes only. Do not risk money which you are afraid to lose. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS. Always verify any actions taken by the bot.

## Features

NOTE: If you use ratios for any of the features, then you will need to activate "TP/SL on Selected Position" for each Asset on the Exchange, for the Bot to work properly.

### Risk Management Monitor
Automated Risk Management Monitor for cryptocurrencies exchanges that forces all open positions to adhere to specific risk ratios, defined per asset. Simply, it automatically adds/modifies _**Stop Loss(es)**_ for any position created or modified, making sure that the maximum Stop Loss (after leverage, in case of using Margin) does not exceed a specific ratio. It also has an Emergency Enforced Market Stop Loss in case a position is open and the price already broke the allowed Stop Loss range.

NOTE: Updating the Leverage might not automatically update your stop loss for the respective position. You would need to change it upon updating so that it auto adjusts.

#### Static Stop Loss

This feature allows you to pre-set a Stop Loss ratio that will be enforced without allowing the user to move it above or below it. It will only allow moving the Stop Loss when position is in profit, which would allow moving it to breakeven or profit. Also, adding into the position will automatically adjust the Stop Loss to maintain the same ratio defined away from the new averaged Entry Price of the position. It will ensure full position-size Stop Loss always in place.

#### Total Balance Static Stop Loss

This feature allows you to set a maximum amount (ratio) of your Total Balance you would like to automatically close any position when its Unrealised PnL hits it. This guarantees a position would not loose more than that amount.

#### Stop Loss Range

This feature allows you to pre-set a maximum range for the Stop Loss, allowing you to move your Stop Loss closer to the entry price (lower loss or in profit) but not further away, thus enforcing a maximum loss.

### Take Profits Monitor
Automated Take Profits Monitor that will ensure specific pre-defined ratios of active positions are taken at specific price levels (in profit ratios), to avoid missing on potential gains that usually get lost if not taken.

### Lock In Profits Monitor
Automated Lock In Profits Monitor to ensure the Stop Loss moves from Loss to Breakeven or In-Profit to avoid incurring losses once a position satisfies the price level conditions.

## Demo

[![CryptoGenie Video Demo](https://i.ibb.co/Y2m03CD/You-Tube-Player-Image.png)](https://youtu.be/Alu4FlkTKi4 "CryptoGenie Video Demo")


- Video 1: [https://youtu.be/Alu4FlkTKi4](https://youtu.be/Alu4FlkTKi4)
- Video 2: [https://youtu.be/r0wvB_O3wjk](https://youtu.be/r0wvB_O3wjk)
- Video 3: [https://youtu.be/8kN0qsg9JcA](https://youtu.be/8kN0qsg9JcA)
- Video 4: [https://youtu.be/yhkY9F-Py1o](https://youtu.be/yhkY9F-Py1o)

## Installation

Installation Video: [https://www.youtube.com/watch?v=djeJiog18Lg](https://www.youtube.com/watch?v=djeJiog18Lg)

- Start by creating exchange API access and copy the credentials (Key and Secret). ByBit instructions: [https://help.bybit.com/hc/en-us/articles/360039749613-How-to-create-a-new-API-key-](https://help.bybit.com/hc/en-us/articles/360039749613-How-to-create-a-new-API-key-)
- Download the codebase (go to "Download" then "Download ZIP") and extrat its contents.
- Install the latest version of Python 3: [https://www.python.org/downloads/](https://www.python.org/downloads/) and make sure to check "Add Python to PATH" during installation. You might need to run the installed "Run as Administrator".
- Open the terminal (Search for 'cmd' on Windows and open it as Administrator) and run the following command to install the required ByBit's PyBit package:
  * `pip3 install pybit`
     - If it didn't work, execute this command instead: `C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python36-32\Scripts\pip3 install pybit` where "Python36-32" should be replaced by the name of the folder pertaining to the installed Python version.

- Run the crypto-genie bot using the command below in the terminal:
  * `python C:\TYPE\PATH\TO\EXTRACTED\ZIP\FOLDER\HERE\crypto-genie.py`

NOTE: This thread could address some of your Pytjon installation issues: https://stackoverflow.com/questions/6587507/how-to-install-pip-with-python-3

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

Edit the constants defined at the beginning of the crypto-genie.py file (using Notepad or any file text editor) to set your Exchange API credentials, as well as specific risk ratios for any specific asset. By default, all assets will have the defined constants with the prefix `default_`.

## Contribute

I will do my best to evolve this project and add more features for Stop Loss and Take Profits to ease implementing trading strategies. If you have any ideas or feature suggestions, please contact me or go to the "Issues" tab above to create ones.
