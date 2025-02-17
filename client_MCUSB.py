from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import sys
import h5py

## Always start by initializing Qt (only once per application)
app = QApplication(sys.argv)

## Define a top-level widget to hold everything
window = QWidget()
window.setWindowTitle('MCUSB Client')

## Create some widgets to be placed inside
panels = QTabWidget()

# Analog Wave Variables
waveform = 'Square'
wave_offset = 0
wave_frequency = 10
wave_shift = 0
wave_amplitude = 1
custom_file = None
wave_io_type = 'Single'
waveform2 = 'Square'
wave_offset2 = 0
wave_frequency2 = 10
wave_shift2 = 0
wave_amplitude2 = 1
custom_file2 = None
multiple_wave_types = False
analogOut_channels = []
analogIn_channels = []
analog_chans_plot = []

# Digital Wave Variables
digital_waveform = 'Sine'
digital_wave_offset = 0
digital_wave_frequency = 10
digital_wave_shift = 0
digital_wave_amplitude = 10
digital_wave_io_type = 'Continuous'
active_digital_channels = []
active_digitalIn_channels = []

sample_rate = 1000
t_buffer = None

class AnalogConfigTab (QWidget) :
    #Channel Options of Tab
    channel_section_label = QLabel("Available Channels:")
    channel_0_label = QLabel("Channel 0:")
    channel_0_box = QCheckBox("On?")
    channel_1_label = QLabel("Channel 1:")
    channel_1_box = QCheckBox("On?")
    #Waveform Options of Tab
    waveform_type_label = QLabel("Wave Type")
    waveform_type_box = QComboBox()
    waveform_type_box2 = QComboBox()
    waveform_frequency_label = QLabel("Frequency (Hz):")
    waveform_frequency_textline = QLineEdit('10')
    waveform_frequency_textline2 = QLineEdit('10')
    waveform_shift_label = QLabel("Phase Shift (Radians):")
    waveform_shift_textline = QLineEdit('0')
    waveform_shift_textline2 = QLineEdit('0')
    waveform_amplitude_label = QLabel("Amplitude (V):")
    waveform_amplitude_textline = QLineEdit('1')
    waveform_amplitude_textline2 = QLineEdit('1')
    custom_file_label = QLabel("If using a file input, please type it below:")
    custom_file_textline = QLineEdit('YourFileName.xlsx')
    custom_file_textline2 = QLineEdit('YourFileName.xlsx')
    waveform_y_label = QLabel("Y-Offset (V)")
    waveform_y_textline = QLineEdit('0')
    waveform_y_textline2 = QLineEdit('0')
    type_output_label = QLabel('Type of Output:')
    type_output_box = QComboBox()
    multiple_waves = QCheckBox('Multiple Waveforms?')
    # Wave Buttons
    generate_button = QPushButton("Generate Wave")
    stop_button = QPushButton("Stop Wave")
    
    
    layout = None
    
    #Initialization of Dropdown Menus
    waveform_type_box.addItem("Square")
    waveform_type_box.addItem("Pulse")
    waveform_type_box.addItem("Sawtooth")
    waveform_type_box.addItem("Sine")
    waveform_type_box.addItem("Custom")
    waveform_type_box2.addItem("Square")
    waveform_type_box2.addItem("Pulse")
    waveform_type_box2.addItem("Sawtooth")
    waveform_type_box2.addItem("Sine")
    waveform_type_box2.addItem("Custom")
    type_output_box.addItem('Single')
    type_output_box.addItem('Continuous')
    
    def __init__(self):
        super().__init__()
        self.layout = QGridLayout()
        layout = self.layout
        self.setLayout(layout)
        #Add Widgets
        layout.addWidget(self.channel_section_label,0,0)
        layout.addWidget(self.channel_0_label,1,0)
        layout.addWidget(self.channel_0_box,1,1)
        layout.addWidget(self.channel_1_label,2,0)
        layout.addWidget(self.channel_1_box,2,1)
        layout.addWidget(self.waveform_type_label,5,0)
        layout.addWidget(self.waveform_type_box,6,0)
        layout.addWidget(self.waveform_frequency_label,9,0)
        layout.addWidget(self.waveform_frequency_textline,10,0)
        layout.addWidget(self.waveform_amplitude_label,11,0)
        layout.addWidget(self.waveform_amplitude_textline,12,0)
        layout.addWidget(self.waveform_shift_label,13,0)
        layout.addWidget(self.waveform_shift_textline,14,0)
        layout.addWidget(self.waveform_y_label,15,0)
        layout.addWidget(self.waveform_y_textline,16,0)
        layout.addWidget(self.type_output_label,17,0)
        layout.addWidget(self.type_output_box,18,0)
        layout.addWidget(self.multiple_waves,19,0)
        layout.addWidget(self.generate_button,20,0)
        layout.addWidget(self.stop_button,21,0)
        
        #Add Listeners
        self.waveform_type_box.activated.connect(self.UpdateWaveform)
        self.waveform_frequency_textline.textChanged.connect(self.UpdateWaveformFreq)
        self.waveform_shift_textline.textChanged.connect(self.UpdateWaveformShift)
        self.waveform_amplitude_textline.textChanged.connect(self.UpdateWaveformAmplitude)
        self.waveform_y_textline.textChanged.connect(self.UpdateOffset)
        self.type_output_box.activated.connect(self.UpdateOutputType)
        self.multiple_waves.stateChanged.connect(self.MultipleWavesSetup)
        self.channel_1_box.stateChanged.connect(self.UpdateChannels)
        self.channel_0_box.stateChanged.connect(self.UpdateChannels)
        self.generate_button.clicked.connect(self.on_generate_button_clicked)
        self.stop_button.clicked.connect(self.on_wave_stop_clicked)
        
    def MultipleWavesSetup(self):
        layout = self.layout
        global multiple_wave_types
        if self.multiple_waves.isChecked():
            layout.addWidget(self.waveform_type_box2,6,1)
            layout.addWidget(self.waveform_frequency_textline2,10,1)
            layout.addWidget(self.waveform_amplitude_textline2,12,1)
            layout.addWidget(self.waveform_shift_textline2,14,1)
            layout.addWidget(self.waveform_y_textline2,16,1)
            multiple_wave_types = True
            self.waveform_type_box2.activated.connect(self.UpdateWaveform2)
            self.waveform_frequency_textline2.textChanged.connect(self.UpdateWaveformFreq)
            self.waveform_shift_textline2.textChanged.connect(self.UpdateWaveformShift)
            self.waveform_amplitude_textline2.textChanged.connect(self.UpdateWaveformAmplitude)
            self.waveform_y_textline2.textChanged.connect(self.UpdateOffset)
        else:
            self.waveform_type_box2.setParent(None)
            self.waveform_frequency_textline2.setParent(None)
            self.waveform_amplitude_textline2.setParent(None)
            self.waveform_shift_textline2.setParent(None)
            self.waveform_y_textline2.setParent(None)
            multiple_wave_types = False
    def UpdateWaveform(self):
        global waveform
        waveform = self.waveform_type_box.currentText()
        if waveform == "Custom":
            self.layout.addWidget(self.custom_file_label,7,0)
            self.layout.addWidget(self.custom_file_textline,8,0)
            self.custom_file_textline.textChanged.connect(self.UpdateCustomFile)
        else:
            self.custom_file_label.setParent(None)
            self.custom_file_textline.setParent(None)
    def UpdateWaveform2(self):
        global waveform2
        waveform2 = self.waveform_type_box2.currentText()
        if waveform2 == "Custom":
            self.layout.addWidget(self.custom_file_textline2,7,1)
            self.custom_file_textline2.textChanged.connect(self.UpdateCustomFile2)
        else:
            self.custom_file_textline2.setParent(None)
    def UpdateWaveformFreq(self):
        global wave_frequency
        wave_frequency = self.waveform_frequency_textline.text()
        if self.multiple_waves.isChecked():
            global wave_frequency2
            wave_frequency2 = self.waveform_frequency_textline2.text()
    def UpdateWaveformShift(self):
        global wave_shift
        wave_shift = self.waveform_shift_textline.text()
    def UpdateWaveformAmplitude(self):
        global wave_amplitude
        wave_amplitude = self.waveform_amplitude_textline.text()
        if self.multiple_waves.isChecked():
            global wave_amplitude2
            wave_amplitude2 = self.waveform_amplitude_textline2.text()
    def UpdateCustomFile(self):
        global custom_file
        custom_file = self.custom_file_textline.text()
    def UpdateCustomFile2(self):
        global custom_file2
        custom_file2 = self.custom_file_textline2.text()
    def UpdateOffset(self):
        global wave_offset
        global wave_amplitude
        temp = float(self.waveform_y_textline.text())
        if temp + wave_amplitude > 10 or temp - wave_amplitude < -10:
            self.waveform_y_textline.setText("OUT OF BOUNDS OFFSET")
        else:
            wave_offset = temp
        if self.multiple_waves.isChecked():
            global wave_offset2
            global wave_amplitude2
            temp = float(self.waveform_y_textline2.text())
            if temp + wave_amplitude2 > 10 or temp - wave_amplitude2 < -10:
                self.waveform_y_textline2.setText("OUT OF BOUNDS OFFSET")
            else:
                wave_offset2 = temp
    def UpdateChannels(self):
        global analogOut_channels
        analogOut_channels = []
        if (self.channel_1_box.isChecked()):
            analogOut_channels.append(1)
        if (self.channel_0_box.isChecked()):
            analogOut_channels.append(0)
    def UpdateOutputType(self):
        global wave_io_type
        wave_io_type =  self.type_output_box.currentText()
    def on_generate_button_clicked(self):
        global waveform
        global wave_frequency
        global wave_shift
        global wave_amplitude
        global wave_offset
        global wave_io_type
        global multiple_wave_types
        global analogOut_channels
        sample_rate_edit = 1000
        high_chan = -100
        low_chan = 100
        for i in analogOut_channels:
            if high_chan < i:
                high_chan = i
            if low_chan > i:
                low_chan = i
        if high_chan == -100:
            low_chan = 0
            high_chan = 0
        if multiple_wave_types:
            global waveform2
            global wave_frequency2
            global wave_shift2
            global wave_amplitude2
            global wave_offset2
            if waveform == "Custom" :
                if waveform2 == "Custom" :
                    talk_to_server([True,waveform,custom_file,wave_frequency,waveform2,custom_file2,wave_frequency2,int(sample_rate_edit),high_chan,low_chan,wave_io_type])
                else:
                    talk_to_server([True,waveform,custom_file,wave_frequency,waveform2,wave_frequency2,wave_shift2,
                                    wave_amplitude2,wave_offset2,int(sample_rate_edit),high_chan,low_chan,wave_io_type])
            else:
                if waveform2 == "Custom" :
                    talk_to_server([True,waveform,wave_frequency,wave_shift,wave_amplitude,
                                    wave_offset,waveform2,custom_file2,wave_frequency2,int(sample_rate_edit),
                                    high_chan,low_chan,wave_io_type])
                else:    
                    talk_to_server([True,waveform,wave_frequency,wave_shift,wave_amplitude,
                                    wave_offset,waveform2,wave_frequency2,wave_shift2,
                                    wave_amplitude2,wave_offset2,int(sample_rate_edit),high_chan,low_chan,wave_io_type])
        else:
            if waveform == "Custom" :
                talk_to_server([False,waveform,custom_file,wave_frequency,int(sample_rate_edit),high_chan,low_chan,wave_io_type])
            else:
                talk_to_server([False,waveform,wave_frequency,wave_shift,wave_amplitude,
                                wave_offset,int(sample_rate_edit),high_chan,low_chan,wave_io_type])
    def on_wave_stop_clicked(self):
        talk_to_server('Stop Wave')

