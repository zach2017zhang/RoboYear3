# search.py
# ---------
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


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]

def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print "Start:", problem.getStartState()
    print "Is the start a goal?", problem.isGoalState(problem.getStartState())
    print "Start's successors:", problem.getSuccessors(problem.getStartState())
    """
    "*** YOUR CODE HERE ***"
    Open = util.Stack()
    #end_state,previous_states,path,cost
    Open.push((problem.getStartState(),[problem.getStartState()],[]))
    while not Open.isEmpty():
        state = Open.pop()
        if problem.isGoalState(state[0]):
            return state[2]
        for succ in problem.getSuccessors(state[0]):
            if succ[0] not in state[1]:
                Open.push((succ[0],state[1]+[succ[0]],state[2]+[succ[1]]))
    return []
    #util.raiseNotDefined()

def breadthFirstSearch(problem):
    """Search the shallowest nodes in the search tree first."""
    "*** YOUR CODE HERE ***"
    Open = util.Queue()
    #end_state,previous_states,path,cost
    Open.push((problem.getStartState(),[problem.getStartState()],[]))
    Close = []
    Discovered = [problem.getStartState()]
    while not Open.isEmpty():
        state = Open.pop()
        if problem.isGoalState(state[0]):
            return state[2]
        for succ in problem.getSuccessors(state[0]):
            if succ[0] not in Close:
                if succ[0] not in Discovered:
                    Open.push((succ[0],state[1]+[succ[0]],state[2]+[succ[1]]))
                    Discovered += [succ[0]]
        Close += [state[0]]
    return []
    #util.raiseNotDefined()

def uniformCostSearch(problem):
    """Search the node of least total cost first."""
    "*** YOUR CODE HERE ***"
    Open = util.PriorityQueue()
    Close = []
    Discovered = {problem.getStartState():[]}
    Open.push(problem.getStartState(),problem.getCostOfActions(Discovered[problem.getStartState()]))
    while not Open.isEmpty():
        state = Open.pop()
        if problem.isGoalState(state):
            return Discovered[state]
        for succ in problem.getSuccessors(state):
            if succ[0] not in Close:
                #update priority
                if succ[0] in Discovered.keys():
                    if problem.getCostOfActions(Discovered[succ[0]])>problem.getCostOfActions(Discovered[state]+[succ[1]]):
                        Discovered[succ[0]]=Discovered[state]+[succ[1]]
                        Open.update(succ[0],problem.getCostOfActions(Discovered[succ[0]]))
                else:
                    Discovered[succ[0]]=Discovered[state]+[succ[1]]
                    Open.push(succ[0],problem.getCostOfActions(Discovered[succ[0]])) 
        Close += [state]
    return []

    #util.raiseNotDefined()

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def aStarSearch(problem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    "*** YOUR CODE HERE ***"
    Open = util.PriorityQueue()
    Close = []
    Discovered = {problem.getStartState():[]}
    Open.push(problem.getStartState(),heuristic(problem.getStartState(),problem)+problem.getCostOfActions(Discovered[problem.getStartState()]))
    while not Open.isEmpty():
        state = Open.pop()
        if problem.isGoalState(state):
            return Discovered[state]
        for succ in problem.getSuccessors(state):
            if succ[0] not in Close:
                #update priority
                if succ[0] in Discovered.keys():
                    Curcost = heuristic(succ[0],problem)+problem.getCostOfActions(Discovered[state]+[succ[1]])
                    if heuristic(succ[0],problem)+problem.getCostOfActions(Discovered[succ[0]])>Curcost:
                        Discovered[succ[0]]=Discovered[state]+[succ[1]]
                        Open.update(succ[0],heuristic(succ[0],problem)+problem.getCostOfActions(Discovered[succ[0]]))
                else:
                    Discovered[succ[0]]=Discovered[state]+[succ[1]]
                    Open.push(succ[0],heuristic(succ[0],problem)+problem.getCostOfActions(Discovered[succ[0]])) 
        Close += [state]
    return []
    #util.raiseNotDefined()


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
