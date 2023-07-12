Author: Hadi Aladdin ([https://linktr.ee/hadialaddin](https://linktr.ee/hadialaddin))

Social Media: @hadialaddin

# Crypto Genie 🧞

Suite of advanced automated trading bots and risk management tools to empower Day Traders and enable them to stick to their Trade Plans — Risk:Reward ratios.
Althoguh designed to automate most of the Risk:Reward aspects of day trading, this suite of tools acts as an assistant instead of auto-pilot.

## Disclaimer

This software is for educational purposes only. Do not risk money which you are afraid to lose. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHOR AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS. Always verify any actions taken by the bot.

## Features

NOTE: If you use ratios for any of the features, then you will need to activate "TP/SL on Selected Position" for each Asset on the Exchange, for the Bot to work properly.

### Risk Management
Automated Risk Management Monitor for cryptocurrencies exchanges that forces all open positions to adhere to specific risk ratios, defined per asset. Simply, it automatically adds/modifies _**Stop Loss(es)**_ for any position created or modified, making sure that the maximum Stop Loss (after leverage, in case of using Margin) does not exceed a specific ratio. It also has an Emergency Enforced Market Stop Loss in case a position is open and the price already broke the allowed Stop Loss range.

NOTE: Updating the Leverage might not automatically update your stop loss for the respective position. You would need to change it upon updating so that it auto adjusts.

#### Static Stop Loss

This feature allows you to pre-set a Stop Loss ratio that will be enforced without allowing the user to move it above or below it. It will only allow moving the Stop Loss when position is in profit, which would allow moving it to breakeven or profit. Also, adding into the position will automatically adjust the Stop Loss to maintain the same ratio defined away from the new averaged Entry Price of the position. It will ensure full position-size Stop Loss always in place.

#### Total Balance Static Stop Loss

This feature allows you to set a maximum amount (ratio) of your Total Balance you would like to automatically close any position when its Unrealised PnL hits it. This guarantees a position would not loose more than that amount.

#### Stop Loss Range

This feature allows you to pre-set a maximum range for the Stop Loss, allowing you to move your Stop Loss closer to the entry price (lower loss or in profit) but not further away, thus enforcing a maximum loss.

### Take Profits
Automated Take Profits Monitor that will ensure profits are partially or fully taken, to avoid missing on potential gains that usually get lost if not taken.

#### Ratio Take

Take Profits at specific pre-defined ratios of active positions (in profit ratios). You can define as many as you want. Supports Limit and TP (market).

#### Dynamic Levels Take Profits

Supports Indicators (eg. EMAs, Bollinger Band, etc.) where you can specify on each time frame you want as many as you want, and Crypto Genie will automatically monitor all to take profit whenever price touches or crosses (in the right direction) those levels in profit. It supports both Limit Close and Market orders, and allows single or multiple levels.

### Lock In Profits
Automated Lock In Profits Monitor to ensure the Stop Loss moves from Loss to Breakeven or In-Profit to avoid incurring losses once a position satisfies the price level conditions.

### Hedging Engine and Hedge Balancer
Allows monitoring hedged positions, as well as balancing them at a specific loss, or killing both sides at a specific total loss reached. Say you open a Long and that reaches a loss of 10% total balance, then Crypto Genie can automatically open an equal size Short to hedge and stop further losses. If you release full or partial size of either sides, the engine will keep monitoring and hedging again if further losses incurred at incremental ratios, up till a spcific total loss on both sides where it will automatically close both sides to prevent further losss.

### Limit Chaser (Smart Spread Bid/Ask Engine)
Crypto Genie has a Smart Spread Bid/Ask Engine which powers a Limit Chaser functionality where it will try to chase the price with a specific margin to close the position without paying Market Fees.

### Auto Trader (Entries)
The Auto Trader feature is an evolving part of Crypto Genie. It will support various smart strategies. Those could include Fibonacci Retracement levels, Dynamic Levels (EMAs, Bollinger Band, VWAPs, aVWAPs, etc.) where a scoring system is used to defined the effective leverage to be used for entering or adding to an already existing position. Such strategies include entering when price is over extended from a dynamic level (eg. EMA), or first hit of a Fibonacci Retracement level. To explore these features, check the end of the 'crypto-genie.py' file and play around with the code.

### Weh Dashboard
The Web Dashboard allows users to manage and monitor the various features of the Crypto Genie Bot, as well as easily control many variables and configurations without the need to edit the script manually. If enabled in the script, the Dashboard can show various charts being exprted by the script such as Fibonacci Retracements of various timeframes for the Auto Trader. Note that to use the Web Dashboard, you will need to edit the "/dashboard/config.php" file with your Databasse's credentials.

- Dashboard Tutorial Video: [https://youtu.be/xQJGU6bD29E](https://youtu.be/xQJGU6bD29E)
- Dashboard and Smart Spread Bid/Ask Engine Tutorial Video: [https://youtu.be/tl49b0AY5xI](https://youtu.be/tl49b0AY5xI)

#### Scaled Orders

Crypto Genie Bot supports Scaled Orders feature through its Web Dashboard. You can easily create batches of Orders within specific ranges of prices, with total quantities order counts as you desire. You can place LONG and SHORT orders quickly.

#### Executable Drawings

This feature is still being built. It allows the use of TradingView's SDK to draw trendlines/objects and have Crypto Genie automate specific actions on them (eg. execute a pyramiding, TPs, SL, Hedging etc. when price reaches the Trendlines/EMA/AVWAP).

- Video: [https://youtu.be/tTfTRI57Qxc](https://youtu.be/tTfTRI57Qxc)

## Demo

[![CryptoGenie Video Demo](https://i.ibb.co/Y2m03CD/You-Tube-Player-Image.png)](https://youtu.be/Alu4FlkTKi4 "CryptoGenie Video Demo")


- Video 1: [https://youtu.be/Alu4FlkTKi4](https://youtu.be/Alu4FlkTKi4)
- Video 2: [https://youtu.be/r0wvB_O3wjk](https://youtu.be/r0wvB_O3wjk)
- Video 3: [https://youtu.be/8kN0qsg9JcA](https://youtu.be/8kN0qsg9JcA)
- Video 4: [https://youtu.be/ASwSyE0Fy78](https://youtu.be/ASwSyE0Fy78)
- Video 5: [https://youtu.be/a7ivDslDH-A](https://youtu.be/a7ivDslDH-A)
- Video 6: [https://youtu.be/WVXoCY-KMlc](https://youtu.be/WVXoCY-KMlc)
- Video 7: [https://youtu.be/z-4SxjahqkY](https://youtu.be/z-4SxjahqkY)
- Video 8: [https://youtu.be/yhkY9F-Py1o](https://youtu.be/yhkY9F-Py1o)
- Video 9: [https://youtu.be/xQJGU6bD29E](https://youtu.be/xQJGU6bD29E)
- Video 10: [https://youtu.be/tl49b0AY5xI](https://youtu.be/tl49b0AY5xI)
- Video 11: [https://youtu.be/tTfTRI57Qxc](https://youtu.be/tTfTRI57Qxc)

## Installation

Installation Video: [https://www.youtube.com/watch?v=djeJiog18Lg](https://www.youtube.com/watch?v=djeJiog18Lg)

- Start by creating exchange API access and copy the credentials (Key and Secret). ByBit instructions: [https://help.bybit.com/hc/en-us/articles/360039749613-How-to-create-a-new-API-key-](https://help.bybit.com/hc/en-us/articles/360039749613-How-to-create-a-new-API-key-)
- Download the codebase (go to "Download" then "Download ZIP") and extrat its contents.
- Install the latest version of Python 3 (3.8+): [https://www.python.org/downloads/](https://www.python.org/downloads/) and make sure to check "Add Python to PATH" during installation. You might need to run the installed "Run as Administrator". Python 3 comes with Pip3, if not you will need to install it, too.
- Open the terminal (Search for 'cmd' on Windows and open it as Administrator) and run the following commands to install the required ByBit's PyBit package as well as Pandas:
  * `pip3 install pybit`
  * `pip3 install wheel`
  * `pip3 install pandas`
  * `pip3 install pandas_ta`
  * `pip3 install matplotlib`
  * `pip3 install mysql-connector-python`
  * `pip3 install pydash`
  * `pip3 install pyyaml`
     - For Windows: if any of the commands didn't work, execute them with the following command structure: `C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python36-32\Scripts\pip3 install pybit` where "Python36-32" should be replaced by the name of the folder pertaining to the installed Python version.

NOTE: This thread could address some of your Python installation issues: https://stackoverflow.com/questions/6587507/how-to-install-pip-with-python-3

## Supported Exchanges

- ByBit:
    - Pairs supported: **USDT Perpetual**, **Inverse Perpetual** and **Inverse Futures**
    - Networks supported: _**Mainnet**_ and _**Testnet**_
    - TP/SL Modes supported: **TP/SL on Entire Position**_ and _**TP/SL on Selected Position**_
    - Position Direction supported: _**One-Way Mode**_. Note that _**Hedge Mode**_ is only supported on the **USDT Perpetuals** for now due to ByBit's API limitations, so _**Hedge Mode**_ is not supported for **Inverse Perpetuals** and **Futures Perpetuals**, yet.

## Configuration

Edit config.yaml with your API keys and MySQL Database credentials (if you want to use the DB features such as Auto Trader or Dashboard, make sure to activate that in the config file as well as at the top of 'postScaledOrders.php' and run the .sql file to setup the DB), and set the variables to your liking.
Make more copies of config.yaml for other setups you want to run.

## Running

You can run this script multiple times, one in each terminal, with a different config file for each! If you don't pass the name of the `config_file`, it will assume it as `config.yaml` by default.

- Run the crypto-genie bot using the command below in the terminal:
  * `python C:\TYPE\PATH\TO\EXTRACTED\ZIP\FOLDER\HERE\crypto-genie.py config_file=config.yaml`

You can run this Python script as a background process using **pm2** to auto reload if it crashes. Install pm2 ([https://pm2.keymetrics.io/docs/usage/quick-start/](https://pm2.keymetrics.io/docs/usage/quick-start/)) then:

To start the pm2 crypto-genie process:
  * `pm2 start crypto-genie.py --name "crypto-genie-process" --interpreter=python3 -- config_file=config.yaml`
  * NOTE: change "config.yaml" to the name of the config file, and "crypto-genie-process" to any custom name for multiple processes if you want to run more than one.

To stop the pm2 crypto-genie process:
  * `pm2 stop crypto-genie-process`
  * * NOTE: change "crypto-genie-process" to the name of the process you want to stop in case of multiple ones running.

_NOTE: In case your server has an older version of Python, you can use "python3" to instead of "python" for all the commands above._

## Contribute

I will do my best to evolve this project and add more features for Stop Loss and Take Profits to ease implementing trading strategies. If you have any ideas or feature suggestions, please contact me or go to the "Issues" tab above to create ones.
