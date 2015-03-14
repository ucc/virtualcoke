#!/usr/bin/env python

# vim: set tabstop=4 shiftwidth=4 expandtab ai

import npyscreen
from datetime import datetime

# npyscreen twisted reactor
import npyscreenreactor
reactor = npyscreenreactor.install()

# Incorporates code from
#Pymodbus Asynchronous Server Example

#---------------------------------------------------------------------------# 
# import the various server implementations
#---------------------------------------------------------------------------# 
from pymodbus.constants import Defaults
from pymodbus.transaction import ModbusSocketFramer, ModbusAsciiFramer
from pymodbus.server.async import ModbusServerFactory


from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSparseDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext


# for emulator code
import os
import sys
import string

# Ascii Coke Logo
# by Normand Veilleux
# in cokelogo.txt

##---------------------------------------------------------------------------# 
## configure the service logging
##---------------------------------------------------------------------------# 
import logging
logging.basicConfig(filename="virtualcoke.log", filemode="a+")
log = logging.getLogger()
log.setLevel(logging.DEBUG)

# Factory for modbus

def StartModbusAsyncServer(context, identity=None, address=None, console=False):
    ''' Helper method to start the Modbus Async TCP server

    :param context: The server data context
    :param identify: The server identity to use (default empty)
    :param address: An optional (interface, port) to bind to.
    :param console: A flag indicating if you want the debug console
    '''
    from twisted.internet import reactor

    address = address or ("", Defaults.Port)
    framer  = ModbusSocketFramer
    factory = ModbusServerFactory(context, framer, identity)
    if console: InstallManagementConsole({'factory': factory})

    log.info("Starting Modbus TCP Server on %s:%s" % address)
    reactor.listenTCP(address[1], factory, interface=address[0])


#

class ContainedMultiSelect(npyscreen.BoxTitle):
    _contained_widget = npyscreen.TitleMultiSelect

class CokeButtonPress(npyscreen.MiniButtonPress):
    def __init__(self, screen, when_pressed_function=None, when_pressed_callback=None, *args, **keywords):
	super(CokeButtonPress, self).__init__(screen, *args, **keywords)
	self.when_pressed_callback = when_pressed_callback

    def whenPressed(self,key=None):
	if self.when_pressed_callback:
		self.when_pressed_callback(widget=self)

class VirtualCoke(npyscreen.Form):

    def while_waiting(self):
        self.date_widget.value = datetime.now().ctime()
	self.statusfield.value = self.parentApp.status
	self.infofield.value = self.parentApp.info
        self.display()

    def create(self, *args, **keywords):
        super(VirtualCoke, self).create(*args, **keywords)

	logofile = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "cokelogo.txt")
	logotext = open(logofile).read()
	self.cokelogo = []

	cly = 1
	for line in logotext.splitlines():
		widget = self.add(npyscreen.FixedText, value=line, editable = False, rely = cly)
		cly = cly + 1
		self.cokelogo.append(widget)

	# LEDS
	self.leds = []
	lx = 1
	ly = cly 
	for led in range(0,7):
		lx = ((7 * 7) + 3) - ( led * 7 )
		widget = self.add(npyscreen.FixedText, value="[SOLD]", editable = False, relx = lx, rely = ly)
		self.leds.append(widget)
		#
		# FIXME Hook up widgets and callbacks
		#
