'''
A sample client that uses the BluetoothClient library
'''

from BluetoothClient import *
from threading import Thread
import time

#define callback to be used for incoming reads
def on_read(data):
    print "The server said: " + str(data)
    return None

#create config and state objects
uuid = "17397638-30e6-4a5b-ac36-fbfda4b34d38"
bt_config = BluetoothClientConfig(uuid)
bt_state = BluetoothClientState()

#get and print all server candidates
GetConnectionCandidates(bt_state, bt_config)
for x in bt_state._connection_candidates:
    print x

#connect to the first candidate
if len(bt_state._connection_candidates) > 0:
    ConnectToBluetoothServer(bt_state, bt_state._connection_candidates[0])

    #start listening for data from the server on a seperate thread
    t_listener = Thread(target=ReadFromServer, args=[bt_state, on_read])
    t_listener.start()

    #every 5 seconds write a message to the server
    #do this exactly 3 times
    for x in xrange(3):
        time.sleep(5)
        WriteToServer(bt_state, "Hello I'm a client!")

    #wait another minute, then close everything up
    time.sleep(60)
    FlagConnectionTermination(bt_state)
    DisconnectFromBluetoothServer(bt_state)
else:
    raise "Could not find a server to connect to!"