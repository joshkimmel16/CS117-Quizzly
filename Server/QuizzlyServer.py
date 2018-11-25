'''
This is a Python-executable server to facilitate the Quizzly application
'''

#imports
import sys
import json
import time
import random
from Config import *

sys.path.insert(0, './bin')
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

##### HELPER METHODS #####

#method to read in the questions file
def Read_Questions(path_to_questions):
    json_data = open(file_directory).read()
    return json.loads(json_data)
        

#method to write to a log file
def Write_Log(path_to_log, log_tag, log_message):
    #capture timestamp
    timestamp = time.strftime("%d/%m/%Y %H:%M:%S")
    
    #log_message is an exception
    try:
        if log_tag == "ERROR":
            with open(path_to_log, "a") as log_file:
                msg = (timestamp + '\t[' + log_tag + ']\t' + str(log_message))
        #log_message is a string
        else:
            with open(path_to_log, "a") as log_file:
                msg = (timestamp + '\t[' + log_tag + ']\t' + log_message)
    except Exception as e:
        print (str(e))

##### GAME METHODS #####

#method to create a new player in the game
def PlayerCreation(client_uuid, player_data):
    try:
        if (len(players) < 4 and not in_progress):
            for x in players:
                if client_uuid == x._connection._uuid:
                    x.InitializePlayer(player_data)
        else:
            WriteToClient(client_uuid, json.dumps({'type': 'error', 'data': {'message': "A full game is already in progress. Please try again later."}}))
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
        t_reader = Thread(target=ListenForIncomingData, args=[new_client, on_read])
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
    except Exception as e:
        Write_Log(log_path, "ERROR", e)

##### MAIN EXECUTION #####
#TODO: how to gracefully shut down???
if __name__ == "__main__":
    
    #create config and state objects
    config = Config()
    bt_config = BluetoothServerConfig(config.uuid, config.service_name)
    bt_state = BluetoothServerState()
    
    #load available questions
    log_path = config.log_path
    available_questions = Read_Questions(config.question_file_path)
    
    #start by initializing the server socket
    InitializeServerSocket(bt_state)
    
    #start listening for incoming connections in a separate thread
    t_listener = Thread(target=AdvertiseAndListen, args=[bt_config, bt_state, on_connection])
    t_listener.start()
    
    #loop indefinitely trying to run games as long as game_on flag is set
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
            in_progress = True
            score = Score(players)
            for x in players:
                try:
                    WriteToClient(x._connection._uuid, score.ToJson(False))
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
                        WriteToClient(x._connection._uuid, current_question.ToJson())
                    except Exception as e:
                        Write_Log(log_path, "ERROR", e)

                #wait for a predetermined amount of time
                time.sleep(round_wait_time)

                #send a new score update
                is_over = (round_counter == config.number_rounds - 1)
                for x in players:
                    try:
                        WriteToClient(x._connection._uuid, score.ToJson(is_over))
                    except Exception as e:
                        Write_Log(log_path, "ERROR", e)

                round_counter = round_counter + 1

            #game is over so close all open client sockets
            for x in players:
                try:
                    CloseClientSocket(x._connection._uuid)
                except Exception as e:
                    Write_Log(log_path, "ERROR", e)
            players = []
            score = None
            used_questions = {}
            current_question = None
            in_progress = False
    
    #if we get here, the server has been told to shut down
    FlagConnectionTermination(bt_state)
    CloseServerSocket(bt_state)