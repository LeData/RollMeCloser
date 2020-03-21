import PodSixNet.Channel
import PodSixNet.Server
import funtools

from pure_game import TableTop
from time import sleep

def trigger_start(func):
    """
    Decorator that starts every game in the queue of a DiceServer that pass the start condition at the end of a function
    """
    @functools.wrap(func)
    def queue_updated(self, *args, *kwargs):
        func(self, *args, *kwargs)
        for game in self.queue:
            if game.check_start():
                self._start(game)

    return queue_updated

class ClientChannel(PodSixNet.Channel.Channel):
    def Network(self, data):
        """
        called every time a client  does a connection.send(data)
        """
        print(data)

    def Network_score(self, data):
        """
        called when the data passed to connection.send() contains {'action': 'score'}
        """
        self.gameid = data.pop('game_id')
        self._server.score_point_for( self.gameid, data)

    def Network_startgame(self, data):
        """
        called when the data passed to connection.send() contains {'action': 'startgame'}
        """
        self.gameid = data.pop('game_id')
        self._server.score_point_for(self.gameid, data)

class DiceServer(PodSixNet.Server.Server):
    channelClass = ClientChannel

    def __init__(self, game_class, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.game = game_class
        self.games = {} # games that have run or are running on the server
        self.queue = {} # open games

    def _add_new_game_to_queue(self, length = 10):
        # create new game and add it to the queue
        gameid = len(games) + len(queue) +1
        self.queue[current_index] = self.game(gameid, length)
        return gameid

    def _start(self, game):
        for i, player in enumerate(game.players):
            player.Send({"action": "startgame", "player": i, "gameid": game.game_id})
        self.games.append(self.queue.pop(game))


    @trigger_start
    def Connected(self, player_channel, gameid = None):
        """
        TODO: rename as new_player
        gets called whenever a new client connects to the server.
        """

        if gameid is not None:
            if gameid in self.games.keys():
                print("this game has already started")
                return self
            if gameid not in self.queue.keys():
                print("No such game to join, creating one")
                game = None

        if gameid is None:
            game = self._add_new_game_to_queue(player_channel)

        print('Player {player_channel} connected to {self.queue[0].gameid}')
        self.queue[game].add_player(player_channel)
        return self


    def score_point_for(self, game_id, **kwargs):
        #TODO : make this function work for all methods in the GameManager
        game = [a for a in self.games if a.gameid == game_id]
        if len(game) == 1:
            game[0].score_point_for(**kwargs)


class GameManager:

    def __init__(self, gameid, length = 10):
        self.len = length
        self.gameid = gameid
        self.started = False
        # initialize VP ownership
        self.VP = []
        #initialize the player list
        self.players = []
        self.scores = default_dict(int)

    def score_for(self, player, points=1):
        self.VP = self.VP.append(player)
        self.scores[player] += points

    def add_player(self, player):
        player.gameid = self.gameid
        self.players.append(player)

    def check_start(self):
        self.started = self.players >=2
        return self.started

    def check_end(self):
        self.terminated = len(VP) >= self.len
        return self.terminated


class RandomQuestionGenerator:

    def get_question(self, hotness:int = 1):
        random_question = "What was the hottest sex you've had?"
        return random_question



print("STARTING SERVER ON LOCALHOST")
DateServe = DiceServer()
while True:
    DiceServer.Pump()
    sleep(0.01)
