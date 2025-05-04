import backtrader as bt
import datetime
from config import *

PIP = 0.0001  # GBP/USD 一点是 0.0001

class LondonBreakout(bt.Strategy):
    params = dict()

    def __init__(self):
        self.order_buy = None
        self.order_sell = None
        self.pending_orders = []
        self.breakout_high = None
        self.breakout_low = None
        self.entry_price = None
        self.trailing_active = False
        self.trailing_sl = None
        self.holding_direction = None
        self.order_day = None
        self.entry_day = None
        self.trades = []

    def log(self, txt):
        dt = self.datas[0].datetime.datetime(0)
        print(f"[{dt.strftime('%Y-%m-%d %H:%M')}] {txt}")

    def next(self):
        dt = self.datas[0].datetime.datetime(0)
        time_str = dt.strftime('%H:%M')

        # 每天 16:05 计算突破区间
        if time_str == "16:05":
            self.calculate_breakout_range()

        # 每天 16:10 判断并挂单
        if time_str == ORDER_TIME and not self.order_day == dt.date():
            self.cancel_pending_orders()
            self.check_direction_conflict(dt.date())
            self.place_orders()
            self.order_day = dt.date()

        self.manage_trailing_stop()

    def calculate_breakout_range(self):
        data = self.datas[0]
        now = data.datetime.datetime(0)
        today_date = now.date()

        highs = []
        lows = []
        matched_count = 0

        for i in range(-500, 0):
            dt = data.datetime.datetime(i)
            if dt.date() != today_date:
                continue
            if 8 <= dt.hour < 16:
                matched_count += 1
                highs.append(data.high[i])
                lows.append(data.low[i])

        if matched_count < 90:
            self.log(f"⚠ 数据不足：仅找到 {matched_count} 根K线，跳过今日")
            return

        self.breakout_high = max(highs)
        self.breakout_low = min(lows)
        self.log(f"✅ 区间成功 | High={self.breakout_high:.5f}, Low={self.breakout_low:.5f}")

    def place_orders(self):
        if self.breakout_high is None or self.breakout_low is None:
            return

        size = self.broker.get_cash() * 0.95 / self.data.close[0]

        self.order_buy = self.buy(exectype=bt.Order.Stop, price=self.breakout_high, size=size)
        self.order_sell = self.sell(exectype=bt.Order.Stop, price=self.breakout_low, size=size)

        self.pending_orders = [self.order_buy, self.order_sell]
        self.log("📌 已挂 BuyStop 和 SellStop")

    def cancel_pending_orders(self):
        for o in self.pending_orders:
            self.cancel(o)
        if self.pending_orders:
            self.log("🗑️ 取消前日挂单")
        self.pending_orders = []

    def check_direction_conflict(self, today):
        if self.holding_direction and self.entry_day != today:
            new_dir = self.check_new_direction()
            if new_dir and new_dir != self.holding_direction:
                self.log("⚠️ 方向冲突，止损出场")
                self.close()

    def check_new_direction(self):
        if not self.breakout_high or not self.breakout_low:
            return None
        price = self.data.close[0]
        if price > self.breakout_high:
            return 'long'
        elif price < self.breakout_low:
            return 'short'
        return None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.entry_price = order.executed.price
            self.holding_direction = 'long' if order.isbuy() else 'short'
            self.entry_day = self.datas[0].datetime.date(0)
            self.log(f"✅ 成交: {self.holding_direction} @ {self.entry_price:.5f}")
            self.cancel_pending_orders()

    def manage_trailing_stop(self):
        if not self.position:
            return

        price = self.data.close[0]

        if not self.trailing_active:
            if self.holding_direction == 'long' and price >= self.entry_price + TRAIL_TRIGGER_PIPS * PIP:
                self.trailing_active = True
                self.trailing_sl = self.entry_price + TRAIL_START_PIPS * PIP
                self.log(f"🟢 启动追踪止损 @ {self.trailing_sl:.5f}")
            elif self.holding_direction == 'short' and price <= self.entry_price - TRAIL_TRIGGER_PIPS * PIP:
                self.trailing_active = True
                self.trailing_sl = self.entry_price - TRAIL_START_PIPS * PIP
                self.log(f"🟢 启动追踪止损 @ {self.trailing_sl:.5f}")

        elif self.trailing_active:
            if self.holding_direction == 'long':
                new_sl = max(self.trailing_sl, price - (price - self.entry_price - TRAIL_TRIGGER_PIPS * PIP))
                if price < new_sl:
                    self.log(f"🔴 触发止损 @ {price:.5f} < SL {new_sl:.5f}")
                    self.close()
                self.trailing_sl = new_sl
            elif self.holding_direction == 'short':
                new_sl = min(self.trailing_sl, price + (self.entry_price - price - TRAIL_TRIGGER_PIPS * PIP))
                if price > new_sl:
                    self.log(f"🔴 触发止损 @ {price:.5f} > SL {new_sl:.5f}")
                    self.close()
                self.trailing_sl = new_sl

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        try:
            if trade.history:
                entry_time = bt.num2date(trade.history[0].event.dt)
            else:
                entry_time = bt.num2date(self.datas[0].datetime[0])
            exit_time = bt.num2date(self.datas[0].datetime[0])
        except Exception:
            self.log("❗ 无法获取交易时间")
            return

        direction = 'Long' if trade.history and trade.history[0].event.size > 0 else 'Short'
        pnl = trade.pnl

        self.trades.append({
            'entry_time': entry_time,
            'exit_time': exit_time,
            'direction': direction,
            'pnl': pnl
        })

        self.log(f"📈 平仓 | {direction} | Entry: {entry_time}, Exit: {exit_time}, PnL: {pnl:.2f}")

        self.entry_price = None
        self.holding_direction = None
        self.trailing_active = False
        self.trailing_sl = None
        self.entry_day = None
