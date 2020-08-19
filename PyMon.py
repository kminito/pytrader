import sys
from PyQt5.QtWidgets import *
import Kiwoom
import time
from pandas import DataFrame
import datetime
import logging
import pickle

logging.basicConfig(filename="pymon.txt", level=logging.INFO)

MARKET_KOSPI   = '0'
MARKET_KOSDAQ  = '10'
MARKET_ETF = '8'

class PyMon:
    def __init__(self):
        self.kiwoom = Kiwoom.Kiwoom()
        self.kiwoom.commConnect()
        self.get_code_list()
        # self.data = None
        self.result = []

    def get_code_list(self):
        self.kospi_codes = self.kiwoom.getCodeListByMarket(MARKET_KOSPI)
        self.kosdaq_codes = self.kiwoom.getCodeListByMarket(MARKET_KOSDAQ)
        self.codes = self.kospi_codes+self.kosdaq_codes

    def get_price(self, code):
        self.kiwoom.setInputValue("종목코드", code)
        self.kiwoom.commRqData("주식기본정보요청", "opt10001", 0, "2001")

    def get_data(self, codes):
        i = 0
        for code in self.codes:
            print(i)
            self.get_price(code)
            time.sleep(0.3)
            i = i+1

        df = DataFrame(self.kiwoom.opt10001Data, columns=['code', 'high', 'low'])
        self.data = df
        print(df)
        return df

     
    def get_ohlcv(self, code, start):
        self.kiwoom.ohlcv = {'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'volume': []}

        self.kiwoom.setInputValue("종목코드", code)
        self.kiwoom.setInputValue("기준일자", start)
        self.kiwoom.setInputValue("수정주가구분", "1")
        self.kiwoom.commRqData("주식일봉차트조회요청", "opt10081", 0, "0101")
        time.sleep(0.3)

        df = DataFrame(self.kiwoom.ohlcv, columns=['open', 'high', 'low', 'close', 'volume'],
                    index=self.kiwoom.ohlcv['date'])
        return df



    def update_buy_list(self, buy_list):
        f = open("buy_list.txt", "wt")
        for code in buy_list:
            f.writelines("매수;", code, ";시장가;10;0;매수전")
        f.close()

    def load_data(self, file_name):
        try:
            f = open("./data/{}".format(file_name   ), "rb")
            data = pickle.load(f)
            f.close()
            return data
        except:
            pass

    def process_df(self, df):
        
        df = df[df['volume'] !=0]
        ma5 = df['close'].rolling(window=5).mean()
        ma20 = df['close'].rolling(window=20).mean()
        ma60 = df['close'].rolling(window=60).mean()
        df.insert(len(df.columns), "MA5", ma5)
        df.insert(len(df.columns), "MA20", ma20)
        df.insert(len(df.columns), "MA60", ma60)
        df.dropna(inplace=True)
        index_list = df.index

        
        return df

        logging.info("시가{} 손익{} 카운터{}".format(df.loc[index_list[1], 'open'], initial, cnt))







    def run(self):
        # buy_list = []
        # num = len(self.codes)
        # self.get_code_list()
        # self.get_data(self.codes)
        
        for code in self.codes:

            df = self.get_ohlcv(code, "20200729")
            f = open("./data/{}.db".format(code), "wb")
            pickle.dump(df, f)
            f.close()


        for i in os.listdir("data"):
        df = load_data(i)
        df = process_df(df)
        test(df)
        print("{} done".format(i))

        # self.update_buy_list(buy_list)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pymon = PyMon()
    pymon.run()