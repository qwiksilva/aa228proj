from game2 import Game, GameState
import random

game = Game()
state = game.gameState
turn = 0
while True:
    if turn % 2 == 0:
        print(turn)
    print(state.deck)
    print(state.binary)
    print(state.currentHand)
    print(state.opposingHand)
    options = state._allowedActions()
    action = options[random.randint(0, len(options)-1)]
    (state, value, done, penalizePlayer, nextPlayer) = state.takeAction(3)
    if done == 1:
        print("Done!")
        print(state.binary, value, done, penalizePlayer, nextPlayer)
    turn += 1
    if turn == 100:
        print("stopping early")
        break
