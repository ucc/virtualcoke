virtualcoke
===========

Curses based emulator of the UCC Coke Machine PLC

Usage
-----

virtualcoke.py

Via the network:
	When run, virtualcoke attempt to bind to port 502 (Modbus standard port)
	If this fails, it will bind to port 1502
	To bind to the lower port, you may need to be a privileged user

Via the console:
	Keypad numbers (0-6) mimic front buttons of the coke machine
	Keypad numbers (7-9, M) mimic the interior buttons of the coke machine
	^Q exits the simulator cleanly

Requirements
-------------

* npyscreen 4.8.5 or later
* Twisted

Known Issues
-------------

None
