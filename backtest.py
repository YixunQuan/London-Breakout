import backtrader as bt
import pandas as pd
import matplotlib.pyplot as plt
from strategy import LondonBreakout  # 你已写好的策略类
from config import *  # 策略参数

if __name__ == '__main__':
    # 创建 Cerebro 引擎
    cerebro = bt.Cerebro()
    cerebro.addstrategy(LondonBreakout)

    # 读取 CSV 数据
    df = pd.read_csv('./data/GBPUSDM5_standard.csv')
    df['datetime'] = pd.to_datetime(df['datetime']) + pd.Timedelta(hours=5)
    df.set_index('datetime', inplace=True)
    df = df.sort_index()

    # 添加数据到 Backtrader
    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)

    # 初始资金设置
    cerebro.broker.set_cash(100000)
    cerebro.broker.setcommission(commission=0.0001)

    print(f"🚀 Starting Portfolio Value: {cerebro.broker.getvalue():.2f}")

    # 运行策略并获得策略对象
    strats = cerebro.run()
    strat = strats[0]

    print(f"✅ Final Portfolio Value: {cerebro.broker.getvalue():.2f}")

    # 分析交易记录
    trades_df = pd.DataFrame(strat.trades)

    if trades_df.empty:
        print("⚠ 没有交易数据，可能未触发入场条件。")
    else:
        total_trades = len(trades_df)
        win_trades = trades_df[trades_df['pnl'] > 0]
        loss_trades = trades_df[trades_df['pnl'] <= 0]
        win_rate = len(win_trades) / total_trades
        avg_win = win_trades['pnl'].mean() if not win_trades.empty else 0
        avg_loss = abs(loss_trades['pnl'].mean()) if not loss_trades.empty else 1e-9
        profit_factor = avg_win / avg_loss

        # 计算资金曲线和最大回撤
        equity = 100000 + trades_df['pnl'].cumsum()
        drawdown = equity.cummax() - equity
        max_drawdown = drawdown.max()

        # 输出统计信息
        print("\n📊 回测统计结果")
        print(f"总交易次数     : {total_trades}")
        print(f"胜率           : {win_rate:.2%}")
        print(f"平均盈利       : {avg_win:.2f}")
        print(f"平均亏损       : {avg_loss:.2f}")
        print(f"盈亏比         : {profit_factor:.2f}")
        print(f"最大回撤       : {max_drawdown:.2f}")

        # 保存交易数据
        trades_df.to_csv('./trades_result.csv', index=False)
        print("📁 交易数据已保存至 trades_result.csv")

        # 绘制资金曲线
        plt.figure(figsize=(10, 5))
        plt.plot(equity, label='Equity Curve')
        plt.title('Equity Curve')
        plt.xlabel('Trades')
        plt.ylabel('Portfolio Value')
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    # 绘制图表（可选）
    # cerebro.plot(style='candlestick')  # 慢且卡，回测阶段可注释掉
