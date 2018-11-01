'''
Provides an interface and implementation for communicating via Bluetooth on the client side
'''

#imports
import bluetooth
from threading import Thread
import select

#object representing the configuration parameters for a Bluetooth client
class BluetoothClientConfig:
    #constructor
    def __init__(self, server_uuid):
        self._server_uuid = server_uuid #UUID for Bluetooth Server
        
#object representing the state of the client at any given time
class BluetoothClientState:
    #constructor
    def __init__(self):
        self._socket = None
        self._connected = False
        self._end_connection = False
        self._connection_candidates = []
        
#method to display possible Bluetooth servers to connect to given a state and config
#takes a client state and client config as inputs and sets the connection candidates in the state
def GetConnectionCandidates(state, config):
    state._connection_candidates = bluetooth.find_service( uuid = config._server_uuid )
    return None

#method to connect to a Bluetooth server
#takes a client state and candidate Bluetooth server as inputs
#candidate should be a member of the output of GetConnectionCandidates
def ConnectToBluetoothServer(state, candidate):
    if state._connected == False:
        state._socket = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
        state._socket.connect((candidate["host"], candidate["port"]))
        state._connected = True
        state._end_connection = False
    return None

#method to indicate that the client is ready to close its connection and thus set the appropriate flag
#flag must be set so that individual threads that are running know to finish up
def FlagConnectionTermination(state):
    if state._connected == True and state._end_connection == False:
        state._end_connection = True
    return None

#method to disconnect from a Bluetooth server
#takes a client state as input
def DisconnectFromBluetoothServer(state):
    if state._connected == True and state._end_connection == True:
        state._socket.close()
        state._socket = None
        state._connected = False
        state._end_connection = False
    return None

#method to listen for incoming data from the server
#this method should be run in a single thread
def ReadFromServer(state, read_callback):
    read_list = [state._socket]
    while (state._connected == True and state._end_connection == False):
        readable, writable, errored = select.select(read_list, [], [])
        for s in readable:
            if s is state._socket:
                data = s.recv()
                process_response = Thread(target=read_callback, args=[data])
                process_response.start()
    return None

#method to write data to the server
def WriteToServer(state, data):
    write_list = [state._socket]
    while (state._connected == True and state._end_connection == False):
        readable, writable, errored = select.select([], write_list, [])
        for s in writable:
            if s is state._socket:
                state._socket.send(data)
                break
    return None