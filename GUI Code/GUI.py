from PyQt5.QtWidgets import QApplication, QPushButton, QLineEdit, QLabel, QWidget, QSlider, QSpinBox, QComboBox, QMainWindow
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QBrush
from PyQt5.QtCore import Qt, QTimer
from PyQt5 import QtWidgets
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import os
import sys
import re
import threading
import time
import serial
from random import randint

xDials = 750
yDials = 50
spaceX = 300
pom = 1
val = -5
mode = 1
xThrust = xDials
yThrust = yDials
xThrottle = xDials + spaceX
yThrottle = yDials
xRPM = xDials + 2*spaceX
yRPM = yDials
xCurrent = xDials + 3*spaceX
yCurrent = yDials
xRelay = xDials - 320
xSettings = 20
blades = 2
arduino = serial.Serial("COM10", 9600)
throttleSet = 0
thrust = 0
record = -1
running = -1

def convertString(s):
    global time1
    global thrust
    try:
        pattern = "t(.*?)g"
        time1 = int(re.search(pattern, s).group(1))
    except:
        time1 = -1
    
    try:
        pattern = "g(.*?)r"
        thrust1 = re.search(pattern, s).group(1)
    except:
        thrust1 = -1
    
    try:
        pattern = "r(.*?)c"
        rpm = re.search(pattern, s).group(1)
    except:
        rpm = -1
    
    try:
        pattern = "c(.*?)v"
        current = re.search(pattern, s).group(1)
    except:
        current = -1
        
    try:
        pattern = "v(.*?)e"
        voltage = re.search(pattern, s).group(1)
    except:
        voltage = -1    
        
    thrust = int(thrust1)
    print("Current time: " + str(time1))
    print("Current thrust: " + str(thrust))
    print("Current rpm: " + str(rpm))
    print("Current current: " + str(current))
    print("Current voltage: " + str(voltage))
    
    

