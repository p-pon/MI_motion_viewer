
from os import getcwd, path
import sys
import winreg

import tkinter as tk
from tkinter import filedialog
import matplotlib
from itertools import islice
# from scipy import integrate

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


rootPath = getcwd()
initFile = path.join(rootPath, r"IMU\drive_1.csv")
root = tk.Tk()
root.title("Motion viewer")


def readLines():
    RFrom = readFrom.get()
    RTo = readTo.get()
    RStep = readStep.get()
    RColumn1 = readColumn1.get()
    RColumn2 = readColumn2.get()

    with open(filePath.get(), 'r') as f:
        data = list(zip(*map(lambda x: (float(x[RColumn1 - 1]), float(x[RColumn2 - 1])),
                             map(lambda x: x[:-1].split(";"), islice(f, RFrom, RTo, RStep)))))

    axisX = list(range(RFrom, RTo, RStep))

    updateGraph(axisX, data)


def updateGraph(axisX, data):
    global fig
    fig.clear()
    ax = fig.subplots()
    len_data = len(data[0])
    if readColumn1.get() > 0:
        # print(axisX[:len_data])
        ax.tick_params(axis='y', labelcolor="tab:blue")
        ax.plot(axisX[:len_data], data[0])

    if isIntegrate.get():
        IntegratedData = []
        integral = 0.0
        for i in range(len_data):
            integral += data[0][i]
            IntegratedData.append(integral)
        ax3 = ax.twinx()
        ax3.tick_params(axis='y', labelcolor="tab:orange")
        ax3.plot(axisX[:len_data], IntegratedData, color="tab:orange")

    if readColumn2.get() > 0:
        ax2 = ax.twinx()
        ax2.tick_params(axis='y', labelcolor="tab:red")
        ax2.plot(axisX[:len_data], data[1], color="tab:red")

    fig.canvas.draw()


def selectFile():
    filepath = filedialog.askopenfilename(title="Open File", initialfile=initFile)
    if filepath != "":
        filePath.set(filepath)


def loadValues():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'software\MI_motion_viewer', access=winreg.KEY_READ)
        filePath.set(winreg.QueryValueEx(key, 'filePath')[0])
        readFrom.set(winreg.QueryValueEx(key, 'readFrom')[0])
        readTo.set(winreg.QueryValueEx(key, 'readTo')[0])
        readStep.set(winreg.QueryValueEx(key, 'readStep')[0])
        readColumn1.set(winreg.QueryValueEx(key, 'column1')[0])
        readColumn2.set(winreg.QueryValueEx(key, 'column2')[0])
        isIntegrate.set(winreg.QueryValueEx(key, 'isIntegrate')[0])
        winreg.CloseKey(key)
    except FileNotFoundError:
        pass


def Exit():
    global root
    matplotlib.pyplot.close()

    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software')
    winreg.CreateKey(key, 'MI_motion_viewer')
    winreg.CloseKey(key)

    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'software\MI_motion_viewer', access=winreg.KEY_WRITE)
    winreg.SetValueEx(key, 'filePath', None, winreg.REG_SZ, filePath.get())
    winreg.SetValueEx(key, 'readFrom', None, winreg.REG_DWORD, readFrom.get())
    winreg.SetValueEx(key, 'readTo', None, winreg.REG_DWORD, readTo.get())
    winreg.SetValueEx(key, 'readStep', None, winreg.REG_DWORD, readStep.get())
    winreg.SetValueEx(key, 'column1', None, winreg.REG_DWORD, readColumn1.get())
    winreg.SetValueEx(key, 'column2', None, winreg.REG_DWORD, readColumn2.get())
    winreg.SetValueEx(key, 'isIntegrate', None, winreg.REG_DWORD, int(isIntegrate.get()))
    winreg.CloseKey(key)
    root.destroy()


matplotlib.use('TkAgg')  # This defines the Python GUI backend to use for matplotlib
fig = plt.figure(figsize=(16, 8))  # Initialize matplotlib figure for graphing purposes
canvas = FigureCanvasTkAgg(fig, master=root)  # Special type of "canvas" to allow for matplotlib graphing

plot_widget = canvas.get_tk_widget()
plot_widget.grid(row=0, column=0, columnspan=11)  # Add the plot to the tkinter widget
filePath = tk.StringVar(value=getcwd())
tk.Label(root, text='File Path').grid(row=1, column=0, sticky='s')
tk.Entry(root, width=80, textvariable=filePath).grid(row=2, column=0, sticky='sw')
tk.Button(root, text="...", command=selectFile).grid(row=2, column=0, sticky='e')

readFrom = tk.IntVar(value=0)
tk.Label(root, text='Read From').grid(row=1, column=2, sticky='s')
tk.Spinbox(root, from_=1, to=999999, textvariable=readFrom).grid(row=2, column=2, sticky='s')

readTo = tk.IntVar(value=100000)
tk.Label(root, text='Read To').grid(row=1, column=3, sticky='s')
tk.Spinbox(root, from_=0, textvariable=readTo).grid(row=2, column=3, sticky='s')

readStep = tk.IntVar(value=1)
tk.Label(root, text='Read Step').grid(row=1, column=4, sticky='s')
tk.Spinbox(root, from_=0, textvariable=readStep, increment=1).grid(row=2, column=4, sticky='s')

readColumn1 = tk.IntVar(value=1)
tk.Label(root, text='Take Column 1').grid(row=1, column=5, sticky='s')
tk.Spinbox(root, from_=0, textvariable=readColumn1).grid(row=2, column=5, sticky='s')

readColumn2 = tk.IntVar(value=0)
tk.Label(root, text='Take Column 2').grid(row=1, column=7, sticky='s')
tk.Spinbox(root, from_=0, textvariable=readColumn2).grid(row=2, column=7, sticky='s')

isIntegrate = tk.BooleanVar(value=False)
tk.Checkbutton(root, variable=isIntegrate, text='Integrate').grid(row=2, column=6, sticky='s')

tk.Button(root, text="Read", command=readLines).grid(row=1, column=10, sticky='ew')
loadValues()

# start Tk
root.protocol("WM_DELETE_WINDOW", Exit)  # Close window handler
root.mainloop()

sys.exit()
