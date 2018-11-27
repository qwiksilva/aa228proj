import numpy as np
import logging
import random
from enum import Enum

# Mapping from Card Type to position (index) in the Agent's state


class Cards(Enum):
    DEFUSE = 0
    ATTACK = 1
    SKIP = 2
    FAVOR = 3
    SHUFFLE = 4
    CAT1 = 5
    CAT2 = 6
    CAT3 = 7
    CAT4 = 8
    CAT5 = 9
    NULL = 10
    EXPLODING_KITTEN = 15


class Game:
    def __init__(self):
        self.currentPlayer = 1
        self.gameState = self._initGameState()
        # ???? does this include the all Null action? (No card played)
        self.actionSpace = np.array(
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.int)
        self.name = 'exploding_kittens'
        self.state_size = len(self.gameState.binary)
        self.action_size = len(self.actionSpace)

    def _initGameState(self):
        # Put all card in deck except E.K. and 2 defuse
        deck = [Cards.DEFUSE, Cards.DEFUSE,
                Cards.ATTACK, Cards.ATTACK, Cards.ATTACK, Cards.ATTACK,
                Cards.SKIP, Cards.SKIP, Cards.SKIP, Cards.SKIP,
                Cards.FAVOR, Cards.FAVOR, Cards.FAVOR, Cards.FAVOR,
                Cards.SHUFFLE, Cards.SHUFFLE, Cards.SHUFFLE, Cards.SHUFFLE,
                Cards.CAT1, Cards.CAT1, Cards.CAT1, Cards.CAT1,
                Cards.CAT2, Cards.CAT2, Cards.CAT2, Cards.CAT2,
                Cards.CAT3, Cards.CAT3, Cards.CAT3, Cards.CAT3,
                Cards.CAT4, Cards.CAT4, Cards.CAT4, Cards.CAT4,
                Cards.CAT5, Cards.CAT5, Cards.CAT5, Cards.CAT5]

        # Shuffle deck
        random.shuffle(deck)

        # Deal hands (including 1 defuse)
        handSize = 4

        hand1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for _ in range(handSize):
            card = deck.pop()
            hand1[card.value] += 1
        hand1[Cards.DEFUSE.value] = 1

        hand2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for _ in range(handSize):
            card = deck.pop()
            hand2[card.value] += 1
        hand2[Cards.DEFUSE.value] = 1

        # Insert E.K. into deck randomly
        position = random.randint(0, len(deck)-1)
        deck.insert(position, Cards.EXPLODING_KITTEN)
        return GameState(deck, hand1, hand2, [], None, self.currentPlayer)

    def reset(self):
        self.currentPlayer = 1
        self.gameState = self._initGameState()
        return self.gameState

    def step(self, action):
        next_state, value, done, penalizeplayer, next_player = self.gameState.takeAction(
            action)  # Added a penalize player to penalize the right player
        self.gameState = next_state
        self.currentPlayer = next_player
        info = None
        return ((next_state, value, done, info))


