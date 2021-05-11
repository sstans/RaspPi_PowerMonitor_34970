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
rsense = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1]

inst = rm.open_resource('GPIB0::' + gpib_address + '::INSTR')
print(inst.query("*IDN?"))

configure_command = 'CONF:VOLT:DC 2'
display_command = "DISPlay:TEXT:'SCANNING'"
displayclear_command = 'DISP;TEXT:CLEAR'

#print(display_command)
inst.write('*RST')
inst.write('*CLS')
voltagedata =[]


layout = [[sg.Button('Plot'), sg.Cancel(), sg.Button('Popup')]]

window = sg.Window('Have some Matplotlib....', layout)

plotdata = [0.1, 0.2, 0.5, 0.7]
while True:
    inst.write("MEAS:VOLT:DC? 10, (@301:305)")
    #print(inst.read())
    #print(inst.write("INIT"))
    channeldata = inst.read()
    timestamp = datetime.datetime.now().timestamp()
    #print(channeldata)
    parsedvoltages = []
    for row in csv.reader([channeldata]):
        #print(row)
        parsedvoltages.append(row[0])
    
    voltagedata.append(timestamp)
    for i in parsedvoltages:
        voltagedata.append(float(i))
        
    #draw_plot(parsedvoltages)
    event, values = window.read(timeout=100)
    if event in (sg.WIN_CLOSED, 'Cancel'):
        break
    elif event == 'Plot':
        draw_plot(plotdata)
    elif event == 'Popup':
        sg.popup('Yes, your application is still running')
    else:
        print(parsedvoltages[0][0])
        print(voltagedata[-10:])
        print('---')
        draw_plot(voltagedata[:])
window.close()