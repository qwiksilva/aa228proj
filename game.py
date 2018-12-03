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
        # We need grid_shape
        self.currentPlayer = 1
        self.gameState = self._initGameState()
        self.actionSpace = np.array(
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.int)
        self.name = 'exploding_kittens'
        self.state_size = len(self.gameState.binary)
        self.name = 'exploding_kittens'
        self.state_size = len(self.gameState.binary)
        self.action_size = len(self.actionSpace)
        self.input_shape = [len(self.gameState.binary)]

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
        HAND_SIZE = 4

        hand1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for _ in range(HAND_SIZE):
            card = deck.pop()
            hand1[card.value] += 1
        hand1[Cards.DEFUSE.value] = 1

        hand2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for _ in range(HAND_SIZE):
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
        # Sends out next_state, penalty, whether game is done and which player to penalize
        return ((next_state, value, done, penalizeplayer))

    def identities():### ???? Ryan please proof read
        identities = [(state,actionValues)]
        opposingHand = state.currentHand
        currentHand = state.opposingHand
        stateopp=GameState(state.deck, currentHand, opposingHand, state.discard, state.lastPlayedCard, state.currentPlayer)
        identities.append((stateopp,actionValues))


class GameState():
    def __init__(self, deck, currentHand, opposingHand, discard, lastPlayedCard, currentPlayer):
        self.deck = deck
        self.currentHand = currentHand
        self.opposingHand = opposingHand
        self.discard = discard
        self.numTypes = 10
        self.lastPlayedCard = lastPlayedCard
        self.currentPlayer = currentPlayer
        self.playerTurn = currentPlayer
        self.noDrawThisTurn = False
        self.binary = self._binary()
        self.allowedActions = self._allowedActions()
        self.isEndGame = False
        self.value = self._getValue()
        self.score = self._getScore()
        self.id = str(self.binary)

    def _allowedActions(self):
        allowedActions = [10]
        for cardType, numCards in enumerate(self.currentHand):
            if cardType == 0:
                # This action signifies playing a defuse card. Disallow for now, but we can potentially
                # have the agent learn that they should never play this card to show that the agent
                # is learning something
                continue
            elif self.lastPlayedCard == Cards.ATTACK and cardType == 1:
                # To simplify, disallow playing an attack card the first turn after
                # one has just been played
                continue
            elif cardType < 5 and numCards >= 1:  # ????
                allowedActions.append(cardType)
            # Hey Ryan ???? What special condition happens when this is triggered redundant
            elif cardType >= 5 and numCards >= 2:
                # Game rules dictate there must be 2 of a kind to play a 'CAT' card
                allowedActions.append(cardType)
        return allowedActions

    #  binarizes the state observed according to the current player
    def _binary(self):
        lastPlayedValue = self.lastPlayedCard.value if self.lastPlayedCard != None else -1
        state = self.currentHand.copy()
        state.append(lastPlayedValue)
        state.append(len(self.deck))
        return np.array(state)

    # End the turn by drawing a card. Don't draw if noDrawThisTurn (i.e. an attack or skip was played)
    # Returns whether the game ended due to an exploding kitten or not
    def _endTurn(self):
        newDeck = self.deck.copy()
        if self.noDrawThisTurn:
            return False, newDeck
        card = newDeck.pop()
        if card == Cards.EXPLODING_KITTEN:
            if self.currentHand[Cards.DEFUSE.value] != 0:
                # Has a defuse
                self.currentHand[Cards.DEFUSE.value] -= 1
                # Insert E.K. into deck randomly
                if len(self.deck) == 0:
                    newDeck.insert(0, Cards.EXPLODING_KITTEN)
                else:
                    position = random.randint(0, len(self.deck)-1)
                    newDeck.insert(position, Cards.EXPLODING_KITTEN)
            else:
                # EndGame
                return True, newDeck
        else:
            self.currentHand[card.value] += 1

        return False, newDeck

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

        # Due to the way the MCTS algorithm is written, a state needs to be static
        # So only update newState, not the current state by making a copy of the current state
        # A copy of the new deck is returned by endTurn() below
        newDiscard = self.discard.copy()
        newCurrentHand = self.currentHand.copy()
        newOpposingHand = self.opposingHand.copy()

        # Take the card out of the hand
        if card != Cards.NULL:
            newCurrentHand[action] -= 1
            newDiscard.append(card)

        if card == Cards.ATTACK:
            self.noDrawThisTurn = True
        elif card == Cards.SKIP:
            self.noDrawThisTurn = True
        elif card == Cards.SHUFFLE:
            random.shuffle(self.deck)
        elif (card == Cards.FAVOR) or (card == Cards.CAT1) or (card == Cards.CAT2) or (card == Cards.CAT3) or (card == Cards.CAT4) or (card == Cards.CAT5):

            # Take 2 cards from hand if a cat card was played
            if card != Cards.FAVOR:
                newCurrentHand[action] -= 1
                newDiscard.append(card)

            newCurrentHand[action]
            validActions = []
            for cardType, numCards in enumerate(newOpposingHand):
                if numCards > 0:
                    validActions.append(cardType)

            if validActions:
                action = random.randint(0, len(validActions)-1)
                chosenCard = validActions[action]

                newCurrentHand[chosenCard] += 1
                newOpposingHand[chosenCard] -= 1

        # Done taking actions, end turn by drawing a card and checking if the game ends
        self.isEndGame, newDeck = self._endTurn()

        if self.lastPlayedCard == Cards.ATTACK:
            # Set the next players turn equal to the current players turn
            nextPlayer = self.currentPlayer
        else:
            nextPlayer = -self.currentPlayer

        # if self.lastPlayedCard == Cards.ATTACK:
        #     # If the last card played was an attack, the next player is the same as the current player
        #     # Otherwise the state reverses
        #     nextPlayer = self.currentPlayer
        #     newState = GameState(newDeck, newCurrentHand,
        #                          newOpposingHand, newDiscard, card, nextPlayer)
        # else:
        #     nextPlayer = -self.currentPlayer
        #     newState = GameState(newDeck, newOpposingHand,
        #                          newCurrentHand, newDiscard, card, nextPlayer)

        # ???? Shouldn't the state reverse based on whether an attack card was played last?
        if self.currentPlayer == 1:
            # The game states reverse every time
            newState = GameState(newDeck, newCurrentHand,
                                 newOpposingHand, newDiscard, card, nextPlayer)
        else:
            newState = GameState(newDeck, newOpposingHand,
                                 newCurrentHand, newDiscard, card, nextPlayer)
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
