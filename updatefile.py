import re
import sys


def get_data(file_name):
    with open(file_name, 'r') as f:
        data = f.read()
    return data

def get_data_list(data):
    data_list = re.split('\n', data)
    return data_list

def get_data_list_by_re(data, re_str):
    data_list = re.findall(re_str, data)
    return data_list

def append_quoted_content(file, new_content):
    if file:
        with open(file, 'r+', encoding='utf-8') as file:
            content = file.read()
            matches = re.findall(r'(\s+"(\[[^"]*)",)', content, re.S)
            if matches:
                # matches最后一项
                last = matches[-1]
                last_content = last[0]
                last_quoted = last[1]
                new_content = last_content.replace(last_quoted, new_content)

                content = content.replace(last_content, f'{last_content}{new_content}')
                file.seek(0)
                file.write(content)
                file.truncate()
                print('append_quoted_content success!')
                

if __name__ == '__main__':
    # 获取命令行参数
    args = sys.argv
    if len(args) == 4:
        if args[1] == '--quoted':
            append_quoted_content(args[2], args[3])
    else:
        print('参数不足3个')