class AnalogInTab (QWidget):
    channel_label = QLabel('Available Channels:')
    channel_0_label = QLabel('Channel 0:')
    channel_0_on = QCheckBox('On?')
    channel_0_visiual = QCheckBox('Plot?')
    channel_range_label = QLabel('Voltage Range:')
    channel_0_range = QComboBox()
    channel_1_label = QLabel('Channel 1:')
    channel_1_on = QCheckBox('On?')
    channel_1_range = QComboBox()
    channel_1_visiual = QCheckBox('Plot?')
    channel_2_label = QLabel('Channel 2:')
    channel_2_on = QCheckBox('On?')
    channel_2_range = QComboBox()
    channel_2_visiual = QCheckBox('Plot?')
    channel_3_label = QLabel('Channel 3:')
    channel_3_on = QCheckBox('On?')
    channel_3_range = QComboBox()
    channel_3_visiual = QCheckBox('Plot?')
    channel_4_label = QLabel('Channel 4:')
    channel_4_on = QCheckBox('On?')
    channel_4_range = QComboBox()
    channel_4_visiual = QCheckBox('Plot?')
    channel_5_label = QLabel('Channel 5:')
    channel_5_on = QCheckBox('On?')
    channel_5_range = QComboBox()
    channel_5_visiual = QCheckBox('Plot?')
    channel_6_label = QLabel('Channel 6:')
    channel_6_on = QCheckBox('On?')
    channel_6_range = QComboBox()
    channel_6_visiual = QCheckBox('Plot?')
    channel_7_label = QLabel('Channel 7:')
    channel_7_on = QCheckBox('On?')
    channel_7_range = QComboBox()
    channel_7_visiual = QCheckBox('Plot?')

    channel_0_range.addItem('BIP10')
    channel_0_range.addItem('BIP5')
    channel_0_range.addItem('UNI10')
    channel_0_range.addItem('UNI5')
    channel_1_range.addItem('BIP10')
    channel_1_range.addItem('BIP5')
    channel_1_range.addItem('UNI10')
    channel_1_range.addItem('UNI5')
    channel_2_range.addItem('BIP10')
    channel_2_range.addItem('BIP5')
    channel_2_range.addItem('UNI10')
    channel_2_range.addItem('UNI5')
    channel_3_range.addItem('BIP10')
    channel_3_range.addItem('BIP5')
    channel_3_range.addItem('UNI10')
    channel_3_range.addItem('UNI5')
    channel_4_range.addItem('BIP10')
    channel_4_range.addItem('BIP5')
    channel_4_range.addItem('UNI10')
    channel_4_range.addItem('UNI5')
    channel_5_range.addItem('BIP10')
    channel_5_range.addItem('BIP5')
    channel_5_range.addItem('UNI10')
    channel_5_range.addItem('UNI5')
    channel_6_range.addItem('BIP10')
    channel_6_range.addItem('BIP5')
    channel_6_range.addItem('UNI10')
    channel_6_range.addItem('UNI5')
    channel_7_range.addItem('BIP10')
    channel_7_range.addItem('BIP5')
    channel_7_range.addItem('UNI10')
    channel_7_range.addItem('UNI5')

    channel_submit_button = QPushButton("Submit Options")

    layout = None

    def __init__(self):
        super().__init__()
        self.layout = QGridLayout()
        layout = self.layout
        self.setLayout(layout)

        layout.addWidget(self.channel_label,0,0)
        layout.addWidget(self.channel_0_label,1,0)
        layout.addWidget(self.channel_0_on,1,1)
        layout.addWidget(self.channel_0_range,1,3)
        layout.addWidget(self.channel_0_visiual,1,4)
        layout.addWidget(self.channel_1_label,2,0)
        layout.addWidget(self.channel_1_on,2,1)
        layout.addWidget(self.channel_1_range,2,3)
        layout.addWidget(self.channel_1_visiual,2,4)
        layout.addWidget(self.channel_2_label,3,0)
        layout.addWidget(self.channel_2_on,3,1)
        layout.addWidget(self.channel_2_range,3,3)
        layout.addWidget(self.channel_2_visiual,3,4)
        layout.addWidget(self.channel_3_label,4,0)
        layout.addWidget(self.channel_3_on,4,1)
        layout.addWidget(self.channel_3_range,4,3)
        layout.addWidget(self.channel_3_visiual,4,4)
        layout.addWidget(self.channel_4_label,5,0)
        layout.addWidget(self.channel_4_on,5,1)
        layout.addWidget(self.channel_4_range,5,3)
        layout.addWidget(self.channel_4_visiual,5,4)
        layout.addWidget(self.channel_5_label,6,0)
        layout.addWidget(self.channel_5_on,6,1)
        layout.addWidget(self.channel_5_range,6,3)
        layout.addWidget(self.channel_5_visiual,6,4)
        layout.addWidget(self.channel_6_label,7,0)
        layout.addWidget(self.channel_6_on,7,1)
        layout.addWidget(self.channel_6_range,7,3)
        layout.addWidget(self.channel_6_visiual,7,4)
        layout.addWidget(self.channel_7_label,8,0)
        layout.addWidget(self.channel_7_on,8,1)
        layout.addWidget(self.channel_7_range,8,3)
        layout.addWidget(self.channel_7_visiual,8,4)
        layout.addWidget(self.channel_range_label,1,2)
        layout.addWidget(self.channel_submit_button,9,0)

        self.channel_submit_button.clicked.connect(self.SubmitChannels)

    def SubmitChannels(self):
        global analogIn_channels
        global analog_chans_plot
        analogIn_channels = []
        analog_chans_plot = []
        if self.channel_0_on.checkState() == QtCore.Qt.Checked:
            analogIn_channels.append(0)
            if self.channel_0_visiual.checkState() == QtCore.Qt.Checked:
                analog_chans_plot.append(0)
        if self.channel_1_on.checkState() == QtCore.Qt.Checked:
            analogIn_channels.append(1)
            if self.channel_1_visiual.checkState() == QtCore.Qt.Checked:
                analog_chans_plot.append(1)
        if self.channel_2_on.checkState() == QtCore.Qt.Checked:
            analogIn_channels.append(2)
            if self.channel_2_visiual.checkState() == QtCore.Qt.Checked:
                analog_chans_plot.append(2)
        if self.channel_3_on.checkState() == QtCore.Qt.Checked:
            analogIn_channels.append(3)
            if self.channel_3_visiual.checkState() == QtCore.Qt.Checked:
                analog_chans_plot.append(3)
        if self.channel_4_on.checkState() == QtCore.Qt.Checked:
            analogIn_channels.append(4)
            if self.channel_4_visiual.checkState() == QtCore.Qt.Checked:
                analog_chans_plot.append(4)
        if self.channel_5_on.checkState() == QtCore.Qt.Checked:
            analogIn_channels.append(5)
            if self.channel_5_visiual.checkState() == QtCore.Qt.Checked:
                analog_chans_plot.append(5)
        if self.channel_6_on.checkState() == QtCore.Qt.Checked:
            analogIn_channels.append(6)
            if self.channel_6_visiual.checkState() == QtCore.Qt.Checked:
                analog_chans_plot.append(6)
        if self.channel_7_on.checkState() == QtCore.Qt.Checked:
            analogIn_channels.append(7)
            if self.channel_7_visiual.checkState() == QtCore.Qt.Checked:
                analog_chans_plot.append(7)
    
