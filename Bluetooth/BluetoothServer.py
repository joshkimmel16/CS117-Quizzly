'''
Provides an interface and implementation for communicating via Bluetooth on the server side
'''

#imports
import bluetooth
from threading import Thread
import select
import uuid

#object representing the configuration parameters for a Bluetooth server
class BluetoothServerConfig:
    #constructor
    def __init__(self, uuid, service_name):
        self._uuid = uuid #UUID for Bluetooth Server
        self._service_name = service_name #Name of service being provided

#object representing the state of the server at any given time
class BluetoothServerState:
    #constructor
    def __init__(self):
        self._server_socket = None
        self._online = False
        self._num_connections = 0

#object representing a successfully connected client to the server
class BluetoothServerConnection:
    #constructor
    def __init__(self, uuid, client_socket, client_address):
        self._uuid = uuid
        self._client_socket = client_socket
        self._client_address = client_address
        self._is_open = True
        
#method to intialize the communication socket
#Returns: initialized server socket
def InitializeServerSocket (state):
    state._server_socket = bluetooth.BluetoothSocket( bluetooth.RFCOMM )

#method to begin advertising and then listen for incoming connections.
#this method should run in its own thread
#pass in a configuration, initial state, and a callback to execute when a successful connection is made
def AdvertiseAndListen (config, state, connection_callback):
    #set up and start listening
    port = bluetooth.PORT_ANY
    state._server_socket.bind(("", port))
    state._server_socket.listen(1)
    bluetooth.advertise_service(state._server_socket, config._service_name,
                   service_id = config._uuid,
                   service_classes = [ config._uuid, bluetooth.SERIAL_PORT_CLASS ],
                   profiles = [ bluetooth.SERIAL_PORT_PROFILE ], 
                    )
    
    state._online = True
    while (state._online == True and state._server_socket != None):
        #can't have more than 7 active client connections
        if state._num_connections < 8:
            #use select to poll the socket
            read_list = [state._server_socket]
            while (state._online == True and state._server_socket != None):
                readable, writable, errored = select.select(read_list, [], [])
                for s in readable:
                    if s is state._server_socket:
                        client_socket,client_address = state._server_socket.accept()
                        client_id = uuid.uuid4()
                        b = BluetoothServerConnection(client_id, client_socket, client_address)
                        process_client = Thread(target=connection_callback, args=[b])
                        process_client.start()
                        state._num_connections = state._num_connections + 1
                        break
    return None

#method to close the communication socket
def CloseServerSocket (state):
    if state._online == True and state._num_connections == 0:
        state._server_socket.close()
        state._server_socket = None
        state._online = False
        state._num_connections = 0
    return None

#method to close the communication socket for all provided clients
def CloseClientSocket(client, state):
    if state._online and client._is_open == True:
        client._client_socket.close()
        client._is_open = False
        state._num_connections = state._num_connections - 1
    return None

#method to listen for incoming data from a specific client
#this method should be run in a single thread per client
def ListenForIncomingData (client, read_callback):
    read_list = [client._client_socket]
    while (state._online == True and state._server_socket != None and client._is_open == True):
        readable, writable, errored = select.select(read_list, [], [])
        for s in readable:
            if s is client._client_socket:
                data = s.recv()
                process_response = Thread(target=read_callback, args=[client._uuid, data])
                process_response.start()
    return None

#method to write data to a specific client
def WriteToClient (client, data):
    write_list = [client._client_socket]
    while (state._online == True and state._server_socket != None and client._is_open == True):
        readable, writable, errored = select.select([], write_list, [])
        for s in writable:
            if s is client._client_socket:
                client._client_socket.send(data)
                break
    return None