#		widget = self.add(CokeButtonPress,name="%d"%keypad, relx = kpx, rely = kpy, when_pressed_callback=self.parentApp.when_keypad_pressed)
#		self.add_handlers({"%d"%keypad: widget.whenPressed})
		
	# Buttons
	self.buttons = []
	bx = 1
	by = ly + 1
	for button in range(0,7):
		bx = ((7 * 7) + 3) - ( button * 7 )
		widget = self.add(npyscreen.FixedText, value=str(button), editable = False, relx = bx, rely = by)
		self.add_handlers({"%d" % button: self.parentApp.when_keypad_pressed})
		self.buttons.append(widget)
	for button in range(7,10):
		bx = (8 * 7) + ((button - 6) * 4 ) + 3
		widget = self.add(npyscreen.FixedText, value=str(button), editable = False, relx = bx, rely = by)
		self.add_handlers({"%d" % button: self.parentApp.when_keypad_pressed})
		self.buttons.append(widget)
	
        # Manual
	bx = bx + 3
	widget = self.add(npyscreen.FixedText, value="M", editable = False, relx = bx, rely = by)
	self.add_handlers({"M": self.parentApp.when_keypad_pressed})
	self.add_handlers({"m": self.parentApp.when_keypad_pressed})
	self.buttons.append(widget)
	#



	# Slots

	self.slots = []
	sx = 1
	sy = by + 1
	widget = self.add(npyscreen.FixedText, value="Empty?", editable = False, relx = sx, rely = sy)
	for slot in range(0,7):
		sx = ((7 * 7) + 3) - ( slot * 7 )
		widget = self.add(npyscreen.CheckboxBare, name=str(slot), relx = sx, rely = sy, value_changed_callback=self.parentApp.when_empty_toggled)
		self.slots.append(widget)
		self.update_sold(slot, widget.value)
	for slot in range(7,10):
		sx = (8 * 7) + ((slot - 6) * 4 ) + 3
		widget = self.add(npyscreen.CheckboxBare, name=str(slot), relx = sx, rely = sy, value_changed_callback=self.parentApp.when_empty_toggled)
		self.slots.append(widget)
		self.update_sold(slot, widget.value)


	self.date_widget = self.add(npyscreen.FixedText, value=datetime.now().ctime(), editable=False, rely=19)
        self.date_widget.value = "Hello"
	self.add_handlers({"^Q": self.exit_application})
        
	self.statusfield = self.add(npyscreen.TitleText, name = "Status:", value="", editable=False, rely=20 )
        self.infofield = self.add(npyscreen.TitleText, name = "Info:", value="", editable=False )

    def exit_application(self,name):
        self.parentApp.setNextForm(None)
        self.editing = False

    def get_slot_status(self):
    	status = []
    	for slot in self.slots:
    	    status.append(slot.value)
        return status

    def update_sold(self, slot, value):
	self.parentApp.do_info("Slot %d toggled" % slot)
	if value:
		if slot < 6:
			self.leds[slot].value = "[SOLD]"
		# coke slot magic
		elif self.slots[6].value and \
			self.slots[7].value and \
			self.slots[8].value and \
			self.slots[9].value:
			self.leds[6].value = "[SOLD]"
	else:
		if slot < 6:
			self.leds[slot].value = "[    ]"
		else:
			self.leds[6].value = "[    ]"


    

class VirtualCokeApp(npyscreen.StandardApp):
    keypress_timeout_default = 1

    def onStart(self):
	# initialise virtual coke machine

	self.F = self.addForm("MAIN", VirtualCoke, name="Virtual Coke")

	self.status=""
	self.info="in onStart"

    def while_waiting(self):
	pass
	# socket code was here

    def onCleanExit(self):
	pass
	# socket code was here
    
    # Coke Emulator comms below
    
    def do_status(self, data):
	# socket code was here
	self.status = data

    def do_info(self, data):
	# socket code was here
	self.info = data


    # Callbacks
    def get_slot_status(self):
	return self.F.get_slot_status()

    def when_empty_toggled(self, *args, **keywords):
# See 
#  https://code.google.com/p/npyscreen/source/detail?r=9768a97fd80ed1e7b3e670f312564c19b1adfef8#
# for callback info
        self.do_status(keywords['widget'].name + " " + str(self.F.get_slot_status()))
	self.F.update_sold(int(keywords['widget'].name), keywords['widget'].value)
	self.F.display()

    def when_reset_pressed(self, *args, **keywords):
        self.do_status('211 keypress\n')
        keywords['widget'].value = False
	self.F.display()

    def when_keypad_pressed(self, *args, **keywords):
	#key = '0'+ keywords['widget'].name
        #self.do_status('2'+key+' keypress\n')
        #keywords['widget'].value = False
        self.do_status(("%c" % args[0]))
	self.F.display()

    # Coke Emulator code below