class DigitalConfigTab (QWidget):
    # Initialize Widgets
    channel_label = QLabel('Available Channels:')
    channel_0_label = QLabel('Channel 0:')
    channel_0_on = QCheckBox('On?')
    channel_0_input = QCheckBox('Input?')
    channel_0_output = QCheckBox('Output?')
    channel_1_label = QLabel('Channel 1:')
    channel_1_on = QCheckBox('On?')
    channel_1_input = QCheckBox('Input?')
    channel_1_output = QCheckBox('Output?')
    channel_2_label = QLabel('Channel 2:')
    channel_2_on = QCheckBox('On?')
    channel_2_input = QCheckBox('Input?')
    channel_2_output = QCheckBox('Output?')
    channel_3_label = QLabel('Channel 3:')
    channel_3_on = QCheckBox('On?')
    channel_3_input = QCheckBox('Input?')
    channel_3_output = QCheckBox('Output?')
    channel_submit = QPushButton('Submit Channel Options')
    
    layout = None
    
    def __init__(self):
        super().__init__()
        self.layout = QGridLayout()
        layout = self.layout
        self.setLayout(layout)
        # Add Widgets
        layout.addWidget(self.channel_label,1,0)
        layout.addWidget(self.channel_0_label,2,0)
        layout.addWidget(self.channel_0_on,2,1)
        layout.addWidget(self.channel_0_input,2,2)
        layout.addWidget(self.channel_0_output,2,3)
        layout.addWidget(self.channel_1_label,3,0)
        layout.addWidget(self.channel_1_on,3,1)
        layout.addWidget(self.channel_1_input,3,2)
        layout.addWidget(self.channel_1_output,3,3)
        layout.addWidget(self.channel_2_label,4,0)
        layout.addWidget(self.channel_2_on,4,1)
        layout.addWidget(self.channel_2_input,4,2)
        layout.addWidget(self.channel_2_output,4,3)
        layout.addWidget(self.channel_3_label,5,0)
        layout.addWidget(self.channel_3_on,5,1)
        layout.addWidget(self.channel_3_input,5,2)
        layout.addWidget(self.channel_3_output,5,3)
        layout.addWidget(self.channel_submit,6,0)
        
        #Add Listeners
        
        self.channel_submit.clicked.connect(self.SubmitChannels)
        
    def SubmitChannels(self):
        global active_digital_channels
        global active_digitalIn_channels
        active_digital_channels = []
        if self.channel_0_on.checkState() == QtCore.Qt.Checked:
            if self.channel_0_input.checkState() == QtCore.Qt.Checked:
                active_digitalIn_channels.append('0')
            elif self.channel_0_output.checkState() == QtCore.Qt.Checked:
                active_digital_channels.append('0')
        if self.channel_1_on.checkState() == QtCore.Qt.Checked:
            if self.channel_1_input.checkState() == QtCore.Qt.Checked:
                active_digitalIn_channels.append('1')
            elif self.channel_1_output.checkState() == QtCore.Qt.Checked:
                active_digital_channels.append('1')
        if self.channel_2_on.checkState() == QtCore.Qt.Checked:
            if self.channel_2_input.checkState() == QtCore.Qt.Checked:
                active_digitalIn_channels.append('2')
            elif self.channel_2_output.checkState() == QtCore.Qt.Checked:
                active_digital_channels.append('2')
        if self.channel_3_on.checkState() == QtCore.Qt.Checked:
            if self.channel_3_input.checkState() == QtCore.Qt.Checked:
                active_digitalIn_channels.append('3')
            elif self.channel_3_output.checkState() == QtCore.Qt.Checked:
                active_digital_channels.append('3')
        print('Successfully reattributed channels with the listing: ',active_digital_channels)
