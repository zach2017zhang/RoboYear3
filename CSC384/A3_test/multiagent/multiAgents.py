# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util
from math import sqrt

from game import Agent

class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        #print newPos
        #print newFood
        #print newGhostStates
        #print newScaredTimes
        #print successorGameState.getScore()
        if successorGameState.isWin():
            return 100000
        if successorGameState.isLose():
            return -100000
        
        #current score
        score = 5*successorGameState.getScore()
        
        #ghost position
        for ghostPosition in successorGameState.getGhostPositions():
            if manhattanDistance(ghostPosition, newPos) < 2:
                score -= 200
            else:
                score += sqrt(manhattanDistance(ghostPosition, newPos))
        
        #food position
        foodDistance = min([manhattanDistance(foodPosition, newPos) for foodPosition in newFood.asList()])
        score -= 3*foodDistance
        if newPos in currentGameState.getFood().asList():
            score += 20
        
        #capsule position
        if not currentGameState.getCapsules() == []:
            if min([manhattanDistance(capsulePosition, newPos) for capsulePosition in currentGameState.getCapsules()]) < 2:
                score += 30
            if newPos in currentGameState.getCapsules():
                score += 20
        
        #get away from corners
        score += 3*len(successorGameState.getLegalPacmanActions())
        
        #always move
        if action == Directions.STOP:
            score -= 10
                    
        return score

def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """
    def DFMinimax(self,gameState, agentIndex, curDepth):
        if gameState.isWin() or gameState.isLose() or curDepth == 0:
            return self.evaluationFunction(gameState), Directions.STOP
        legalActions = gameState.getLegalActions(agentIndex)
        bestAction = Directions.STOP
        if agentIndex == 0:
            value = -(float("inf"))
            for action in legalActions:
                actionValue = self.DFMinimax(gameState.generateSuccessor(agentIndex, action),agentIndex+1,curDepth)[0]
                if actionValue > value:
                    bestAction = action
                    value = actionValue
        else:
            value = float("inf")
            for action in legalActions:
                if agentIndex == (gameState.getNumAgents()-1):
                    actionValue = self.DFMinimax(gameState.generateSuccessor(agentIndex, action),0,curDepth-1)[0]
                else:
                    actionValue = self.DFMinimax(gameState.generateSuccessor(agentIndex, action),agentIndex+1,curDepth)[0]
                if actionValue < value:
                    bestAction = action
                    value = actionValue
        return value, bestAction
                
    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game
        """
        "*** YOUR CODE HERE ***"
        return self.DFMinimax(gameState, 0, self.depth)[1]
        #util.raiseNotDefined()

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """
    def alphaBeta(self,gameState, agentIndex, curDepth,alpha, beta):
        if gameState.isWin() or gameState.isLose() or curDepth == 0:
            return self.evaluationFunction(gameState), Directions.STOP, self.evaluationFunction(gameState)
        legalActions = gameState.getLegalActions(agentIndex)
        bestAction = Directions.STOP
        if agentIndex == 0:
            value = -(float("inf"))
            for action in legalActions:
                actionValue,notUsed,alphaValue = self.alphaBeta(gameState.generateSuccessor(agentIndex, action),agentIndex+1,curDepth,alpha, beta)
                if actionValue > value:
                    bestAction = action
                    value = actionValue
                if alphaValue > alpha:
                    alpha = alphaValue
                if alpha >= beta:
                    break
            return value, bestAction, alpha
        else:
            value = float("inf")
            for action in legalActions:
                if agentIndex == (gameState.getNumAgents()-1):
                    actionValue,notUsed,betaValue = self.alphaBeta(gameState.generateSuccessor(agentIndex, action),0,curDepth-1,alpha, beta)
                else:
                    actionValue,notUsed,betaValue = self.alphaBeta(gameState.generateSuccessor(agentIndex, action),agentIndex+1,curDepth,alpha, beta)
                if actionValue < value:
                    bestAction = action
                    value = actionValue
                if betaValue < beta:
                    beta = betaValue
                if alpha >= beta:
                    break
            return value, bestAction, beta

        
    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        return self.alphaBeta(gameState, 0, self.depth,-(float("inf")),float("inf"))[1]
        #util.raiseNotDefined()

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """
    def Expectimax(self,gameState, agentIndex, curDepth):
        if gameState.isWin() or gameState.isLose() or curDepth == 0:
            return self.evaluationFunction(gameState), Directions.STOP
        legalActions = gameState.getLegalActions(agentIndex)
        bestAction = Directions.STOP
        if agentIndex == 0:
            value = -(float("inf"))
            for action in legalActions:
                actionValue = self.Expectimax(gameState.generateSuccessor(agentIndex, action),agentIndex+1,curDepth)[0]
                if actionValue > value:
                    bestAction = action
                    value = actionValue
        else:
            value = 0
            for action in legalActions:
                if agentIndex == (gameState.getNumAgents()-1):
                    actionValue = self.Expectimax(gameState.generateSuccessor(agentIndex, action),0,curDepth-1)[0]
                else:
                    actionValue = self.Expectimax(gameState.generateSuccessor(agentIndex, action),agentIndex+1,curDepth)[0]
                value += actionValue
            value = float(value)/len(legalActions)
        return value, bestAction
        
    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        return self.Expectimax(gameState, 0, self.depth)[1]
        util.raiseNotDefined()