class App(QWidget):
    
    global val
    global xThrust, yThrust, xThrottle, yThrottle, xRPM, yRPM, xCurrent, yCurrent, xRelay, xDials, yDials, xSettings
    global thrust, record, throttleSet
    
    def __init__(self):       
        super().__init__()
        self.title = 'Thrust Tester'
        self.left = 200
        self.top = 200
        self.width = 1920
        self.height = 1080
        self.qTimer = QTimer()
        self.qTimer.setInterval(50)    
        self.qTimer.timeout.connect(self.updateEvent)
        self.qTimer.timeout.connect(self.update_plot_data)
        self.qTimer.start()
        
        
        
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(25, 35, 40))
        self.setPalette(p)
        
        ### DIAL SECTION
        
        # THRUST DIAL
        self.labelThrust = QLabel(self)
        self.labelThrust.setText(str(thrust))
        self.labelThrust.setGeometry(xThrust + 62, yThrust + 75, 300, 50)
        self.labelThrust.setFont(QFont("Arial", 36))
        self.labelThrust.setStyleSheet("QLabel {color : cyan}")
        
        self.labelThrustName = QLabel(self)
        self.labelThrustName.setText("Thrust [g]")
        self.labelThrustName.setGeometry(xThrust + 20, yThrust + 210, 300, 50)
        self.labelThrustName.setFont(QFont("Arial", 24))
        self.labelThrustName.setStyleSheet("QLabel {color : cyan}")
        
        # Throttle DIAL
        self.labelThrottle = QLabel(self)
        self.labelThrottle.setText(str(-val))
        self.labelThrottle.setGeometry(xThrottle + 75, yThrottle + 75, 300, 50)
        self.labelThrottle.setFont(QFont("Arial", 36))
        self.labelThrottle.setStyleSheet("QLabel {color : rgb(255, 7, 58)}")
        
        self.labelThrottleName = QLabel(self)
        self.labelThrottleName.setText("Throttle [%]")
        self.labelThrottleName.setGeometry(xThrottle + 20, yThrottle + 210, 300, 50)
        self.labelThrottleName.setFont(QFont("Arial", 24))
        self.labelThrottleName.setStyleSheet("QLabel {color : rgb(255, 7, 58)}")
        
        # RPM DIAL
        self.labelRPM = QLabel(self)
        self.labelRPM.setText(str(-val))
        self.labelRPM.setGeometry(xRPM + 62, yRPM + 75, 300, 50)
        self.labelRPM.setFont(QFont("Arial", 36))
        self.labelRPM.setStyleSheet("QLabel {color : rgb(255, 131, 0)}")
        
        self.labelRPMName = QLabel(self)
        self.labelRPMName.setText("RPM [x1000]")
        self.labelRPMName.setGeometry(xRPM + 10, yRPM + 210, 300, 50)
        self.labelRPMName.setFont(QFont("Arial", 24))
        self.labelRPMName.setStyleSheet("QLabel {color : rgb(255, 131, 0)}")
        
        # CURRENT DIAL
        self.labelCurrent = QLabel(self)
        self.labelCurrent.setText(str(-val))
        self.labelCurrent.setGeometry(xCurrent + 75, yCurrent + 75, 300, 50)
        self.labelCurrent.setFont(QFont("Arial", 36))
        self.labelCurrent.setStyleSheet("QLabel {color : rgb(57, 255, 20)}")
        
        self.labelCurrentName = QLabel(self)
        self.labelCurrentName.setText("Current [A]")
        self.labelCurrentName.setGeometry(xCurrent + 20, yCurrent + 210, 300, 50)
        self.labelCurrentName.setFont(QFont("Arial", 24))
        self.labelCurrentName.setStyleSheet("QLabel {color : rgb(57, 255, 20)}")
        
        
        
        
        ### RELAY SECTION
        
        # RELAY NAME
        self.labellRelayName = QLabel(self)
        self.labellRelayName.setText("RELAY")
        self.labellRelayName.setGeometry(xRelay + 30, yDials - 15, 300, 50)
        self.labellRelayName.setFont(QFont("Arial", 43))
        self.labellRelayName.setStyleSheet("QLabel {color : rgb(150, 150, 150)}")
        
        # RELAY STATUS ON
        self.labellRelayStatusON = QLabel(self)
        self.labellRelayStatusON.setText("ON")
        self.labellRelayStatusON.setGeometry(xRelay + 75, yDials + 200, 300, 50)
        self.labellRelayStatusON.setFont(QFont("Arial", 43))
        self.labellRelayStatusON.setStyleSheet("QLabel {color : rgb(150, 150, 150)}")
        self.labellRelayStatusON.setHidden(False)
        
        # RELAY STATUS OFF
        self.labellRelayStatusON = QLabel(self)
        self.labellRelayStatusON.setText("OFF")
        self.labellRelayStatusON.setGeometry(xRelay + 70, yDials + 200, 300, 50)
        self.labellRelayStatusON.setFont(QFont("Arial", 43))
        self.labellRelayStatusON.setStyleSheet("QLabel {color : rgb(150, 150, 150)}")
        self.labellRelayStatusON.setHidden(True)
        
        
        
        
        ### SETTINGS SECTION
        
        # SETTIGNS NAME
        self.labelSettingsName = QLabel(self)
        self.labelSettingsName.setText("SETTINGS")
        self.labelSettingsName.setGeometry(xSettings + 48, yDials - 15, 300, 50)
        self.labelSettingsName.setFont(QFont("Arial", 43))
        self.labelSettingsName.setStyleSheet("QLabel {color : rgb(150, 150, 150)}")
        
        # NUMBER OF BLADES
        self.labelSettingsName = QLabel(self)
        self.labelSettingsName.setText("Number of Blades:")
        self.labelSettingsName.setGeometry(xSettings + 15, yDials + 70, 300, 50)
        self.labelSettingsName.setFont(QFont("Arial", 24))
        self.labelSettingsName.setStyleSheet("QLabel {color : rgb(150, 150, 150)}")
        
        # NUMBER OF BLADES SPINBOX
        self.numberOfBlades = QSpinBox(self)
        self.numberOfBlades.valueChanged.connect(self.bladesValueChange)
        self.numberOfBlades.setRange(2, 5)
        self.numberOfBlades.setGeometry(xSettings + 290, yDials + 70, 70, 50)
        self.numberOfBlades.setFont(QFont("Arial", 30))
        self.numberOfBlades.setValue(2)
        self.numberOfBlades.setStyleSheet("QSpinBox {background-color : rgb(45, 50, 60); color : rgb(150, 150, 150)}")
        
        # MODE BUTTON
        self.buttonMenu = QPushButton("MODE", self)
        self.buttonMenu.resize(100, 50)
        self.buttonMenu.move(xSettings + 15, yDials + 175)
        self.buttonMenu.clicked.connect(self.buttonModeFunction)
        self.buttonMenu.setFont(QFont("Arial", 20))
        self.buttonMenu.setStyleSheet("QPushButton {background-color : rgb(45, 50, 60); color : rgb(150, 150, 150); font-weight: bold}")
        
        # MODE OPTIONS
        self.labelSettingsName = QLabel(self)
        self.labelSettingsName.setText("A        M")
        self.labelSettingsName.setGeometry(xSettings + 145, yDials + 175, 300, 50)
        self.labelSettingsName.setFont(QFont("Arial", 30))
        self.labelSettingsName.setStyleSheet("QLabel {color : rgb(150, 150, 150)}")
        
        
        
        
        ### MANUAL CONTROLS
        
        # NAME
        self.labelManualName = QLabel(self)
        self.labelManualName.setText("MANUAL CONTROLS")
        self.labelManualName.setGeometry(xSettings + 45, yDials + 295 + 10, 600, 50)
        self.labelManualName.setFont(QFont("Arial", 43))
        self.labelManualName.setStyleSheet("QLabel {color : rgb(150, 150, 150)}")
        
        # Throttle
        self.labelManualName = QLabel(self)
        self.labelManualName.setText("Throttle")
        self.labelManualName.setGeometry(xSettings + 15, yDials + 295 + 70 + 30, 600, 50)
        self.labelManualName.setFont(QFont("Arial", 30))
        self.labelManualName.setStyleSheet("QLabel {color : rgb(150, 150, 150)}")
        
        # Slider1
        self.Slider1 = QSlider(Qt.Horizontal, self)
        self.Slider1.setGeometry(xSettings + 170, yDials + 295 + 70 + 30, 360, 50)
        self.Slider1.setRange(0,100)
        self.Slider1.valueChanged[int].connect(self.changeSliderValue)
        
        # Slider1 Label
        self.labelSlider1 = QLabel(self)
        self.labelSlider1.setText(str(throttleSet))
        self.labelSlider1.setGeometry(xSettings + 170 + 390, yDials + 295 + 70 + 30, 67, 50)
        self.labelSlider1.setFont(QFont("Arial", 30))
        self.labelSlider1.setStyleSheet("QLabel {color : rgb(150, 150, 150)}")
        
        # RECORD BUTTON
        self.buttonRecord = QPushButton("RECORD", self)
        self.buttonRecord.resize(150, 50)
        self.buttonRecord.move(xSettings + 15, yDials + 495)
        self.buttonRecord.clicked.connect(self.buttonRecordFunction)
        self.buttonRecord.setFont(QFont("Arial", 20))
        self.buttonRecord.setStyleSheet("QPushButton {background-color : rgb(45, 50, 60); color : rgb(150, 150, 150); font-weight: bold}")
        
        # RECORD LABEL
        self.labelRecord = QLabel(self)
        self.labelRecord.setText("Recording:")
        self.labelRecord.setGeometry(xSettings + 190 , yDials + 495, 400, 50)
        self.labelRecord.setFont(QFont("Arial", 30))
        self.labelRecord.setStyleSheet("QLabel {color : rgb(150, 150, 150)}")
        
        # STOP BUTTON
        self.buttonStop1 = QPushButton("STOP ALL", self)
        self.buttonStop1.resize(150, 50)
        self.buttonStop1.move(xSettings + 475, yDials + 495)
        self.buttonStop1.clicked.connect(self.buttonStopFunction)
        self.buttonStop1.setFont(QFont("Arial", 20))
        #self.buttonStop1.setStyleSheet("QPushButton {background-color : rgb(45, 50, 60); color : rgb(150, 150, 150)}")
        self.buttonStop1.setStyleSheet("QPushButton {background-color : red; color : yellow; font-weight: bold}")
        
        
        
        
        ### AUTO CONTROLS
        
        # NAME
        self.labelManualName = QLabel(self)
        self.labelManualName.setText("AUTO CONTROLS")
        self.labelManualName.setGeometry(xSettings + 80, yDials + 310 + 320, 600, 50)
        self.labelManualName.setFont(QFont("Arial", 43))
        self.labelManualName.setStyleSheet("QLabel {color : rgb(150, 150, 150)}")
        
        # COMBO BOX LABEL
        self.labelRecord = QLabel(self)
        self.labelRecord.setText("Select test:")
        self.labelRecord.setGeometry(xSettings + 15 , yDials + 710, 400, 50)
        self.labelRecord.setFont(QFont("Arial", 30))
        self.labelRecord.setStyleSheet("QLabel {color : rgb(150, 150, 150)}")
        
        # COMBO BOX
        self.testPickComboBox = QComboBox(self)
        self.testPickComboBox.addItems(["Linear Throttle Test", "Speed Up/Down Test", "Responsivness Test", "All Tests Sequentially"])
        self.testPickComboBox.setGeometry(xSettings + 230 , yDials + 710, 390, 50)
        self.testPickComboBox.setFont(QFont("Arial", 20))
        self.testPickComboBox.setStyleSheet("QComboBox {background-color : rgb(45, 50, 60); color : rgb(150, 150, 150)}")
        
        # RUN TEST BUTTON
        self.buttonRunTest = QPushButton("RUN TEST", self)
        self.buttonRunTest.resize(165, 50)
        self.buttonRunTest.move(xSettings + 15, yDials + 800)
        self.buttonRunTest.clicked.connect(self.buttonRunFunction)
        self.buttonRunTest.setFont(QFont("Arial", 20))
        self.buttonRunTest.setStyleSheet("QPushButton {background-color : rgb(45, 50, 60); color : rgb(150, 150, 150); font-weight: bold}")
        
        # RUNNING LABEL
        self.labelRecord = QLabel(self)
        self.labelRecord.setText("Running:")
        self.labelRecord.setGeometry(xSettings + 200 , yDials + 800, 400, 50)
        self.labelRecord.setFont(QFont("Arial", 30))
        self.labelRecord.setStyleSheet("QLabel {color : rgb(150, 150, 150)}")
        
        # STOP BUTTON
        self.buttonStop2 = QPushButton("STOP ALL", self)
        self.buttonStop2.resize(150, 50)
        self.buttonStop2.move(xSettings + 475, yDials + 800)
        self.buttonStop2.clicked.connect(self.buttonStopFunction)
        self.buttonStop2.setFont(QFont("Arial", 20))
        self.buttonStop2.setStyleSheet("QPushButton {background-color : red; color : yellow; font-weight: bold}")
        
        # MESSAGE NAME LABEL
        self.labelMessageName = QLabel(self)
        self.labelMessageName.setText("Message:")
        self.labelMessageName.setGeometry(xSettings + 15 , yDials + 880, 400, 50)
        self.labelMessageName.setFont(QFont("Arial", 30))
        self.labelMessageName.setStyleSheet("QLabel {color : rgb(150, 150, 150)}")
        
        # MESSAGE LABEL
        self.labelMessage = QLabel(self)
        self.labelMessage.setText("")
        self.labelMessage.setGeometry(xSettings + 200 , yDials + 880, 420, 50)
        self.labelMessage.setFont(QFont("Arial", 30))
        self.labelMessage.setStyleSheet("QLabel {background-color : rgb(45, 50, 60); color : rgb(150, 150, 150)}")
        
        
        
        ### GRAPH
        
        self.x = list(range(100))  # 100 time points
        self.y = [randint(0,0) for _ in range(100)]  # 100 data points
        self.y1 = [randint(0,0) for _ in range(100)]
        #self.y = numpy.zeros(100)
        #self.y1 = numpy.zeros(100)
        
        self.graphWidget = pg.PlotWidget(self)
        #self.setCentralWidget(self.graphWidget)
        self.graphWidget.setGeometry(xDials - 50, yDials + 290, 1200, 670)
        self.graphWidget.setBackground(None)
        self.graphWidget.setYRange(0, 100, padding=0.04)
        pen = pg.mkPen(color=(255, 7, 58), width=3)
        
        
        self.graphWidget.getAxis("bottom").setFont(QFont("Arial", 30))
        
        styles = {'color':'rgb(150, 150, 150)', 'font-size':'24px'}
        self.graphWidget.setLabel('left', 'Thrust [%]', **styles)
        self.graphWidget.setLabel('bottom', 'Time [ms]', **styles)

        # plot data: x, y values
        self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pen)
        #self.graphWidget.plot(hour, temperature, pen = pen)
        pen = pg.mkPen(color=(0, 255, 255), width=3)
        self.data_line1 =  self.graphWidget.plot(self.x, self.y1, pen=pen)
        
        
        self.show()
        
        
    def update_plot_data(self):
        global throttleSet, thrust
        self.x = self.x[1:]  # Remove the first y element.
        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.

        self.y = self.y[1:]  # Remove the first 
        self.y.append(throttleSet)  # Add a new random value.
        
        self.y1 = self.y1[1:]  # Remove the first 
        self.y1.append(thrust/1.7)  # Add a new random value.

        self.data_line.setData(self.x, self.y)  # Update the data.
        self.data_line1.setData(self.x, self.y1)  # Update the data.
        
        
    def updateEvent(self):
        self.labelThrust.setText(str(thrust))
        self.labelThrottle.setText(str(throttleSet))
        self.labelRPM.setText(str(-val/10))
        self.labelCurrent.setText(str(-val/10))
        self.update()
        
    def bladesValueChange(self):
        global blades
        blades = self.numberOfBlades.value()
        
    def buttonModeFunction(self):
        global mode
        mode = mode * (-1)
        
    def changeSliderValue(self, value):
        global throttleSet
        throttleSet = value
        print(throttleSet)
        self.labelSlider1.setText(str(value))
        arduino.write(throttleSet.encode())
        
    def buttonRecordFunction(self):
        global record
        record = record * (-1)
        
    def buttonStopFunction(self):
        global record, throttleSet, running
        record = -1
        running = -1
        throttleSet = 0
        self.labelMessage.setText("ABORTED")
        self.Slider1.setValue(0)
        self.labelSlider1.setText(str(0))
        self.updateEvent(self)
        
    def buttonRunFunction(self):
        global running
        running = running * (-1)
        
        
    def paintEvent(self, event):

        global xThrust, yThrust, xThrottle, yThrottle, xRPM, yRPM, xCurrent, yCurrent, xDials, yDials, xRelay, xSettings
        global thrust, throttleSet, record, running
        
        global val
        global pom
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        ### DIALS PAINTING
        
        painter.setPen(QPen(QColor(150, 150, 150), 5))
        painter.drawRect(xDials - 50, yDials - 30, 1200, 300)
        
        painter.setPen(QPen(QColor(45, 50, 60), 20))      
        painter.drawArc(xThrust, yThrust, 200, 200, -90 * 16, 360 * 16)
        painter.drawArc(xThrottle, yThrottle, 200, 200, -90 * 16, 360 * 16)
        painter.drawArc(xCurrent, yCurrent, 200, 200, -90 * 16, 360 * 16)
        painter.drawArc(xRPM, yRPM, 200, 200, -90 * 16, 360 * 16)
              
        painter.setPen(QPen(Qt.cyan, 20))            
        painter.drawArc(xThrust, yThrust, 200, 200, -90 * 16, -thrust * 16)
        
        painter.setPen(QPen(QColor(255, 7, 58), 20))
        painter.drawArc(xThrottle, yThrottle, 200, 200, -90 * 16, -throttleSet * 16 * 3.6)
        
        painter.setPen(QPen(QColor(255, 131, 0), 20))
        painter.drawArc(xRPM, yRPM, 200, 200, -90 * 16, val * 16)
        
        painter.setPen(QPen(QColor(57, 255, 20), 20))
        painter.drawArc(xCurrent, yCurrent, 200, 200, -90 * 16, val * 16)
        
        
        
        ### RELAY STATUS PAINTING
        painter.setPen(QPen(QColor(150, 150, 150), 5))
        painter.drawRect(xRelay, yDials - 30, 250, 300)      
        painter.setBrush(QBrush(QColor(57, 255, 20), Qt.SolidPattern))
        painter.drawEllipse(xRelay + 70, yDials + 60, 110, 110)
        
        
        
        ### SETTINGS PAINTING
        painter.setPen(QPen(QColor(150, 150, 150), 5))
        painter.setBrush(QBrush(Qt.transparent, Qt.SolidPattern))
        painter.drawRect(xSettings, yDials - 30, 390, 300)
        
        if mode == 1:
            painter.drawEllipse(xSettings + 185, yDials + 175, 50, 50)
            painter.setBrush(QBrush(QColor(57, 255, 20), Qt.SolidPattern))
            painter.drawEllipse(xSettings + 185 + 120, yDials + 175, 50, 50)
        else:
            painter.drawEllipse(xSettings + 185 + 120, yDials + 175, 50, 50)
            painter.setBrush(QBrush(QColor(57, 255, 20), Qt.SolidPattern))
            painter.drawEllipse(xSettings + 185, yDials + 175, 50, 50)
            
        
        
        ### MANUAL CONTROLS
        painter.setPen(QPen(QColor(150, 150, 150), 5))
        painter.setBrush(QBrush(Qt.transparent, Qt.SolidPattern))
        painter.drawRect(xSettings, yDials + 290, 660, 300)
        
        if record == 1:
            painter.setBrush(QBrush(QColor(57, 255, 20), Qt.SolidPattern))
        
        painter.drawEllipse(xSettings + 390 , yDials + 495, 50, 50)
        
        
        
        
        
        ### AUTOMATIC CONTROLS
        painter.setPen(QPen(QColor(150, 150, 150), 5))
        painter.setBrush(QBrush(Qt.transparent, Qt.SolidPattern))
        painter.drawRect(xSettings, yDials + 290 + 320, 660, 350)
        
        if running == 1:
            painter.setBrush(QBrush(QColor(57, 255, 20), Qt.SolidPattern))
        
        painter.drawEllipse(xSettings + 375 , yDials + 800, 50, 50)
               
        ### GRAPH
        painter.setPen(QPen(QColor(150, 150, 150), 5))
        painter.setBrush(QBrush(Qt.transparent, Qt.SolidPattern))
        painter.drawRect(xDials - 50, yDials + 290, 1200, 670)
        
        
        
        
        if (val == -360 or val == 0):
            pom = pom * (-1)
        
        if pom == 1:
            val = val - 1
        else:
            val = val + 1
        



def fun1():
    app = QApplication(sys.argv)
    ex = App()
    app.exec_()

   

def fun2():
    while True:
        time.sleep(0.5)
        global arduinoData
        val1 = arduino.readline()
        print(val1)
        convertString(str(val1))
        
        
t1 = threading.Thread(target = fun1)
t2 = threading.Thread(target = fun2)

t1.start()
t2.start()