class GameState():
    def __init__(self, deck, currentHand, opposingHand, discard, lastPlayedCard, currentPlayer):
        self.deck, self.discard = self._initDeck(deck, discard)
        self.currentHand = currentHand
        self.opposingHand = opposingHand
        # self.discard = discard
        self.numTypes = 10
        self.lastPlayedCard = lastPlayedCard
        self.currentPlayer = currentPlayer
        self.noDrawThisTurn = False
        self.binary = self._binary()
        self.allowedActions = self._allowedActions()
        self.isEndGame = False
        self.value = self._getValue()
        self.score = self._getScore()

    def _initDeck(self, deck, discard):
        if len(deck) == 0:
            deck = discard
            discard = []
            random.shuffle(deck)
        return deck, discard

    # I forgot in my original design that I had action 0 be the NULL or 'don't play a card'
    # In the hand, slot 0 is for the defuse card, which ideally should never be played by the player
    # (in _endTurn(), a defuse is automatically played if needed), so we can instead use
    # action 0 to mean NULL; or we can keep action 10 to signify NULL action. Either way works.

    def _allowedActions(self):
        allowedActions = [10]
        for cardType, numCards in enumerate(self.currentHand):
            if cardType == 0:
                continue
            # Hey Ryan ???? What special condition happens when this is triggered redundant
            elif cardType >= 5 and numCards >= 2:
                # Game rules dictate there must be 2 of a kind to play a 'CAT' card
                allowedActions.append(cardType)
            elif self.lastPlayedCard == Cards.ATTACK and cardType == 1:
                # To simplify, disallow playing an attack card the first turn after
                # one has just been played
                continue
            elif cardType < 5 and numCards >= 1:  # ????
                allowedActions.append(cardType)
        return allowedActions

    # Binary binarizes the state observed according to the current player
    def _binary(self):
        lastPlayedValue = self.lastPlayedCard.value if self.lastPlayedCard != None else -1
        state = self.currentHand.copy()
        state.append(lastPlayedValue)
        state.append(len(self.deck))
        return (state)

    def _endTurn(self):
        if self.noDrawThisTurn:
            # self.isEndGame = False  # ????
            return
        card = self.deck.pop()
        if card == Cards.EXPLODING_KITTEN:
            if self.currentHand[Cards.DEFUSE.value] != 0:
                # Has a defuse
                self.currentHand[Cards.DEFUSE.value] -= 1
                # Insert E.K. into deck randomly
                if len(self.deck) == 0:
                    self.deck.insert(0, Cards.EXPLODING_KITTEN)
                else:
                    position = random.randint(0, len(self.deck)-1)
                    self.deck.insert(position, Cards.EXPLODING_KITTEN)
            else:
                # EndGame
                self.isEndGame = True
        else:
            self.currentHand[card.value] += 1

    def _getValue(self):
        # This is the value of the state for the current player
        # i.e. if the previous player played a winning move, you lose
        if self.isEndGame:
            return (-1, -1, 1)
        return (0, 0, 0)

    def _getScore(self):
        tmp = self._getValue()
        return (tmp[1], tmp[2])

    def takeAction(self, action):
        # I'm unsure if the allowedActions() function completely eliminates actions. If it does
        # then the self.currentHand[action]>0 case is covered, if not then we need to check
        # for it again here.
        card = Cards(action)
        # Take the card out of the hand
        self.currentHand[action] -= 1
        self.discard.append(card)
        if card == Cards.NULL:
            pass
        elif card == Cards.ATTACK:
            self.noDrawThisTurn = True  # self.passed ensures that the next guy skips his turn ????
        elif card == Cards.SKIP:
            self.noDrawThisTurn = True  # self.passed ensures that the next guy skips his turn ????
        elif card == Cards.SHUFFLE:
            random.shuffle(self.deck)
        elif (card == Cards.FAVOR) or (card == Cards.CAT1) or (card == Cards.CAT2)or (card == Cards.CAT3) or (card == Cards.CAT4) or (card == Cards.CAT5):  # ???????????????

            # Take 2 cards from hand if a cat card was played ????
            if card != Cards.FAVOR:
                self.currentHand[action] -= 1
                self.discard.push(card)
        # Nothing happens if action == 10, i.e. the player doesn't play a card

            # Acts like FAVOUR
            self.currentHand[action]
            validActions = []
            for cardType, numCards in enumerate(self.opposingHand):
                if numCards > 0:
                    validActions.append(cardType)

            if validActions:
                action = random.randint(0, len(validActions)-1)
                chosenCard = validActions[action]

                self.currentHand[chosenCard] += 1
                self.opposingHand[chosenCard] -= 1

        # Done taking actions, end turn by drawing a card and checking if the game ends
        self._endTurn()

        if self.lastPlayedCard == Cards.ATTACK:
            # Set the next players turn equal to the current players turn
            currentHand = self.currentHand
            opposingHand = self.opposingHand
            self.currentPlayer = -self.currentPlayer
        else:
            currentHand = self.opposingHand
            opposingHand = self.currentHand

        nextPlayer = -self.currentPlayer
        newState = GameState(self.deck, currentHand,
                             opposingHand, self.discard, card, nextPlayer)
        value = 0
        done = 0
        if self.isEndGame == True:
            value = -1
            done = 1
        return (newState, value, done, self.currentPlayer, nextPlayer)


'''

	def render(self, logger):
		for r in range(6):
			logger.info([self.pieces[str(x)] for x in self.board[7*r : (7*r + 7)]])
		logger.info('--------------')
'''
