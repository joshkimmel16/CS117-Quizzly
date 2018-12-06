'''
This is a Python-executable server to facilitate the Quizzly application
'''

#imports
import sys
import os
from sys import path
import json
import time
import random
from Config import *

sys.path.insert(0, './data')
from DataStructures import *

sys.path.insert(0, '../Bluetooth')
from BluetoothServer import *

##### GAME VARIABLES #####
game_on = True
log_path = ""
players = []
avaiable_questions = []
used_questions = {}
score = None
current_question = None
in_progress = False
bt_state = None

##### HELPER METHODS #####

#method to read in the questions file
def Read_Questions(path_to_questions):
    json_data = open(path_to_questions).read()
    return json.loads(json_data)
        

#method to write to a log file
def Write_Log(path_to_log, log_tag, log_message):
    #capture timestamp
    timestamp = time.strftime("%d/%m/%Y %H:%M:%S")
    
    #log_message is an exception
    try:
        if log_tag == "ERROR":
            with open(path_to_log, "a") as log_file:
                msg = (timestamp + '\t[' + log_tag + ']\t' + str(log_message) + "\n")
                log_file.write(msg)
        #log_message is a string
        else:
            with open(path_to_log, "a") as log_file:
                msg = (timestamp + '\t[' + log_tag + ']\t' + log_message + "\n")
                log_file.write(msg)
    except Exception as e:
        print (str(e))

##### GAME METHODS #####

#method to create a new player in the game
def PlayerCreation(client_uuid, player_data):
    client = None
    for x in players:
        if client_uuid == x._connection._uuid:
            client = x
            break
    
    try:
        if (len(players) < 4 and not in_progress and client != None):
            client.InitializePlayer(player_data)
        else:
            if client != None:
                WriteToClient(bt_state, client._connection, json.dumps({'type': 'error', 'data': {'message': "A full game is already in progress. Please try again later."}}))
            else:
                Write_Log(log_path, "ERROR", "UUID: " + client_uuid + " is missing!")
    except Exception as e:
        Write_Log(log_path, "ERROR", e)

#method to capture an answer provided by a player
def CaptureAnswer(client_uuid, provided_answer):
    try:
        a = Answer(provided_answer)
        for x in players:
            if client_uuid == x._connection._uuid:
                score.UpdateScore(x, current_question, a)
    except Exception as e:
        Write_Log(log_path, "ERROR", e)

##### EVENT HANDLERS #####

#method to handle new players being added to the game
def on_connection(new_client):
    try:
        players.append(Player(new_client))
        t_reader = Thread(target=ListenForIncomingData, args=[bt_state, new_client, on_read])
        t_reader.daemon = True
        t_reader.start()
    except Exception as e:
        Write_Log(log_path, "ERROR", e)
    
#method to handle incoming reads from a client socket
def on_read(client_uuid, response):
    try:
        data = json.loads(response)
        if data['type'] == 'playerCreation':
            PlayerCreation(client_uuid, data['data'])
        elif data['type'] == 'answer':
            CaptureAnswer(client_uuid, data['data'])
        elif data['type'] == 'socketError':
            Write_Log(log_path, "INFO", "Socket for client " + str(client_uuid) + " has been closed.")
    except Exception as e:
        Write_Log(log_path, "ERROR", e)

##### MAIN EXECUTION #####
if __name__ == "__main__":
    
    #create config and state objects
    config = Config()
    bt_config = BluetoothServerConfig(config.uuid, config.service_name)
    bt_state = BluetoothServerState()
    
    #load available questions
    log_path = config.log_path
    available_questions = Read_Questions(config.question_file_path)
    Write_Log(log_path, "INFO", "The Quizzly server is coming online.")
    
    #start by initializing the server socket
    InitializeServerSocket(bt_state)
    
    #start listening for incoming connections in a separate thread
    t_listener = Thread(target=AdvertiseAndListen, args=[bt_config, bt_state, on_connection])
    t_listener.daemon = True
    t_listener.start()
    
    #loop indefinitely trying to run games as long as game_on flag is set
    try:
        while (game_on):

            #wait for 4 players or a predetermined amount of time
            sleep_count = 0
            while (sleep_count < config.max_join_wait and len(players) < 4):
                time.sleep(config.join_sleep_time)
                sleep_count = sleep_count + 1

            #give players an extra bit of time to create their usernames
            time.sleep(config.extra_join_time)

            #only continue this game if there are players in it
            if len(players) > 0:
                #start by initializing the score and sending an initial score update
                Write_Log(log_path, "INFO", "The game has begun.")
                in_progress = True
                score = Score(players)
                for x in players:
                    try:
                        WriteToClient(bt_state, x._connection, score.ToJson(False))
                    except Exception as e:
                        Write_Log(log_path, "ERROR", e)

                #loop through a predetermined number of rounds
                round_counter = 0
                while (round_counter < config.number_rounds):
                    #pick an unused question in this game
                    q_found = False
                    while (not q_found):
                        pot = random.choice(available_questions)
                        if not pot['number'] in used_questions:
                            current_question = Question(pot)
                            used_questions[pot['number']] = True
                            q_found = True

                    #send the question to each player
                    for x in players:
                        try:
                            WriteToClient(bt_state, x._connection, current_question.ToJson())
                        except Exception as e:
                            Write_Log(log_path, "ERROR", e)

                    #wait for a predetermined amount of time
                    time.sleep(config.round_wait_time)

                    #send a new score update
                    is_over = (round_counter == config.number_rounds - 1)
                    for x in players:
                        try:
                            WriteToClient(bt_state, x._connection, score.ToJson(is_over))
                        except Exception as e:
                            Write_Log(log_path, "ERROR", e)

                    round_counter = round_counter + 1
                    time.sleep(config.score_wait_time) #yield CPU

                #game is over so close all open client sockets
                for x in players:
                    try:
                        CloseClientSocket(x._connection, bt_state)
                    except Exception as e:
                        Write_Log(log_path, "ERROR", e)
                players = []
                score = None
                used_questions = {}
                current_question = None
                in_progress = False
                Write_Log(log_path, "INFO", "The game has ended.")
    except KeyboardInterrupt:
        game_on = False
    
    #if we get here, the server has been told to shut down
    Write_Log(log_path, "INFO", "The Quizzly server is shutting down.")
    CloseServerSocket(bt_state)