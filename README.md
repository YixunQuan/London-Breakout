# London Breakout Strategy

A high-probability intraday breakout system implemented in Python using Backtrader, designed to simulate and optimize GBP/USD trading during the London session. The strategy is based on Tokyo session range breakout logic.

---

## 📌 Strategy Overview

This strategy executes breakout trades based on the 08:00–16:00 (GMT+8) Tokyo session range.

### Entry Logic

* At **16:00**, calculate the high and low from the Tokyo session.
* At **16:00**, place:

  * `Buy Stop` at the high
  * `Sell Stop` at the low
* Cancel untriggered orders from the previous day.
* Once one order is triggered, cancel the other.

### Exit Logic

* If floating profit exceeds `TRAIL_TRIGGER_PIPS`, activate a trailing stop starting from `TRAIL_START_PIPS`.
* If the next day's breakout direction **conflicts** with the current position, exit at market.

---

## 📊 Data Source & Preparation

* Raw data was exported from **MetaTrader 5 demo account**, using M5 chart data of GBP/USD.
* The data was **cleaned and converted to GMT+8 timezone**, and column headers (e.g. `datetime`, `open`, `high`, `low`, `close`, `volume`) were adjusted to meet **Backtrader's PandasData format**.
* All timestamps were localized to UTC+8 to ensure correct session segmentation.

---

## ✅ Real-World Performance

This strategy has been forward-tested in **MetaTrader 5** and demonstrated:

* 🏆 **Win Rate**: >80% in favorable market conditions
* ⚠️ **Drawdown**: Can be significant during volatility, depends on the lot size; one dropdown could eat up 30 wins profit.
* 📉 **Profit Factor**: Low per-trade profit, sensitive to position sizing and news events

> It is a **high win-rate, low profit** system, where risk control and news avoidance are crucial for long-term profitability.

---

## 📈 Backtest Summary

* Start Account: 100000
* Total Trades: 34
* Win Rate: 64.71%
* Avg Win: 451.19
* Avg Loss: 505.89
* Profit Factor: 0.89
* Max Drawdown: 2769.93
* Final Portfolio Value: 102865.40
* Monthly Increase rate: 1.5% ( at low lot size, if you can handle 10% DD it can go up to 15%)

> 📌 Recent market volatility decreased win rate , and also led to higher drawdowns. Careful filtering and capital allocation remain essential.

---

## ⏱ Timezone Notes

* Strategy logic assumes all times are in **GMT+8**.
* For real deployment, **adjust entry windows according to DST**:

  * UK Summer Time: London open ≈ 15:00 GMT+8
  * UK Winter Time: London open ≈ 16:00 GMT+8
* Tokyo session window may need to shift accordingly when operating across timezones or seasons.

---

## 🔧 Future Improvements

* 📉 Filter trades during excessive range days or low volatility
* ⏱ Add time-based stopout (e.g. force close after 24h)
* ⚖ Dynamic position sizing based on volatility
* 📰 Avoid New York session volatility by skipping post-news hours
* 🔄 Support multi-symbol backtesting (EUR/USD, XAU/USD)
* 📊 Export full trade logs to CSV for performance visualization

---

## 📁 Project Structure

```
LondonBreakout/
├── strategy.py          # Core strategy logic
├── backtest.py          # Execution script
├── config.py            # Parameter definitions
├── data/GBPUSDM5.csv    # Sample dataset
├── README.md            # Documentation and usage
```

---

## 🧠 Skills Demonstrated

* Quantitative strategy design & testing
* Backtrader framework & time-series control
* Risk management & exit design
* Python-based trade logging & performance evaluation
