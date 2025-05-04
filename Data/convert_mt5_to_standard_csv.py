import pandas as pd

def convert_mt5_to_standard_csv(input_path, output_path):
    df = pd.read_csv(input_path, header=None)

    print(f"列数：{len(df.columns)}")  # 确认是7列

    # 正确设置 7 列名
    df.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'misc']

    # 保留需要的6列
    df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']]

    # 转换时间格式
    df['datetime'] = pd.to_datetime(df['datetime'], format='%Y.%m.%d %H:%M')

    # 保存为标准格式
    df.to_csv(output_path, index=False)
    print(f"✅ 文件转换成功：{output_path}")

if __name__ == "__main__":
    convert_mt5_to_standard_csv('./GBPUSDM5_utf8.csv', './GBPUSDM5_standard.csv')