def helperEvaluation(gameState, agentIndex, curDepth,alpha, beta):
    if gameState.isWin() or gameState.isLose() or curDepth == 0:
        return gameState.getScore(), Directions.STOP, gameState.getScore()
    legalActions = gameState.getLegalActions(agentIndex)
    bestAction = Directions.STOP
    if agentIndex == 0:
        value = -(float("inf"))
        for action in legalActions:
            actionValue,notUsed,alphaValue = helperEvaluation(gameState.generateSuccessor(agentIndex, action),agentIndex+1,curDepth,alpha, beta)
            if actionValue > value:
                bestAction = action
                value = actionValue
            if alphaValue > alpha:
                alpha = alphaValue
            if alpha >= beta:
                break
        return value, bestAction, alpha
    else:
        value = float("inf")
        for action in legalActions:
            if agentIndex == (gameState.getNumAgents()-1):
                actionValue,notUsed,betaValue = helperEvaluation(gameState.generateSuccessor(agentIndex, action),0,curDepth-1,alpha, beta)
            else:
                actionValue,notUsed,betaValue = helperEvaluation(gameState.generateSuccessor(agentIndex, action),agentIndex+1,curDepth,alpha, beta)
            if actionValue < value:
                bestAction = action
                value = actionValue
            if betaValue < beta:
                beta = betaValue
            if alpha >= beta:
                break
        return value, bestAction, beta

def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    #print helperEvaluation(currentGameState, 0, 2,-(float("inf")),float("inf"))[0]

    # Useful information you can extract from a GameState (pacman.py)

    newPos = currentGameState.getPacmanPosition()
    
    if currentGameState.isWin():
        return float("inf")
    if currentGameState.isLose():
        return -(float("inf"))
    
    score = currentGameState.getScore()
    
    #food position
    score -= 50*len(currentGameState.getFood().asList())
    newFood = currentGameState.getFood()
    for foodPosition in newFood.asList():
        score -= sqrt(manhattanDistance(foodPosition, newPos))*20/len(currentGameState.getFood().asList())
    #foodDistance = min([manhattanDistance(foodPosition, newPos) for foodPosition in newFood.asList()])
    #score -= 4*foodDistance

    #capsule position
    score -= 2000*len(currentGameState.getCapsules())
    if not currentGameState.getCapsules() == []:
        capsuleDistance = min([manhattanDistance(capsulePosition, newPos) for capsulePosition in currentGameState.getCapsules()])
        score -= 0.5*capsuleDistance
    
    #ghost position
    ghostDistance = min([manhattanDistance(ghostPosition, newPos) for ghostPosition in currentGameState.getGhostPositions()])
    if ghostDistance < 2:
        score -= 40
    else:
        score += ghostDistance * 2
    
    #alphabeta
    score += 3*helperEvaluation(currentGameState, 0, 1,-(float("inf")),float("inf"))[0]
    
    return score
    #util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction

