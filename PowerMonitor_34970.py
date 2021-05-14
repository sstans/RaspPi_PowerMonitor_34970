import PySimpleGUI as sg
import matplotlib.pyplot as plt
import csv
import pyvisa #as visa
from datetime import datetime

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

# Setup parameters for measurement
gpib_address = '09'
scan_list = '300, 301, 302, 303, 304. 305'
filefieldnames = ['Timestamp', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'I1', 'I2', 'I3', 'I4', 'I5', 'I6'] # Sense voltages (may be named if desired)
rsense = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
runnumber = 1
filename = datetime.now().strftime("%Y%m%d-%H%M%S") + "_RadFacility" 
print(filename)
with open(filename + '.csv', 'w') as csvfile:
    writer = csv.writer(csvfile,
                        escapechar = 'X',
                        lineterminator='\n')
    writer.writerow(filefieldnames)

    inst = rm.open_resource('GPIB0::' + gpib_address + '::INSTR')
    #print(inst.query("*IDN?"))
    configure_command = 'CONF:VOLT:DC 2'
    #display_command = "DISPlay:TEXT:'SCANNING'"
    #displayclear_command = 'DISP;TEXT:CLEAR'
    inst.write('*RST')
    inst.write('*CLS')

    #layout = [[sg.Button('Plot'), sg.Cancel(), sg.Button('Popup')]]
    layout = [[sg.Button('Done'), sg.Cancel()]]
    window = sg.Window('Current Monitoring Control', layout)

    voltagedata = []
    currentdata = []
    #initialtimestamp = datetime.datetime.now().timestamp()
    initialtimestamp = 0
    while True:
        inst.write("MEAS:VOLT:DC? 10, (@301:305)")
        channeldata = inst.read()
        timestamp = datetime.now().timestamp() - initialtimestamp
                    # write last read value into
        #rowdata = ','.join([str(timestamp), channeldata])
        #print(rowdata, type(rowdata))
        #print(str(timestamp))
        #print(channeldata)
        rowdata = str(timestamp) + ", " + channeldata
        print(rowdata)
        writer.writerow([rowdata])

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
        elif event == 'Done':
            #Close file
            break
        elif event == 'Popup':
            sg.popup('Yes, your application is still running')
        else:
            plt.clf()
            # Below uses generators to build plotdata.   Single loop is trickier.
            # Need to use append or some other method.  Leave non-pythonic for now.
            xdata = [a[0] for a in currentdata[-10:]]
            ydata1 = [a[1] for a in currentdata[-10:]]
            ydata2 = [a[2] for a in currentdata[-10:]]
            ydata3 = [a[3] for a in currentdata[-10:]]
            ydata4 = [a[4] for a in currentdata[-10:]]
            ydata5 = [a[5] for a in currentdata[-10:]]
            plt.plot(xdata, ydata1, 'ro-')
            plt.plot(xdata, ydata1, 'bo-')
            plt.plot(xdata, ydata2, 'go-')
            plt.plot(xdata, ydata3, 'o-')
            plt.plot(xdata, ydata4, 'o-')
            plt.plot(xdata, ydata5, 'o-')
            plt.show(block=False)
            # write last read value to file
#            writer.writerow([xdata[-1], ydata1[-1], ydata2[-1], ydata3[-1], ydata4[-1], ydata5[-1]])
            #writer.writerow(str(xdata), str(ydata1)) #, ydata2, ydata3, ydata4, ydata5)
            
    window.close()
