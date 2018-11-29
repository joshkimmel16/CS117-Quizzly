'''
This is a helper defining all data structures used by the Quizzly server
'''

#imports
import json

#object representing a player in a Quizzly game
class Player:
    #constructor
    #takes a BluetoothServerConnection object as input
    def __init__(self, conn_obj):
        self._connection = conn_obj
        self._name = ""
        
    #method to initialize the player based on data provided from a client 
    def InitializePlayer(self, data):
        self._name = data["playerName"]
        

#object representing a question in a Quizzly game
class Question:
    #constructor
    def __init__(self, data):
        self._number = data["number"]
        self._category = data["category"]
        self._question = data["question"]
        self._options = data["options"]
        self._answer = data["answer"]
    
    #convert to JSON for transmission
    def ToJson(self):
        d = {"number": self._number, "category": self._category, "question": self._question, "options": self._options, "answer": self._answer}
        return json.dumps({'type': "question", 'data': d})

#object representing an answer provided to a question
class Answer:
    #constructor
    def __init__(self, data):
        self._number = data["number"]
        self._answer = data["answer"]
        
#object representing the current score in a game    
class Score:
    #constructor
    def __init__(self, players):
        self._rankings = []
        for x in players:
            self._rankings.append({'id': x._connection._uuid, 'name': x._name, 'score': 0})
    
    #method to update the score
    def UpdateScore(self, player, question, answer):
        for x in self._rankings:
            if player._connection._uuid == x['id']:
                if question._number == answer._number and question._answer == answer._answer:
                    x['score'] = x['score'] + 1
                break
    
    #convert to JSON for transmission
    def ToJson(self, is_over):
        output = {'type': "scoreUpdate", 'data': {'isOver': is_over, 'rankings': []}}
        sorted_rankings = sorted(self._rankings, key=lambda x: x['score'], reverse=True)
        for x in sorted_rankings:
            output['data']['rankings'].append({'playerName': x['name'], 'score': x['score']})
        return json.dumps(output)