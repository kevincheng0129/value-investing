# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 15:04:58 2020

@author: user
"""

import requests
import pandas as pd
import matplotlib.ticker as ticker
from io import StringIO
import time
import tkinter as tk
import datetime
import yfinance as yf
import matplotlib.pyplot as plt
from tqdm import tqdm

class value_investing:
    def __init__(self, n_year, n_season, o_year, o_season, n_month):

        self.stock = []
        self.n_year = n_year
        self.n_season = n_season
        self.o_year = o_year
        self.o_season = o_season
        self.month = n_month
        self.month_data = self.monthly_report()
        self.new_data = self.get_FP(n_year, n_season)
        self.old_data = self.get_FP(o_year, o_season)
        self.date = self.get_current_date()
    def get_current_date(self):
        x = datetime.datetime.now()
        date = str(x)[0:10]
        return date
    def financial_statement(self, year, season, type='綜合損益彙總表'):

        if year >= 1000:
            year -= 1911
    
        if type == '綜合損益彙總表':
            url = 'https://mops.twse.com.tw/mops/web/ajax_t163sb04'
        elif type == '資產負債彙總表':
            url = 'https://mops.twse.com.tw/mops/web/ajax_t163sb05'
        elif type == '營益分析彙總表':
            url = 'https://mops.twse.com.tw/mops/web/ajax_t163sb06'
        else:
            print('type does not match')
    
        r = requests.post(url, {
            'encodeURIComponent':1,
            'step':1,
            'firstin':1,
            'off':1,
            'TYPEK':'sii',
            'year':str(year),
            'season':str(season),
        })
        r.encoding = 'utf8'
        dfs = pd.read_html(r.text, header=None)
        return dfs
    def get_FP(self, year,season):
        data = self.financial_statement(year, season, '營益分析彙總表')
        data = pd.DataFrame(data[0])
        data.columns = data.iloc[0]
        data = data.drop([0])
        data = data.set_index(['公司代號'])
        data = data.drop(['公司名稱'],axis =1)
        data = data.drop(['公司代號'])
        data = data.astype(float)
        return data
    def GM_groth(self):#毛利成長
        choice = []
        if not self.stock:
            for stock in self.new_data.index:
                if stock in self.old_data.index:
                    if self.new_data.loc[stock]['毛利率(%)(營業毛利)/(營業收入)'] > self.old_data.loc[stock]['毛利率(%)(營業毛利)/(營業收入)']:
                        choice.append(stock)
        else:
            for stock in self.new_data.index:
                if stock in self.old_data.index and stock in self.stock:
                    if self.new_data.loc[stock]['毛利率(%)(營業毛利)/(營業收入)'] > self.old_data.loc[stock]['毛利率(%)(營業毛利)/(營業收入)']:
                        choice.append(stock)
        self.stock[:] = choice
    def PF_groth(self):#營業利益率(%)(營業利益)/(營業收入)
        choice = []
        if not self.stock:
            for stock in self.new_data.index:
                if stock in self.old_data.index:
                    if self.new_data.loc[stock]['營業利益率(%)(營業利益)/(營業收入)'] > self.old_data.loc[stock]['營業利益率(%)(營業利益)/(營業收入)']:
                        choice.append(stock)
        else:
            for stock in self.new_data.index:
                if stock in self.old_data.index and stock in self.stock:
                    if self.new_data.loc[stock]['營業利益率(%)(營業利益)/(營業收入)'] > self.old_data.loc[stock]['營業利益率(%)(營業利益)/(營業收入)']:
                        choice.append(stock)
        self.stock[:] = choice
    def NI_groth(self):#稅後純益
        choice = []
        if not self.stock:
             for stock in self.new_data.index:
                 if stock in self.old_data.index:
                     if self.new_data.loc[stock]['稅後純益率(%)(稅後純益)/(營業收入)'] > self.old_data.loc[stock]['稅後純益率(%)(稅後純益)/(營業收入)']:
                         choice.append(stock)
        else:
            for stock in self.new_data.index:
                if stock in self.old_data.index and stock in self.stock:
                    if self.new_data.loc[stock]['稅後純益率(%)(稅後純益)/(營業收入)'] > self.old_data.loc[stock]['稅後純益率(%)(稅後純益)/(營業收入)']:
                        choice.append(stock)
        self.stock[:] = choice
    def monthly_report(self):
        url = 'https://mops.twse.com.tw/nas/t21/sii/t21sc03_'+str(self.n_year)+'_'+str(self.month)+'.html'
        
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        

        r = requests.get(url, headers=headers)
        r.encoding = 'big5'
        dfs = pd.read_html(StringIO(r.text), encoding='big-5')
    
        df = pd.concat([df for df in dfs if df.shape[1] <= 11 and df.shape[1] > 5])
        
        if 'levels' in dir(df.columns):
            df.columns = df.columns.get_level_values(1)
        else:
            df = df[list(range(0,10))]
            column_index = df.index[(df[0] == '公司代號')][0]
            df.columns = df.iloc[column_index]
        
        df['當月營收'] = pd.to_numeric(df['當月營收'], 'coerce')
        df = df[~df['當月營收'].isnull()]
        df = df[df['公司代號'] != '合計']
        time.sleep(5)
    
        return df
    def monthly_yoy(self):
        cond = self.month_data['去年同月增減(%)'] > 0
        choice = []
        if not self.stock:
            for stock in self.month_data[cond]['公司代號']:
                if stock !='總計':
                    choice.append(stock)
        else:
            for stock in self.month_data[cond]['公司代號']:
                if stock !='總計' and stock in self.stock:
                    choice.append(stock)
        self.stock[:] = choice
    def monthly_mom(self):
        cond = self.month_data['上月比較增減(%)'] > 0
        choice = []
        if not self.stock:
            for stock in self.month_data[cond]['公司代號']:
                if stock !='總計':
                    choice.append(stock)
        else:
            for stock in self.month_data[cond]['公司代號']:
                if stock !='總計' and stock in self.stock:
                    choice.append(stock)
        self.stock[:] = choice
    def choose(self,v1, v2, v3, v4, v5, LB):
        if v1.get() == 1:
            self.GM_groth()
        if v2.get() == 1:
            self.PF_groth()   
        if v3.get() == 1:
            self.NI_groth()
        if v4.get() == 1:
            self.monthly_yoy()
        if v5.get() == 1:
            self.monthly_mom()
        LB.delete(0,'end')#
        LB.insert(tk.END,str('總共找到: '+str(len(self.stock))+'檔股票'))
        for i in self.stock:
            LB.insert(tk.END,i)

    def draw2(self):
        chart = {}
        for i in tqdm(self.stock):
            stock = yf.download(i+".TW", start="2012-09-16", end=self.date, progress=False)
            switch = False
            for d in stock.index:
                if not switch:
                    switch = True
                    start = stock.loc[str(d)[0:10],'Adj Close']
                if str(d)[0:10] not in chart:
                    chart[str(d)[0:10]] = (stock.loc[str(d)[0:10],'Adj Close']-start)/start
                else:
                    chart[str(d)[0:10]] = chart[str(d)[0:10]] + (stock.loc[str(d)[0:10],'Adj Close']-start)/start
                #print(stock.loc[str(d)[0:10],'Close'],start)
        for j in chart.keys():
            chart[j]=chart[j]*100/len(self.stock)
            
        lists = sorted(chart.items()) # sorted by key, return a list of tuples
        x, y = zip(*lists) # unpack a list of pairs into two tuples
        #yy = prof(y)
        fig, ax = plt.subplots(1,1)
        ax.plot(x, y)
        plt.xticks(rotation=90)
        ax.xaxis.set_major_locator(ticker.MultipleLocator(int(len(chart)/12)))
        plt.show()
    def make_window(self):
        window = tk.Tk()
        window.title('選股')
        window.geometry('200x350')
        window.configure(background ='black')
        LB = tk.Listbox(window)
        LB.pack()
        var1 = tk.IntVar()
        tk.Checkbutton(window,text='毛利率成長',variable = var1).pack()
        var2 = tk.IntVar()
        tk.Checkbutton(window,text='淨利率成長',variable = var2).pack()
        var3 = tk.IntVar()
        tk.Checkbutton(window,text='淨益率成長',variable = var3).pack()
        var4 = tk.IntVar()
        tk.Checkbutton(window,text='月營收年成長',variable = var4).pack()
        var5 = tk.IntVar()
        tk.Checkbutton(window,text='月營收月成長',variable = var5).pack()
        tk.Button(window,text='篩選', command =  lambda:self.choose(var1,var2,var3,var4,var5,LB)).pack()
        tk.Button(window,text='績效', command =  lambda:self.draw2()).pack()
        window.mainloop()
view = value_investing(n_year = 109, n_season = 3, o_year = 108, o_season = 3, n_month = 8)
view.make_window()