class DigitalControlTab (QWidget) :
    layout = None
    # This tab will be used to switch between High and Low Input vs Output
    # To do so I think we'll have to briefly stop output and restart, unsure what to do for input

    def __init__(self):
        super().__init__()
        self.layout = QGridLayout()
        layout = self.layout
        self.setLayout(layout)

class MCCUSBControlTab (QWidget) :
    initiate_button = QPushButton("Confirm Device Settings")
    input_mode_label = QLabel("Input Type:")
    input_mode = QComboBox()
    sample_rate_label = QLabel("Sample Rate (Hz):")
    sample_rate_edit = QLineEdit('1000')

    input_mode.addItem("Single-Ended")
    input_mode.addItem("Differential")

    def __init__(self):
        super().__init__()
        
        layout = QGridLayout()
        self.setLayout(layout)

        layout.addWidget(self.input_mode_label,0,0)
        layout.addWidget(self.input_mode,0,1)
        layout.addWidget(self.sample_rate_label, 1, 0)
        layout.addWidget(self.sample_rate_edit, 1, 1)
        layout.addWidget(self.initiate_button,2,0,2,1)

        self.initiate_button.clicked.connect(self.reinitiateMCCUSB)

    def reinitiateMCCUSB(self):
        global analogIn_channels
        global active_digitalIn_channels
        global sample_rate
        sample_rate = int(self.sample_rate_edit.text())
        ahigh_chan = -100
        alow_chan = 100
        for i in analogIn_channels:
            if ahigh_chan < i:
                ahigh_chan = i
            if alow_chan > i:
                alow_chan = i
        if ahigh_chan == -100:
            alow_chan = 0
            ahigh_chan = 0
        dhigh_chan = -100
        dlow_chan = 100
        for i in active_digitalIn_channels:
            if dhigh_chan < i:
                dhigh_chan = i
            if dlow_chan > i:
                dlow_chan = i
        if dhigh_chan == -100:
            dlow_chan = 0
            dhigh_chan = 0
        arange = ahigh_chan - alow_chan
        drange = dhigh_chan - dlow_chan
        request = ["Reinit",ahigh_chan,alow_chan,sample_rate,self.input_mode.currentText()]
        talk_to_server(request)
    # Function to connect to a specific device/Device Select
    # Initiation of Device?
    # Function to use external/internal clock
    # Triggers? I.e. Red Pitaya?
