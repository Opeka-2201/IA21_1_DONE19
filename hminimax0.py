# Complete this class for all parts of the project

from pacman_module.game import Agent
from pacman_module.pacman import Directions
from pacman_module.util import PriorityQueue
from pacman_module.util import manhattanDistance
import math


def heuristic(state):
    """
    Heuristic function for hminimax0.

    Arguments:
    ----------
    -`state`: the current game state. See FAQ and class
              `pacman.GameState`.

    Return:
    -------
    - Cost of path from base node to goal node.
    """

    heuristicsSet = set()
    pacmanPos = state.getPacmanPosition()
    food = state.getFood()
    iRange = food.width
    jRange = food.height

    for i in range(0, iRange):
        for j in range(0, jRange):
            if food[i][j] is True:
                heuristicsSet.add(manhattanDistance(pacmanPos, (i, j)))

    if not heuristicsSet:
        return 0

    return min(heuristicsSet)


def cutoff(state, depth):
    """
    Checks if we need to cutoff the algorithm.

    Arguments:
    ----------
    - `state` : the current game state. See FAQ and class
                `pacman.GameState`.
    - `depth` : current depth.

    Return:
    -------
    - Boolean that checks if we need to cutoff the algorithm.
    """

    if state.isWin() or state.isLose() or depth == 4:
        return True
    else:
        return False


def aStar(state):
    """
    Implements the astar algorithm to run through the recursion tree

    Arguments:
    ----------
    - `state`: the current game state. See FAQ and class
                `pacman.GameState`.

    Return:
    -------
    - Distance to win or 0 depending on case
    """

    baseCost = 0
    baseFood = state.getFood()

    stateQueue = PriorityQueue()
    stateQueue.push((state, baseCost), 0)

    stateDict = dict()
    stateDict[state] = (None)

    visitedNodes = set()

    while not stateQueue.isEmpty():
        dontCare, (newState, baseCost) = stateQueue.pop()
        pacmanPos = newState.getPacmanPosition()
        foodUpdate = newState.getFood()

        if baseFood != foodUpdate:
            return distanceToWin(stateDict, newState)

        if (pacmanPos, foodUpdate) in visitedNodes:
            continue
        else:
            visitedNodes.add((pacmanPos, foodUpdate))
            for successor in newState.generatePacmanSuccessors():
                stateDict[successor[0]] = newState
                if foodUpdate == successor[0].getFood():
                    costIncrement = 10
                else:
                    costIncrement = 1

                heuristicCompute = heuristic(successor[0])

                costUpdate = 10 * heuristicCompute + baseCost + costIncrement
                stateQueue.push((successor[0], costIncrement + baseCost),
                                costUpdate)

    return 0


def keyHash(state, player):
    """
    Returns a unique hash to identifie the game's state (food, positions of
    ghosts (+ directions) and Pacman).

    Arguments:
    ----------
    - `state`: current gameState, see class
                `pacman.gameState`.

    Return:
    -------
    - Returns a unique hash to identifie the game's state.
    """

    return player, state.getFood(), state.getPacmanPosition(),\
        state.getGhostPosition(1), state.getGhostDirection(1)


def distanceToWin(aStarDict, aStarState):
    """
    Computes complete path cost from a node to the goal node in aStar.

    Arguments:
    ----------
    -`aStarDict`: dictionnary of states from aStar.
    -`aStarState`: actual state from aStar.

    Return:
    -------
    - An integer computing the path cost.
    """

    distance = 0

    while aStarDict[aStarState] is not None:
        aStarState = aStarDict[aStarState]
        distance += 1

    return distance


class PacmanAgent(Agent):
    def __init__(self, args):
        """
        Arguments:
        ----------
        - `args`: Namespace of arguments from command-line prompt.
        """
        self.args = args

    def get_action(self, state):
        """
        Given a pacman game state, returns a legal move.

        Arguments:
        ----------
        - `state`: the current game state. See FAQ and class
                   `pacman.GameState`.

        Return:
        -------
        - A legal move as defined in `game.Directions`.
        """

        # To avoid visiting same nodes twice, we'll keep track of visited nodes
        # in a set
        visitedNodes = set()

        # For first iteration, alpha and beta are put a infinite,
        # player = 0 = pacman, depth = 0
        return self.hminimax0(state, -math.inf, +math.inf, 0, 0, visitedNodes)

    def hminimax0(self, state, alpha, beta, player, depth, visitedNodes):
        """
        Computes h-minimax value of a node or best move if depth = 0.

        Arguments:
        ----------
        - `state`: the current game state. See FAQ and class
                   `pacman.GameState`.
        - `alpha`: bound for alpha-beta pruning.
        - `beta`: bound for alpha-beta pruning.
        - `player`: current player's index. 0 -> Pacman, >0 -> Ghosts.
        - `depth`: current depth.
        - `visitedNodes`: set of visited nodes during computation.

        Return:
        -------
        - h-minimax value of a node and best Move if depth = 0.
        """

        if cutoff(state, depth):
            return state.getScore() - aStar(state)

        if not player:
            # Player = Pacman, we need to maximize the score
            opponent = 1
            move = Directions.STOP
            value = -math.inf

            for successor in state.generatePacmanSuccessors():
                succHash = keyHash(successor[0], opponent)
                if succHash not in visitedNodes:
                    visitedNodes.add(succHash)
                else:
                    continue

                # To recursively call the function we create a copy of the set
                # of visited nodes
                copySet = visitedNodes.copy()
                temp = self.hminimax0(successor[0], alpha, beta, 1, depth + 1,
                                      copySet)

                if temp > value and temp != +math.inf:
                    value = temp
                    move = successor[1]

                if value >= beta:
                    return value

                alpha = max(value, alpha)

            if not depth:
                return move

            return value

        else:
            # Player = Ghost, we need to minimize the score
            opponent = 0
            value = +math.inf

            for successor in state.generateGhostSuccessors(1):
                succHash = keyHash(successor[0], opponent)
                if succHash not in visitedNodes:
                    visitedNodes.add(succHash)
                else:
                    continue

                copySet = visitedNodes.copy()
                temp = self.hminimax0(successor[0], alpha, beta, 0, depth + 1,
                                      copySet)

                if temp < value and temp != -math.inf:
                    value = temp
                if value <= alpha:
                    return value
                beta = max(value, beta)

            return value
