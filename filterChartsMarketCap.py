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

            ticker = f.split('_')[0]
            tickers_list.append(ticker)

print("получение данных по капитализации")
start = time.time()
try:
    cap = web.get_quote_yahoo(tickers_list)['marketCap']
except KeyError:
    exit(1)
end = time.time()
elapsed_time = format((end - start), '.2f')
print(f'данные по {len(tickers_list)} тикерам получены за {elapsed_time} сек.')

print("удаление файлов акций, которые не подходят под заданные параметры капитализации")
deleted_tickers = dict()
for root, _, f_names in os.walk(directory):
    for f in f_names:
        if f.endswith('.png'):
            if 'FAANG-FAAMG + other stocks' not in root:
                continue

            ticker = f.split('_')[0]
            cap_bln = float(format((cap[ticker] / 1e9), '.2f'))

            if (max_cap_is_defined and cap_bln > max_cap_bln) or \
                    (min_cap_is_defined and cap_bln < min_cap_bln):
                os.remove(os.path.join(root, f))
                deleted_tickers[ticker] = cap_bln
                continue

            if rename_files == 'yes':
                new_name = str(cap_bln) + '_' + f
                os.rename(os.path.join(root, f), os.path.join(root, new_name))

print(f'тикеры удаленных файлов с капитализацией: {str(dict(deleted_tickers))}')