class AcquisitionTab (QWidget) :
    graph = pg.PlotWidget(name='Plot1')
    p1 = graph.plot()
    graph_filename_label = QLabel('Plot Data filename: ')
    graph_filename_textline = QLineEdit("test.hdf")
    graph_CheckBox1 = QCheckBox("Plot all data points")
    graph_update_button = QPushButton("Update plot every 0.5 s")
    graph_stopupdate_button = QPushButton("Stop plot update")
    graph_CheckBox1.setCheckState(0)
    button_MCUSB_start = QPushButton('Start')
    button_MCUSB_stop = QPushButton('Stop')
    message2 = QLabel('Run number:')
    MCUSB_run_no_textline = QLineEdit("1")
    t = QtCore.QTimer()
    textbox = QLineEdit()
    
    def __init__(self):
        super().__init__()
        
        layout = QGridLayout()
        self.setLayout(layout)
        #Add widgets to the tab
        layout.addWidget(self.button_MCUSB_start,1,3) # button goes in upper-middle
        layout.addWidget(self.button_MCUSB_stop,1,4) # button goes in upper-middle
        layout.addWidget(self.graph_filename_label, 0,1)
        layout.addWidget(self.graph_filename_textline, 0,2)
        layout.addWidget(self.graph_CheckBox1, 2,0)
        layout.addWidget(self.graph_update_button, 1,5)
        layout.addWidget(self.graph_stopupdate_button, 1,6)
        layout.addWidget(self.graph,2,1,6,6)
        layout.addWidget(self.message2,5,0)
        layout.addWidget(self.MCUSB_run_no_textline,6,0)
        
        #Add function connections
        self.graph_update_button.clicked.connect(self.updatePlot)
        self.graph_stopupdate_button.clicked.connect(self.stopUpdatePlot)
        self.button_MCUSB_start.clicked.connect(self.on_start_button_clicked)
        self.button_MCUSB_stop.clicked.connect(self.on_stop_button_clicked)
        self.t.timeout.connect(self.updateData)

        global t_buffer
        t_buffer = self.t
   
    def updateData(self):
        global analog_chans_plot
        filename = str(self.graph_filename_textline.text())
        f = h5py.File(filename, 'r', libver='latest', swmr=True)
        dset = f["events"]
        ss = len(dset)
        yd = np.zeros((dset.shape[0],len(analog_chans_plot)))
        chan = 0
        colors = ["red","orange","yellow","green","blue","purple","white"]
        for i in analog_chans_plot:
            if self.graph_CheckBox1.isChecked():
                yd = dset[:,i]
                xd = np.linspace(0,ss,ss)
            else:
                n_points = 2000
                if ss<n_points:
                #if ss<ss+1:
                    yd = dset[:,i]
                    xd = np.linspace(0,ss,ss)
                else:
                    yd = dset[ss-n_points:ss,i]
                    xd = np.linspace(ss-n_points,ss-1,n_points)
            self.graph.plot(x=xd, y=yd, pen=None, symbol='o', symbolPen=colors[chan], symbolSize=10)
            chan = chan + 1
        
    def updatePlot(self):
        self.t.start(500) #500 ms?
        
    def stopUpdatePlot(self):
        self.t.stop()
    
    def on_start_button_clicked(self):
        global sample_rate
        global analogIn_channels
        high_chan = -100
        low_chan = 100
        for chan in analogIn_channels:
            if high_chan < chan:
                high_chan = chan
            if low_chan > chan:
                low_chan = chan
        if high_chan == -100:
            low_chan = 0
            high_chan = 0
        run_no = self.MCUSB_run_no_textline.text()
        service_request = ['Acquire '+ str(run_no),high_chan,low_chan]
        if self.textbox.text() == 'Server Not Alive.':
            print('Server is not alive')
        talk_to_server(service_request)
        graph_filename='test'+str(run_no)+'.hdf'
        self.graph_filename_textline.setText(graph_filename)

    def on_stop_button_clicked(self):
        run_no = self.MCUSB_run_no_textline.text()
        self.MCUSB_run_no_textline.setText(str(int(run_no) + 1))
        talk_to_server('Stop')