#---------------------------------------------------------------------------# 
# initialize your data store
#---------------------------------------------------------------------------# 
# The datastores only respond to the addresses that they are initialized to.
# Therefore, if you initialize a DataBlock to addresses of 0x00 to 0xFF, a
# request to 0x100 will respond with an invalid address exception. This is
# because many devices exhibit this kind of behavior (but not all)::
#
#     block = ModbusSequentialDataBlock(0x00, [0]*0xff)
#
# Continuting, you can choose to use a sequential or a sparse DataBlock in
# your data context.  The difference is that the sequential has no gaps in
# the data while the sparse can. Once again, there are devices that exhibit
# both forms of behavior::
#
#     block = ModbusSparseDataBlock({0x00: 0, 0x05: 1})
#     block = ModbusSequentialDataBlock(0x00, [0]*5)
#
# Alternately, you can use the factory methods to initialize the DataBlocks
# or simply do not pass them to have them initialized to 0x00 on the full
# address range::
#
#     store = ModbusSlaveContext(di = ModbusSequentialDataBlock.create())
#     store = ModbusSlaveContext()
#
# Finally, you are allowed to use the same DataBlock reference for every
# table or you you may use a seperate DataBlock for each table. This depends
# if you would like functions to be able to access and modify the same data
# or not::
#
#     block = ModbusSequentialDataBlock(0x00, [0]*0xff)
#     store = ModbusSlaveContext(di=block, co=block, hr=block, ir=block)
#---------------------------------------------------------------------------# 

#---------------------------------------------------------------------------# 
# create your custom data block with callbacks
#---------------------------------------------------------------------------# 
class CallbackDataBlock(ModbusSparseDataBlock):
    ''' A datablock that stores the new value in memory
    and passes the operation to a message queue for further
    processing.
    '''

    def __init__(self, values, app=None):
	self.toggle = 1
	self.app = app
	super(CallbackDataBlock, self).__init__(values)

    def getValues(self, address, count=1):
        ''' Returns the requested values from the datastore

        :param address: The starting address
        :param count: The number of values to retrieve
        :returns: The requested values from a:a+c
        '''	
	ciCoke_DropBitBase = 1024 + 1;
	ciCoke_StatusBitBase = 16 + 1;

        # get status of slots from form
	
        slots = self.app.get_slot_status()

	#log.debug("CBD getValues %d:%d" % (address, count))

        # check if a status read or a drop read
	if address < ciCoke_DropBitBase:
		log.debug("Status Read getValues %d:%d" % (address, count))
                if address < ciCoke_StatusBitBase or \
                        address >= ciCoke_StatusBitBase + len(slots):
		        return [0]
                # calculate slot
                reading = address - ciCoke_StatusBitBase
		# invert 
		status = not slots[reading]

                return [status]

	log.debug("Dispense Read getValues %d:%d" % (address, count))
                
	if address >= ciCoke_DropBitBase + len(slots):
	        return [0]

	dispensing = address - ciCoke_DropBitBase

        now = datetime.now().ctime()
	self.app.do_info("At %s, Dispense slot %d ...... bzzzztclunk ..." % (now, dispensing))

	self.toggle = self.toggle+1

	#log.debug("CBD getValues toggle %d" % (self.toggle))
	if self.toggle % 3 == 0:
		return [1]
	
	if self.toggle % 3 == 1:
		return [1]

	if self.toggle % 3 == 2:
		return [0]

	return [1]
	


def modbus_setup(app):
	store = ModbusSlaveContext(
	    di = CallbackDataBlock([0]*100, app=app),
	    co = CallbackDataBlock([0]*65536, app=app), 
	    hr = CallbackDataBlock([0]*100, app),
	    ir = CallbackDataBlock([0]*100, app))

	context = ModbusServerContext(slaves=store, single=True)

	return context


if __name__ == "__main__":
    App = VirtualCokeApp()
    context = modbus_setup(App)

    reactor.registerNpyscreenApp(App)
    StartModbusAsyncServer(context)
    reactor.run()

