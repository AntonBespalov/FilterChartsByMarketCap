import os
import configparser
from pathlib import Path
import pandas_datareader.data as web
import time

config = configparser.ConfigParser()
config.read("config.ini", encoding='utf-8')

min_cap = config.get('settings', 'min_cap')
min_cap_is_defined = False
if min_cap.isnumeric():
    min_cap_bln = float(min_cap)
    min_cap_is_defined = True

max_cap = config.get('settings', 'max_cap')
max_cap_is_defined = False
if max_cap.isnumeric():
    max_cap_bln = float(max_cap)
    max_cap_is_defined = True

max_price_str = config.get('settings', 'max_price')
max_price_is_defined = False
if max_price_str.isnumeric():
    max_price = float(max_price_str)
    max_price_is_defined = True

rename_files = config.get('settings', 'rename_files').lower()
path_to_charts = config.get('path', 'path')

print("формирование списка тикеров")
tickers_list = []
directory = Path(path_to_charts)

for root, _, f_names in os.walk(directory):
    for f in f_names:
        if f.endswith('.png'):
            if 'FAANG-FAAMG + other stocks' not in root:
                continue

            filename_splitted = f.split('_')
            if len(filename_splitted) > 2:
                # в названии тикера есть подчеркивание (пример: BRK_B), заменяем на дефис
                ticker = filename_splitted[0] + '-' + filename_splitted[1]
            else:
                ticker = filename_splitted[0]
            tickers_list.append(ticker)

print("получение данных по капитализации")
start = time.time()
try:
    quote = web.get_quote_yahoo(tickers_list)
    cap = quote['marketCap']
    price = quote['regularMarketPrice']
except Exception as ex:
    print('Error:', ex)
end = time.time()
elapsed_time = format((end - start), '.2f')
print(f'данные по {len(tickers_list)} тикерам получены за {elapsed_time} сек.')

print("удаление файлов акций, которые не подходят под заданные параметры капитализации и цены")
del_tickers_cap = dict()
del_tickers_price = dict()
for root, _, f_names in os.walk(directory):
    for f in f_names:
        if f.endswith('.png'):
            if 'FAANG-FAAMG + other stocks' not in root:
                continue

            filename_splitted = f.split('_')
            if len(filename_splitted) > 2:
                # в названии тикера есть подчеркивание (пример: BRK_B), заменяем на дефис
                ticker = filename_splitted[0] + '-' + filename_splitted[1]
            else:
                ticker = filename_splitted[0]

            cap_bln = float(format((cap[ticker] / 1e9), '.2f'))

            if (max_cap_is_defined and cap_bln > max_cap_bln) or \
                    (min_cap_is_defined and cap_bln < min_cap_bln):
                os.remove(os.path.join(root, f))
                del_tickers_cap[ticker] = cap_bln
                continue

            if price[ticker] > max_price:
                os.remove(os.path.join(root, f))
                del_tickers_price[ticker] = price[ticker]
                continue

            if rename_files == 'yes':
                new_name = str(cap_bln) + '_' + f
                os.rename(os.path.join(root, f), os.path.join(root, new_name))

print(f'тикеры файлов, не подошедших по капитализации компании: {str(dict(del_tickers_cap))}')
print(f'тикеры файлов, не подошедших по цене акции: {str(dict(del_tickers_price))}')
