from game2 import Game, GameState
import random
import unitTests


def randomGame(score):
    game = Game()
    state = game.gameState
    turn = 0
    while True:
        # print(turn)
        # print(state.deck)
        # print(state.binary)
        # print(state.currentHand)
        # print(state.opposingHand)
        options = state._allowedActions()
        action = options[random.randint(0, len(options)-1)]
        # print("action", action)
        (state, value, done, penalizePlayer, nextPlayer) = state.takeAction(action)
        if done == 1:
            # print("Done!")
            # print(state.binary, value, done, penalizePlayer, nextPlayer)
            return score + penalizePlayer
        turn += 1


score = 0
for i in range(10000):
    if i % 1000 == 0:
        print(i)
    score = randomGame(score)

print("Score:", score)
