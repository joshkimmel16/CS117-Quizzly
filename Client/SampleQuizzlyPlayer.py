'''
This is a sample Quizzly client that serves primarily for testing purposes
'''

import sys
import os
from sys import path
from threading import Thread
import time
import json
from random import randint
from Queue import Queue
from BluetoothClient import *

##### GLOBAL VARIABLES #####
game_over = False
work_queue = Queue()
uuid = "17397638-30e6-4a5b-ac36-fbfda4b34d38"
bt_config = BluetoothClientConfig(uuid)
bt_state = BluetoothClientState()

##### GAME PLAY METHODS #####

def Question(q_data):
    print "Category: " + q_data['category']
    print q_data["question"]
    for x in q_data["options"]:
        print x
    print ""
    i = input("Please enter an answer 0-3: ")
    r = '{"type": "answer", "data": {"number": ' + str(q_data["number"]) + ', "answer": ' + str(i) + '}}'
    WriteToServer(bt_state, r)
    print "\n"

def ShowScore(s_data):
    for x in s_data["rankings"]:
        print x["playerName"] + " has score : " + str(x["score"])
    print "\n"
    if s_data["isOver"] == True:
        print 'The game is now over!'
        game_over = True
    else:
        print "Moving to next round!"
        print "\n"

##### EVENT HANDLERS #####

#define callback to be used for incoming reads
def on_read(response):
    try:
        data = json.loads(response)
        work_queue.put(data)
    except Exception as e:
        print str(e)

##### MAIN EXECUTION #####
if __name__ == "__main__":
    
    #get and print all server candidates
    GetConnectionCandidates(bt_state, bt_config)
        
    #connect to the first candidate
    try:
        if len(bt_state._connection_candidates) > 0:
            ConnectToBluetoothServer(bt_state, bt_state._connection_candidates[0])

            #start listening for data from the server on a seperate thread
            t_listener = Thread(target=ReadFromServer, args=[bt_state, on_read])
            t_listener.daemon = True
            t_listener.start()

            #create the player
            p_name = input("Please enter your name: ")
            p = '{"type": "playerCreation", "data": {"playerName": "' + str(p_name) + '"}}'
            WriteToServer(bt_state, p)

            while (not game_over):
                while not work_queue.empty():
                    task = work_queue.get()
                    try:
                        if task['type'] == 'question':
                            Question(task['data'])
                        elif task['type'] == 'scoreUpdate':
                            ShowScore(task['data'])
                        elif task['type'] == 'socketError':
                            print 'The server socket is no longer readable'
                            game_over = True
                    except Exception as e:
                        print str(e)
                    time.sleep(1)
                time.sleep(2)
        else:
            print "Could not detect any Bluetooth devices!"
    except KeyboardInterrupt:
        game_over = True
        
    DisconnectFromBluetoothServer(bt_state)