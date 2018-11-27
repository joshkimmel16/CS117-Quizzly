'''
This file represents the configuration for the Quizzly server
'''

class Config:
    def __init__(self):
        self.uuid = "17397638-30e6-4a5b-ac36-fbfda4b34d38" #UUID for Bluetooth service
        self.service_name = "Quizzly Server" #name for Bluetooth service
        self.log_path = './log/Quizzly.log' #path for log file
        self.question_file_path = './data/questions.json' #path for available questions file
        self.max_join_wait = 3 #this corresponds to waiting for this times join_sleep_time seconds for players to join a game
        self.join_sleep_time = 5 #this corresponds to sleeping for this number of seconds before checking whether or not the game is ready
        self.extra_join_time = 1 #give players an extra this number of seconds to create and send their usernames once all players have joined
        self.number_rounds = 8 #each game consists of this many rounds
        self.round_wait_time = 30 #each round lasts for this number of seconds
        