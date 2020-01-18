import gi
import serial
import sys
import glob
import threading
import time
from gi.repository import GLib, Gtk, GObject
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from serial.tools.list_ports import comports

builder = Gtk.Builder()
builder.add_from_file("serialconsole.glade")

port: serial.Serial
baud = 9600
portName = ""

class EventHandler:
    def __init__(self, builder):
        self.builder = builder

    def onBaudComboChanged(self, combo):
        currentIter = combo.get_active_iter()
        if currentIter is not None:
            model = combo.get_model()
            baud = model[currentIter][0]
            print("Selected: baud=" + str(baud))
            port = serial.Serial("/dev/pts/5", baud, timeout=1)
            port.open()

    def onPortComboChanged(self, combo):
        currentIter = combo.get_active_iter()
        if currentIter is not None:
            model = combo.get_model()
            portName = model[currentIter][0]
            print("Selected: portName=" + str(portName))
            port = serial.Serial("/dev/pts/5", baud, timeout=1)
            port.open()

def serial_ports():
    ports = comports()

    result = []
    for port in ports:
        try:
            s = serial.Serial("/dev/" + port.description)
            s.close()
            result.append(port.description)
        except (OSError, serial.SerialException):
            print("oof")
            pass
    return result

builder.connect_signals(EventHandler(builder))

baudCombo = builder.get_object("baudCombo")
portCombo = builder.get_object("portCombo")

baudStore = Gtk.ListStore(int)
portStore = Gtk.ListStore(str)

baud = [
    300,
    600,
    1200,
    2400,
    4800,
    9600,
    14400,
    19200,
    28800,
    31250,
    38400,
    57600,
    115200
]

ports = serial_ports()

for b in baud:
    baudStore.append([b])

for p in ports:
    portStore.append([p])

baudCombo.set_model(baudStore)
portCombo.set_model(portStore)
renderer_text = Gtk.CellRendererText()
baudCombo.pack_start(renderer_text, True)
baudCombo.add_attribute(renderer_text, "text", 0)
portCombo.pack_start(renderer_text, True)
portCombo.add_attribute(renderer_text, "text", 0)

baudCombo.set_active(5)
portCombo.set_active(0)

listBox = builder.get_object("contentList")

def add_line(line):
    label = Gtk.Label.new(line)
    label.set_halign(Gtk.Align.START)
    listBox.insert(label, 0)

def main_loop():
    while True:
        line = ""

        try:
            line = port.read_line()
        except (NameError):
            line = ""
        
        GLib.idle_add(add_line, line)
        time.sleep(0.2)

thread = threading.Thread(target=main_loop)
thread.daemon = True
thread.start()

win = builder.get_object("mainWindow")
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()