panels.addTab(AnalogConfigTab(), 'Analog Output')
panels.addTab(AnalogInTab(), 'Analog Input')
panels.addTab(DigitalConfigTab(), 'Digital Config')
panels.addTab(DigitalControlTab(), 'Digital Control')
panels.addTab(MCCUSBControlTab(), 'MCCUSB Control')
panels.addTab(AcquisitionTab(), 'Acquisition')
textbox = QLabel()


## Create a grid layout to manage the widgets size and position
layout = QGridLayout()
window.setLayout(layout)

## Add widgets to the layout in their proper positions
layout.addWidget(panels, 1, 2)
layout.addWidget(textbox,7,0)

## Display the widget as a new window
window.show()
    
## read the hdf5 file here

class HDF5Plot(pg.PlotCurveItem):
    def __init__(self, *args, **kwds):
        self.hdf5 = None
        global sample_rate
        self.rate = sample_rate
        global t_buffer
        self.limit = self.rate * t_buffer # maximum number of samples to be plotted
        pg.PlotCurveItem.__init__(self, *args, **kwds)
        
    def setHDF5(self, data):
        self.hdf5 = data
        self.updateHDF5Plot()
        
    def viewRangeChanged(self):
        self.updateHDF5Plot()
        
    def updateHDF5Plot(self):
        if self.hdf5 is None:
            self.setData([])
            return
        
        vb = self.getViewBox()
        if vb is None:
            return  # no ViewBox yet
        
        # Determine what data range must be read from HDF5
        xrange = vb.viewRange()[0]
        start = max(0,int(xrange[0])-1)
        stop = min(len(self.hdf5), int(xrange[1]+2))
        
        # Decide by how much we should downsample 
        ds = int((stop-start) / self.limit) + 1
        
        if ds == 1:
            # Small enough to display with no intervention.
            visible = self.hdf5[start:stop]
            scale = 1
        else:
            # Here convert data into a down-sampled array suitable for visualizing.
            # Must do this piecewise to limit memory usage.        
            samples = 1 + ((stop-start) // ds)
            visible = np.zeros(samples*2, dtype=self.hdf5.dtype)
            sourcePtr = start
            targetPtr = 0
            
            # read data in chunks of ~1M samples
            chunkSize = (1000000//ds) * ds
            while sourcePtr < stop-1: 
                chunk = self.hdf5[sourcePtr:min(stop,sourcePtr+chunkSize)]
                sourcePtr += len(chunk)
                
                # reshape chunk to be integral multiple of ds
                chunk = chunk[:(len(chunk)//ds) * ds].reshape(len(chunk)//ds, ds)
                
                # compute max and min
                chunkMax = chunk.max(axis=1)
                chunkMin = chunk.min(axis=1)
                
                # interleave min and max into plot data to preserve envelope shape
                visible[targetPtr:targetPtr+chunk.shape[0]*2:2] = chunkMin
                visible[1+targetPtr:1+targetPtr+chunk.shape[0]*2:2] = chunkMax
                targetPtr += chunk.shape[0]*2
            
            visible = visible[:targetPtr]
            scale = ds * 0.5
            
        self.setData(visible) # update the plot
        self.setPos(start, 0) # shift to match starting index
        self.resetTransform()
        self.scale(scale, 1)  # scale to match downsampling
###---------------------------------------------

def CheckStatus_MCUSB(): 
    print("Check status …")
    socket.send(b"Status")
    # #  Get the reply.
    message = socket.recv()
    print("Received reply [ %s ]" % (message))
    textbox.setText("Received reply %s [ %s ]" % (request, message))
    
#------------------------------------------------------------------
#   ZMQ REQ client in Python
#   Connects REQ socket to tcp://localhost:5555
import zmq

context = zmq.Context()

ms = 200 # In milliseconds.

#  Socket to talk to server
def socket_open():
    global socket
    #print("Connecting to the MCUSB server…")
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")
    socket.setsockopt(zmq.SNDTIMEO, ms)
    socket.setsockopt(zmq.RCVTIMEO, ms)
    socket.setsockopt(zmq.LINGER, ms) # Discard pending buffered socket messages on close().
    socket.setsockopt(zmq.CONNECT_TIMEOUT, ms)

request = 0
def talk_to_server(service_request):
    global socket
    global request
    request = request + 1
    if type(service_request) != str:
        service_request = str(service_request)
    print("Sending request ... %s" % service_request)
    #This service_request will need more information. What channels are on? What's the sample rate? What's the waveform frequency?
    #Currently this request only handles basic one-word requests. This is problematic for a generalized DAQ software
    #Log 1: Attempting to rectify this loss of information. Currently raising error when request is a list, despite a cast to string
    #Log 2: This seems to not throw the error as long as I only send a one-word string
    socket.send(service_request.encode(),flags=zmq.NOBLOCK)
    #socket.send_string(service_request)
    #  Get the reply.
    try:
        message = socket.recv()
    except:
        message = 'Server Not Alive.'
        socket.setsockopt(zmq.LINGER, 0)
        socket.close()  # this is the only way to flush/drop the request
        socket_open() # immediately open the socket again for future communications
        pass
    print("--> %s Received reply [ %s ]" % (request, message))
    if service_request == 'Acquire Channels':
        return message
        

def ping_server():
    global socket
    service_request='Alive?'
    socket.send(service_request.encode(),flags=zmq.NOBLOCK)
    #  Get the reply.
    pixmap = QPixmap('smiley-mr-green.png')
    try:
        message = socket.recv()
    except:
        pixmap = QPixmap('heart-break.png')
        socket.setsockopt(zmq.LINGER, 0)
        socket.close()  # this is the only way to flush/drop the request
        socket_open() # immediately open the socket again for future communications
        pass

# Check server connection
socket_open()
print('server connected? ')
ping_server()

t2 = QtCore.QTimer()
t2.timeout.connect(ping_server)
t2.start(1000) #50 ms?

## Start the Qt event loop
app.exec_()
