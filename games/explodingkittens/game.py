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
    EXPLODING_KITTEN = 15


class Game:

    def __init__(self):
        self.currentPlayer = 1
        self.gameState = self._initGameState()
        self.actionSpace = np.array(
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.int)
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
        next_state, value, done, next_player = self.gameState.takeAction(
            action)
        self.gameState = next_state
        self.currentPlayer = next_player
        info = None
        return ((next_state, value, done, info))

    # def identities(self, state, actionValues):
    # 	identities = [(state,actionValues)]

    # 	currentBoard = state.board
    # 	currentAV = actionValues

    # 	currentBoard = np.array([
    # 		  currentBoard[6], currentBoard[5],currentBoard[4], currentBoard[3], currentBoard[2], currentBoard[1], currentBoard[0]
    # 		, currentBoard[13], currentBoard[12],currentBoard[11], currentBoard[10], currentBoard[9], currentBoard[8], currentBoard[7]
    # 		, currentBoard[20], currentBoard[19],currentBoard[18], currentBoard[17], currentBoard[16], currentBoard[15], currentBoard[14]
    # 		, currentBoard[27], currentBoard[26],currentBoard[25], currentBoard[24], currentBoard[23], currentBoard[22], currentBoard[21]
    # 		, currentBoard[34], currentBoard[33],currentBoard[32], currentBoard[31], currentBoard[30], currentBoard[29], currentBoard[28]
    # 		, currentBoard[41], currentBoard[40],currentBoard[39], currentBoard[38], currentBoard[37], currentBoard[36], currentBoard[35]
    # 		])

    # 	currentAV = np.array([
    # 		currentAV[6], currentAV[5],currentAV[4], currentAV[3], currentAV[2], currentAV[1], currentAV[0]
    # 		, currentAV[13], currentAV[12],currentAV[11], currentAV[10], currentAV[9], currentAV[8], currentAV[7]
    # 		, currentAV[20], currentAV[19],currentAV[18], currentAV[17], currentAV[16], currentAV[15], currentAV[14]
    # 		, currentAV[27], currentAV[26],currentAV[25], currentAV[24], currentAV[23], currentAV[22], currentAV[21]
    # 		, currentAV[34], currentAV[33],currentAV[32], currentAV[31], currentAV[30], currentAV[29], currentAV[28]
    # 		, currentAV[41], currentAV[40],currentAV[39], currentAV[38], currentAV[37], currentAV[36], currentAV[35]
    # 				])

    # 	identities.append((GameState(currentBoard, state.playerTurn), currentAV))

    # 	return identities


class GameState():
    def __init__(self, deck, currentHand, opposingHand, discard, lastPlayedCard, playerTurn):
        self.deck = deck
        self.currentHand = currentHand
        self.opposingHand = opposingHand
        self.discard = discard
        self.numTypes = 10
        self.lastPlayedCard = lastPlayedCard
        self.playerTurn = playerTurn
        self.binary = self._binary()
        self.passed = False
        # self.id = self._convertStateToId()
        self.allowedActions = self._allowedActions()
        self.isEndGame = None
        self.value = self._getValue()
        self.score = self._getScore()

    def _allowedActions(self):
        allowedActions = []
        for cardType, numCards in enumerate(self.currentHand):
            if cardType == 0:
                continue
            elif cardType >= 5 and numCards >= 2:
                allowedActions.append(cardType)
            elif self.lastPlayedCard == Cards.ATTACK and cardType == 1:
                continue
            elif numCards >= 1:
                allowedActions.append(cardType)

        return allowedActions

    def _binary(self):
        lastPlayedValue = self.lastPlayedCard.value if self.lastPlayedCard != None else -1
        state = self.currentHand.copy()
        state.append(lastPlayedValue)
        state.append(len(self.deck))

        return (state)

    # def _convertStateToId(self):
    # 	player1_position = np.zeros(len(self.board), dtype=np.int)
    # 	player1_position[self.board==1] = 1

    # 	other_position = np.zeros(len(self.board), dtype=np.int)
    # 	other_position[self.board==-1] = 1

    # 	position = np.append(player1_position,other_position)

    # 	id = ''.join(map(str,position))

    # 	return id

    def _endTurn(self):
        if self.passed:
            self.isEndGame = False
            return

        card = self.deck.pop()
        if card == Cards.EXPLODING_KITTEN:
            if self.currentHand[Cards.DEFUSE.value] != 0:
                # Has a defuse
                self.currentHand[Cards.DEFUSE.value] -= 1

                # Insert E.K. into deck randomly
                position = random.randint(0, len(self.deck)-1)
                self.deck.insert(position, Cards.EXPLODING_KITTEN)
            else:
                # EndGame
                self.isEndGame = True

        else:
            self.currentHand[card.value] += 1

        self.isEndGame = False

    def _getValue(self):
        # This is the value of the state for the current player
        # i.e. if the previous player played a winning move, you lose
        if self.isEndGame != None and self.isEndGame:
            return (-1, -1, 1)
        return (0, 0, 0)

    def _getScore(self):
        tmp = self._getValue()
        return (tmp[1], tmp[2])

    def takeAction(self, action):
        # Action is an integer 0-9
        card = Cards(action)

        # Take the card out of the hand
        self.currentHand[action] -= 1
        self.discard.append(card)

        if card == Cards.ATTACK:
            self.passed = True
        elif card == Cards.SKIP:
            self.passed = True
        elif card == Cards.SHUFFLE:
            random.shuffle(self.deck)
        elif card == Cards.FAVOR or Cards.CAT1 or Cards.CAT2 \
                or Cards.CAT3 or Cards.CAT4 or Cards.CAT5:
            # Could make this better in the future by defining an order
            # in which to give up cards for favor

            # Take 2 cards from hand if a cat card was played
            if card != Cards.FAVOR:
                self.currentHand[action] -= 1
                self.discard.append(card)

            validActions = []
            for cardType, numCards in enumerate(self.opposingHand):
                if numCards > 0:
                    validActions.append(cardType)

            if validActions:
                action = random.randint(0, len(validActions)-1)
                cardAction = validActions[action]

                self.currentHand[cardAction] += 1
                self.opposingHand[cardAction] -= 1

        # Done taking actions, end turn by drawing a card and checking if the game ends
        self._endTurn()

        if self.lastPlayedCard == Cards.ATTACK:
            # Set the next players turn equal to the current players turn
            currentHand = self.currentHand
            opposingHand = self.opposingHand
            self.playerTurn = -self.playerTurn
        else:
            currentHand = self.opposingHand
            opposingHand = self.currentHand

        nextPlayer = -self.playerTurn
        newState = GameState(self.deck, currentHand,
                             opposingHand, self.discard, card, nextPlayer)
        value = 0
        done = 0

        if self.isEndGame != None and self.isEndGame == True:
            value = -1
            done = 1

        return (newState, value, done, nextPlayer)

    def render(self, logger):
        for r in range(6):
            logger.info([self.pieces[str(x)]
                         for x in self.board[7*r: (7*r + 7)]])
        logger.info('--------------')
