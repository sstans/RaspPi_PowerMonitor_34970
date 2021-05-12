import PySimpleGUI as sg
import matplotlib.pyplot as plt
import csv
import pyvisa #as visa
import datetime

"""
    Adapted from pySimpleGui demo code:
    Simultaneous PySimpleGUI Window AND a Matplotlib Interactive Window
    A number of people have requested the ability to run a normal PySimpleGUI window that
    launches a MatplotLib window that is interactive with the usual Matplotlib controls.
    It turns out to be a rather simple thing to do.  The secret is to add parameter block=False to plt.show()
"""

def draw_plot(plotdata):
    # plt.plot([0.1, 0.2, 0.5, 0.7])
    plt.plot(plotdata)
    plt.show(block=False)
    
def calc_current(voltagedrop, rsense):
    return voltagedrop/rsense

rm = pyvisa.ResourceManager('@py')
#rm.list_resources()

gpib_address = '09'
scan_list = '300, 301, 302, 303, 304. 305'
fieldnames = 'V1, V2, V3, V4, V5, V6' # Sense voltages (may be named if desired)
rsense = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1]

inst = rm.open_resource('GPIB0::' + gpib_address + '::INSTR')
print(inst.query("*IDN?"))

configure_command = 'CONF:VOLT:DC 2'
display_command = "DISPlay:TEXT:'SCANNING'"
displayclear_command = 'DISP;TEXT:CLEAR'

#print(display_command)
inst.write('*RST')
inst.write('*CLS')

layout = [[sg.Button('Plot'), sg.Cancel(), sg.Button('Popup')]]

window = sg.Window('Have some Matplotlib....', layout)

voltagedata = []
currentdata = []
#initialtimestamp = datetime.datetime.now().timestamp()
initialtimestamp = 0
while True:
    inst.write("MEAS:VOLT:DC? 10, (@301:305)")
    channeldata = inst.read()
    timestamp = datetime.datetime.now().timestamp() - initialtimestamp
    parsedvoltages = [timestamp]
    parsedcurrents = [timestamp]
    for count, value in enumerate(list(csv.reader([channeldata]))[0]):
        parsedcurrents.append(float(value)/rsense[count])
        parsedvoltages.append(float(value))  
    voltagedata.append(parsedvoltages)
    currentdata.append(parsedcurrents)
    event, values = window.read(timeout=100)
    if event in (sg.WIN_CLOSED, 'Cancel'):
        break
    elif event == 'Plot':
        draw_plot(plotdata)
    elif event == 'Popup':
        sg.popup('Yes, your application is still running')
    else:
        plt.clf()
        xdata = [a[0] for a in currentdata[-10:]]
        ydata1 = [a[1] for a in currentdata[-10:]]
        ydata2 = [a[2] for a in currentdata[-10:]]
        ydata3 = [a[3] for a in currentdata[-10:]]
        ydata4 = [a[4] for a in currentdata[-10:]]
        ydata5 = [a[5] for a in currentdata[-10:]]
        plt.plot(xdata, ydata1, 'ro-')
        plt.plot(xdata, ydata1, 'bo-')
        plt.plot(xdata, ydata2, 'go-')
        plt.plot(xdata, ydata3, '-')
        plt.plot(xdata, ydata4, '-')
        plt.plot(xdata, ydata5, '-')
        plt.show(block=False)
window.close()