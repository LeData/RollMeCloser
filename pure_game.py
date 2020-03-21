from random import choice
from collections import defaultdict

class Die:

    side = None
    rolled = False
    locked = False

    def __init__(self, sides):
        self.sides = sides
        self.n_sides = len(self.sides)
        self.reset()

    def roll(self):
        if not self.locked:
            self.side = choice(self.sides)
            self.rolled = True

    def lock_unlock(self):
        self.locked = ~self.locked

    def reset(self):
        self.side = None
        self.rolled = False
        self.locked = False

class DiceGroup:

    def __init__(self, sides, n):
        self.dice = [Die(sides) for i in range(n)]
        self.check_state()

    def roll(self):
        for die in self.dice:
            die.roll()
        self._check_state()

    def _check_state(self):
        self.state = [die.side for die in self.dice]

    def reset(self):
        for die in self.dice:
            die.reset()


class PlayerBoard:

    def __init__(self, player_name, sides, n_dice, n_win):
        """
        :param player_name: name of the player
        :param sides: sides of the dice
        :param n: number of dice
        :param n_win: number of dice with identical side to win
        """
        self.name = player_name
        self.shield = Die(sides)
        self.hand = DiceGroup(sides, n_dice)
        self.locked = False
        self.n_win = n_win

    def pause(self):
        self.locked = True

    def display_challenge(self, action):
        self.pause()
        print(action)

    @broadcast('resume')
    def resume_play(self):
        self.locked = False
        self.broadcast_resume()

    def broadcast_resume(self):
        return {'action': 'resume'}

    def broadcast_hand(self):
        return {'state': self.hand.state}

    def broadcast_shield(self):
        return {'shield': self.shield.side}

    def reset_board(self):
        self.hand.reset()


class TableTop:

    def __init__(self, win_vp):
        self.started = False
        self.players = []
        self.n_players = len(self.players)
        self.win_VP = win_vp
        self.VP = [None] * self.win_VP

    def add_player(self, player_board):
        self.players.append(player_board)
        self.n_players = len(self.players)

    def check_win(self, player):
        roll = self.players[player].broadcast_hand()['state']
        counter = defaultdict(int)
        for face in roll:
            counter[face] += 1
            if counter[face] >= self.win_VP:
                self.broadcast_win(player, face)

    def broadcast_win(self, winner, side):
        """
        broadcast the win
        :param winner: board of the winner
        :param side: action to undertake
        """
        potential_targets = [player for player in self.players if (player.name != winner) and player.shield != side]
        for player in potential_targets:
            if player.name == winner:
                message = 'Pick a target'
            elif player in potential_targets:
                message = f'{winner} may ask you to {side}'
            else:
                message = 'You are safe. Thanks to your shield!'
            player.display_challenge(message)


    def allocate_point(self, player):
        for i, point in enumerate(self.VP):
            if point is None:
                self.VP[i] = player
                return self.VP
        self.broadcast_end()
        # TODO: broadcast/update scores on screens

    def broadcast_resume(self):
        """
        Tells the player's boards the game as resumed.
        """
        return {'action': 'resume'}

    def broadcast_end(self):
        pass