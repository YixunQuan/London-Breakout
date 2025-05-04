# convert_to_utf8.py

import chardet

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(10000))  # 读取部分内容检测
        return result['encoding']

def convert_to_utf8(input_path, output_path):
    encoding = detect_encoding(input_path)
    print(f"Detected encoding: {encoding}")

    if encoding.lower() == 'utf-8':
        print("File is already in UTF-8 encoding. No conversion needed.")
        return

    with open(input_path, 'r', encoding=encoding, errors='ignore') as infile:
        content = infile.read()

    with open(output_path, 'w', encoding='utf-8') as outfile:
        outfile.write(content)

    print(f"File converted to UTF-8 and saved to: {output_path}")

if __name__ == '__main__':
    input_file = './GBPUSDM5.csv'
    output_file = './GBPUSDM5_utf8.csv'

    convert_to_utf8(input_file, output_file)
