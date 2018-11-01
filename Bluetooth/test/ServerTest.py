'''
A sample server that uses the BluetoothServer library
'''

from BluetoothServer import *
from threading import Thread
import time

#define callbacks to be used for incoming connections and client data
clients = {}
def on_connection(new_client):
    clients[new_client._uuid] = new_client
    t_reader = Thread(target=ListenForIncomingData, args=[new_client, on_read])
    t_reader.start()
    return None
def on_read(client_uuid, data):
    print "Client " + client_uuid + " said: " + str(data)
    return None

#create config and state objects
uuid = "17397638-30e6-4a5b-ac36-fbfda4b34d38"
service_name = "Quizzly Server"
bt_config = BluetoothServerConfig(uuid, service_name)
bt_state = BluetoothServerState()

#start by initializing the server socket
InitializeServerSocket(bt_state)

#start listening for incoming connections in a separate thread
t_listener = Thread(target=AdvertiseAndListen, args=[bt_config, bt_state, on_connection])
t_listener.start()

#every 10 seconds write a message to all active clients
#do this exactly 6 times
for x in xrange(6):
    time.sleep(10)
    for y in clients:
        WriteToClient(clients[y], "Hello this is your server speaking.")
        
#wait another minute, then close everything up
time.sleep(60)
FlagConnectionTermination(bt_state)
for z in clients:
    CloseClientSocket(clients[z], bt_state)
CloseServerSocket(bt_state)