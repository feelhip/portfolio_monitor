# This Python file uses the following encoding: utf-8
import sys
import os

from PySide2 import QtGui
from PySide2.QtGui import QColor, QPainter
from PySide2.QtWidgets import *
from PySide2 import QtCore,QtGui, QtWidgets
from PySide2.QtWidgets import QApplication, QWidget, QMessageBox
from PySide2.QtCore import QFile
from PySide2.QtCore import QTimer
from PySide2.QtUiTools import QUiLoader
from websocket import create_connection
from PySide2.QtCharts import QtCharts
import json
import pandas as pd
import time
from datetime import datetime
import threading
from PySide2.QtGui import *
from PySide2.QtCore import *
import logging
from liveportfolionominals import LivePortfolioNominals
from getsqldata import getsqldata
from playsound import playsound


import traceback, sys


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])


class WorkerSignals(QObject):

    finished = Signal()  # QtCore.Signal
    error = Signal(tuple)
    result = Signal(object)




class Worker(QRunnable):
    '''
    Worker thread
    '''

    def __init__(self, *args, **kwargs):
        super(Worker, self).__init__()
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()





    @Slot()  # QtCore.Slot
    def run(self):

        #print("Thread start")
        #print (self.args)

        while True:
            jsonResponse = self.args[0].recv()
            print('JSON response: ')
            print(jsonResponse)
            arrayResponse = json.loads(jsonResponse)

            if 'event' not in arrayResponse:
                price_data = [arrayResponse[1][5],arrayResponse[3]]
                print("Price data: "+str(price_data))
                self.signals.result.emit(price_data)
                break

        #print("Thread complete")




