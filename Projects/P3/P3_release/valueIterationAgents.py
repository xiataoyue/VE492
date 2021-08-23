import mdp, util

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        "*** YOUR CODE HERE ***"
        for rnd in range(self.iterations):
            values = self.values.copy()
            for state in self.mdp.getStates():
                if self.mdp.isTerminal(state):
                    continue
                actions = self.mdp.getPossibleActions(state)
                valueList = []
                for action in actions:
                    valueList.append(self.getQValue(state, action))
                values[state] = max(valueList)
            self.values = values


    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        QValue = 0
        for nextState, p in self.mdp.getTransitionStatesAndProbs(state, action):
            QValue += (self.mdp.getReward(state, action, nextState) + self.discount * self.values[nextState]) * p
        return QValue
        util.raiseNotDefined()

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"
        if self.mdp.isTerminal(state):
            return None
        actions = self.mdp.getPossibleActions(state)
        QValues = [self.getQValue(state, action) for action in actions]
        maxValue = max(QValues)
        index = QValues.index(maxValue)
        return actions[index]
        util.raiseNotDefined()

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        for i in range(self.iterations):
            states = self.mdp.getStates()
            state = states[i % len(states)]
            if self.mdp.isTerminal(state):
                continue
            actions = self.mdp.getPossibleActions(state)
            values = []
            for action in actions:
                values.append(self.getQValue(state, action))
            self.values[state] = max(values)


class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        predecessors = dict()
        for state in self.mdp.getStates():
            if self.mdp.isTerminal(state):
                continue
            actions = self.mdp.getPossibleActions(state)
            for action in actions:
                for nextState, p in self.mdp.getTransitionStatesAndProbs(state, action):
                    if nextState not in predecessors.keys():
                        predecessors[nextState] = set()
                    if p:
                        predecessors[nextState].add(state)

        pq = util.PriorityQueue()
        for state in self.mdp.getStates():
            if self.mdp.isTerminal(state):
                continue
            actions = self.mdp.getPossibleActions(state)
            valueList = []
            for action in actions:
                valueList.append(self.getQValue(state, action))
            QValue = max(valueList)
            diff = abs(self.values[state] - QValue)
            pq.push(state, -diff)

        for rnd in range(self.iterations):
            if pq.isEmpty():
                break
            newState = pq.pop()
            if self.mdp.isTerminal(newState):
                continue
            actions = self.mdp.getPossibleActions(newState)
            qValue = -float("inf")
            for action in actions:
                if self.getQValue(newState, action) > qValue:
                    qValue = self.getQValue(newState, action)
            self.values[newState] = qValue

            for pred in predecessors[newState]:
                if self.mdp.isTerminal(pred):
                    continue
                actions = self.mdp.getPossibleActions(pred)
                pQValue = -float("inf")
                for action in actions:
                    if self.getQValue(pred, action) > pQValue:
                        pQValue = self.getQValue(pred, action)

                diff = abs(self.values[pred] - pQValue)
                if diff > self.theta:
                    pq.update(pred, -diff)