class main(QWidget):

    @Slot()
    def manage_alarm(self):
        if self.ten_min_mva_alarm_active == False:
            self.ten_min_mva_alarm_active = True
            self.mva_alarm_btn.setStyleSheet("background-color: rgb(0, 255, 0)")



    minPrice = 1000000
    maxPrice = 0
    def __init__(self):
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
        super(main, self).__init__()
        self.load_ui()



    def refreshLiveData(self,ws):
        worker = Worker(ws)
        self.threadpool.start(worker)
        worker.signals.result.connect(self.updateComponents)





    def updateComponents(self, s):



        price_float = float(s[0])

        #print("Thread output: "+str(s))


        #Update Portfolio Table

        ptf_total_usd_value=float(0)

        #portfolioNominalsObj = LivePortfolioNominals()
        portfolio_nominals_dict = self.portfolioNominals.get_nominals()
        new_table_data =[]

        ws_pair = s[1]
        #print ("WebSocket response pair: "+str (ws_pair))

        ptf_size = len(self.old_ptf_table_data)



        for asset, old_ptf_data in zip(portfolio_nominals_dict,self.old_ptf_table_data):

            if asset == 'ZUSD':
                portfolio_nominals_dict[asset]
                new_table_data.append([asset, portfolio_nominals_dict[asset], portfolio_nominals_dict[asset],portfolio_nominals_dict[asset]])
                ptf_total_usd_value = ptf_total_usd_value + float(portfolio_nominals_dict[asset])

                continue


            ptf_pair = self.ledger_ws_assets_codes[asset]
            print ('Portfolio Pair: '+str(ptf_pair))

            if (price_float!=old_ptf_data[2] and ws_pair == ptf_pair+"/USD"):
                new_table_data.append([asset,portfolio_nominals_dict[asset],price_float,price_float*float(portfolio_nominals_dict[asset])])
                ptf_total_usd_value = ptf_total_usd_value+price_float*float(portfolio_nominals_dict[asset])
                self.price_update_counter = self.price_update_counter + 1
            else:
                new_table_data.append([asset, portfolio_nominals_dict[asset], old_ptf_data[2],float(old_ptf_data[2])*float( portfolio_nominals_dict[asset])])
                ptf_total_usd_value = ptf_total_usd_value + float(old_ptf_data[2])*float( portfolio_nominals_dict[asset])
        model = TableModel(new_table_data)

        self.portfolio_table_view.setModel(model)
        self.portfolio_table_view.show()

        self.old_ptf_table_data = new_table_data





        if self.price_update_counter >=ptf_size : #Only update charts when all assets are updated at least twice
            # Total Portfolio Value

            self.ptf_total_value_label.setText(str(ptf_total_usd_value))

            # Moving Average Portfolio Value
            self.ptf_values_list.append(ptf_total_usd_value)

            ptf_value_updates_count = len(self.ptf_values_list)

            if ptf_value_updates_count>600:
                del self.ptf_values_list [0]

            cumulated_ptf_value =0
            for ptf_value in  self.ptf_values_list:
                cumulated_ptf_value = cumulated_ptf_value+ptf_value

            average_ptf_value = cumulated_ptf_value/ptf_value_updates_count

            self.ptf_10min_mva_label.setText(str(average_ptf_value))


            #Alerts
            if ptf_total_usd_value <= average_ptf_value*0.9 and  self.ten_min_mva_alarm_active == True:
                playsound('alarm.mp3')
                self.ten_min_mva_alarm_active = False
                self.mva_alarm_btn.setStyleSheet("background-color: red")


            # Update Chart

            self.minPrice = min(self.minPrice, ptf_total_usd_value)
            self.maxPrice = max(self.maxPrice, ptf_total_usd_value)




            self.chart.removeSeries(self.series)

            dt = QtCore.QDateTime.currentDateTime()
            # print("Append data in series")
            # print(dt.toMSecsSinceEpoch())
            self.series.append(float(dt.toMSecsSinceEpoch()), ptf_total_usd_value)
            # print("Add Series to chart")
            self.chart.addSeries(self.series)
            self.chart.removeAxis(self.axis_x)
            self.chart.removeAxis(self.axis_y)

            self.axis_x = QtCharts.QDateTimeAxis()
            self.axis_x.setTickCount(10)
            self.axis_x.setLabelsAngle(70)
            self.axis_x.setFormat("dd.MM.yy h:mm:ss")
            self.axis_x.setFormat("hh:mm:ss")
            self.axis_x.setTitleText("Date")
            self.axis_x.setMax(QtCore.QDateTime.currentDateTime().addSecs(10))
            self.axis_x.setMin(QtCore.QDateTime.currentDateTime().addSecs(-3600))
            self.axis_y = QtCharts.QValueAxis()
            self.axis_y.setTickCount(7)
            self.axis_y.setLabelFormat("%i")
            self.axis_y.setTitleText("Price")
            self.axis_y.setMax(self.maxPrice + 5)
            self.axis_y.setMin(self.minPrice - 5)
            self.chart.setAxisX(self.axis_x, self.series)
            self.chart.setAxisY(self.axis_y, self.series)


    def load_ui(self):


        loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__), "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        ui = loader.load(ui_file, self)

        self.ptf_10min_mva_label =ui.ptf_10min_mva_QLabel

        self.price_update_counter = 0
        self.ptf_update_counter = 0
        self.ptf_values_list =[]

        getSqlData = getsqldata()
        self.ledger_ws_assets_codes = getSqlData.get_live_json_codes_dict()

        self.ptf_total_value_label = ui.ptf_usd_value_QLbl
        self.ptf_total_value_label.setText("Updating...")

        #Config Buttons
        self.mva_alarm_btn = ui.mva_alarm_QPButton
        self.mva_alarm_btn.clicked.connect(self.manage_alarm)

        #Set Alarms
        self.ten_min_mva_alarm_active = True


        #Portfolio Table

        self.portfolioNominals = LivePortfolioNominals()
        portfolio_nominals_dict = self.portfolioNominals.get_nominals()
        self.table_data =[]
        for asset in portfolio_nominals_dict:
            self.table_data.append([asset,portfolio_nominals_dict[asset],0,0])

        self.model = TableModel(self.table_data)
        self.portfolio_table_view = ui.ptfTableView
        self.portfolio_table_view.setModel(self.model)
        self.portfolio_table_view.show()
        self.old_ptf_table_data =  self.table_data
        #ui.price_label.setText(str(0))




        #Websocket Connections

        try:
            print ("Try to create websocket connection")
            self.ws = create_connection("wss://ws.kraken.com/")
            self.ws.send('{ "event": "subscribe", "pair": ["BTC/USD"], "subscription": { "name": "ohlc", "interval":1}}') #can add a reqid. Ex: ,"reqid":123'

            print("Create multiple WS queries")
            for asset in portfolio_nominals_dict:
                if asset=='ZUSD':
                    continue

                ptf_pair = self.ledger_ws_assets_codes[asset]
                subscription_req = '{ "event": "subscribe", "pair": ["%s/USD"], "subscription": { "name": "ohlc", "interval":1}}'%(ptf_pair)
                print ("Subsctiption request: " + subscription_req)
                self.ws.send(subscription_req)
        except Exception as e:
            print ("ERROR")
            print (e)


        #Chart

        print("Create chart")
        self.chart = QtCharts.QChart()
        print("Chart Created")
        #self.chart.setAnimationOptions(QtCharts.QChart.AllAnimations)
        self.series = QtCharts.QLineSeries()
        self.series.setName("Portfolio USD Value")
        dt = QtCore.QDateTime.currentDateTime()
        self.chart.addSeries(self.series)
        print("Create axis")
        self.axis_x = QtCharts.QDateTimeAxis()
        self.axis_x.setTickCount(10)
        self.axis_x.setLabelsAngle(70)
        #self.axis_x.setFormat("dd.MM.yy h:mm:ss")
        self.axis_x.setFormat("hh:mm:ss")
        self.axis_x.setTitleText("Date")
        self.axis_x.setMax(QtCore.QDateTime.currentDateTime().addSecs(10))
        self.axis_x.setMin(QtCore.QDateTime.currentDateTime().addSecs(-3600))
        self.axis_y = QtCharts.QValueAxis()
        self.axis_y.setTickCount(7)
        self.axis_y.setLabelFormat("%i")
        self.axis_y.setTitleText("Price")
        self.axis_y.setMax(10)
        self.axis_y.setMin(0)

        print("Set axis to chart")
        self.chart.setAxisX(self.axis_x, self.series)
        self.chart.setAxisY(self.axis_y, self.series)

        self.chartView = QtCharts.QChartView(self.chart)
        self.chartView.setRenderHint(QPainter.Antialiasing)

        ui.chartLayout.addWidget(self.chartView)



        timer = QTimer(self)
        self.connect(timer, QtCore.SIGNAL("timeout()"), (lambda: self.refreshLiveData(self.ws)))
        timer.start(1000)
        ui_file.close()




    def getNowQDateTime(self):
        currentTime = datetime.now()
        currentTimeFormat = "yyyy-MM-dd HH:mm:ss.zzz"
        new_date = QDateTime().fromString(currentTime.strftime(currentTimeFormat), currentTimeFormat)
        return str(new_date)





if __name__ == "__main__":
    app = QApplication([])
    widget = main()
    widget.show()
    sys.exit(app.exec_())
