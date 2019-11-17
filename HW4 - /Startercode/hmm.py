import math
import random
import functools

class HiddenMarkovModel:
    def __init__(self, states, chars, 
                 transition_prob_matrix=None, initial_probs=None, emission_prob_matrix=None):
        """Initializes a HiddenMarkovModel
        
        Models represented by this class do not explicitly represent a begin state and do
        not allow for an end state.
        
        Args:
            states: a list giving a the names (as strings) of the hidden states of the model
            chars: a string giving the set of characters possibly emitted by the
                states of the model
            transition_prob_matrix: a list of lists of probabilities representing a
                transition probability matrix. transition_prob_matrix[s][t] should equal 
                P(pi_i = t | pi_{i-1} = s). Row s is thus the conditional probability 
                distribution P(pi_i | pi_{i-1} = s). The indices in this matrix correspond 
                to the indices of the states in the states argument.  If None, then this
                model will need to be trained.
            initial_probs: a list of probabilities representing the initial state 
                probabilities. Entry s of this list is P(pi_1 = s), i.e., the probability that
                the first state in the chain is s.  The indices of this list correspond to the
                indices of the states in the states argument. If None, then this
                model will need to be trained.
            emission_prob_matrix: a list of lists of probabilities representing an emission
                probability matrix.  emission_prob_matrix[s][c] should equal 
                P(X_i = c | pi_i = s), i.e., the probability of state s emitting character c. 
                Row s is thus the conditional probability distribution P(X_i | pi_i = s).
                The row indices of this matrix correspond to the indices of the states in
                the states argument.  The column indices of the matrix correspond to the 
                indices of the characters in the chars argument. If None, then this
                model will need to be trained.
        
        """
        self.states = states
        self.chars = chars
        self.set_parameters(transition_prob_matrix, initial_probs, emission_prob_matrix)
    
    def set_parameters(self, transition_prob_matrix, initial_probs, emission_prob_matrix):
        """Sets the parameters of the model.
        
        Args:
            transition_prob_matrix: the transition matrix as defined in the constructor.
            initial_probs: the initial state probabilities as defined in the constructor.
            emission_prob_matrix: the emission matrix as defined in the constructor.
        """
        
        # set the parameters to copies of the matrices/vectors provided as input
        self.transition_prob_matrix = copy_matrix(transition_prob_matrix) if transition_prob_matrix else None
        self.initial_probs = copy_vector(initial_probs) if initial_probs else None
        self.emission_prob_matrix = copy_matrix(emission_prob_matrix) if emission_prob_matrix else None
        
        # Skip the pre-processing steps below if the parameters are not given
        if None in (transition_prob_matrix, initial_probs, emission_prob_matrix): return

        # precompute log parameters
        self._compute_log_parameters()
        
        # precompute the children and parents of each state based on the non-zero
        # entries in the transition probability matrix
        self.children = [[ell for ell in range(len(self.states)) if self.transition_prob_matrix[k][ell]]
                         for k in range(len(self.states))]
        self.parents = [[ell for ell in range(len(self.states)) if self.transition_prob_matrix[ell][k]]
                        for k in range(len(self.states))]

    def _compute_log_parameters(self):
        """Computes and stores log-transformations of the model parameters.
        
        This method should be run whenever the parameters of the model are updated."""
        self.log_transition_prob_matrix = log_transform_matrix(self.transition_prob_matrix)
        self.log_initial_probs = log_transform_vector(self.initial_probs)
        self.log_emission_prob_matrix = log_transform_matrix(self.emission_prob_matrix)
        
    def encode_states(self, state_sequence):
        """Encodes a list of state strings as a list of indices of the states."""
        return [self.states.index(state) for state in state_sequence]

    def decode_states(self, indices):
        """Decodes a list of state indices into a list of the state strings."""
        return [self.states[index] for index in indices]

    def encode_sequence(self, sequence):
        """Encodes a string of observed characters as a list of indices of the characters."""
        return [self.chars.index(char) for char in sequence]

    def decode_sequence(self, indices):
        """Decodes a sequence of observed character indices into a string of characters."""
        return "".join(self.chars[index] for index in indices)
      
    def simulate(self, length):
        """Simulates a sequence of hidden states and emitted characters of
        the given length from this HMM.
        
        Args:
            length: the length of the sequence to simulate
        Returns:
            A tuple of the form (hidden_state_list, char_string) where hidden_state_string is a
            list of state strings and char_string is a string of observed characters.
        """
        state_indices = [None] * length
        char_indices = [None] * length
        for i in range(length):
            state_probs = self.transition_prob_matrix[state_indices[i - 1]] if i > 0 else self.initial_probs
            state_indices[i] = sample_categorical(state_probs)
            char_indices[i] = sample_categorical(self.emission_prob_matrix[state_indices[i]])
            
        return (self.decode_states(state_indices), self.decode_sequence(char_indices))

    def log_joint_probability(self, hidden_state_string, char_string):
        """Calculates the (natural) log joint probability (log(P(hidden_states, observed_chars))) 
        of a path of hidden states and an observed sequence given this HMM"""
        state_indices = self.encode_states(hidden_state_string)
        char_indices = self.encode_sequence(char_string)

        log_p = 0.0
        last_state_index = None
        for state_index, char_index in zip(state_indices, char_indices):
            if last_state_index is None:
                log_p += self.log_initial_probs[state_index]
            else:
                log_p += self.log_transition_prob_matrix[last_state_index][state_index]
            log_p += self.log_emission_prob_matrix[state_index][char_index]
            last_state_index = state_index
        return log_p

    def posterior_decoding_path(self, char_string):
        p = self.posterior_matrix(char_string)
        state_indices = [max((prob, i) for i, prob in enumerate(col))[1] for col in zip(*p)]
        return self.decode_states(state_indices)
     
    def most_probable_path(self, char_string):
        """Computes a most probable path of hidden states for the observed sequence."""
        V = self.viterbi_matrix(char_string)
        return self.viterbi_traceback(V)

    def viterbi_matrix(self, char_string):
        """Computes and returns the (log-transformed) Viterbi dynamic programming matrix V for
        the given observed sequence."""

        char_indices = self.encode_sequence(char_string)
        
        # Initialize the viterbi dynamic programming matrix
        # the entry V[k][i] corresponds to the subproblem V_k(i+1)
        # where i is a 0-based index (e.g., V[k][0] corresponds to the subproblem
        # of the most probable path of the prefix of length = 1). We will not explicitly
        # represent the begin or end states.  As a result, we will not explicitly store the
        # initialization values described in the textbook and lecture.
        V = matrix(len(self.states), len(char_string))
        if not char_string: return V
        
        # initialization
        for ell in range(len(self.states)):
            V[ell][0] = (self.log_initial_probs[ell] + 
                         self.log_emission_prob_matrix[ell][char_indices[0]])

        # main fill stage
        for i in range(1, len(char_string)):
            for ell in range(len(self.states)):
                V[ell][i] = (self.log_emission_prob_matrix[ell][char_indices[i]] + 
                             max(V[k][i - 1] + self.log_transition_prob_matrix[k][ell]
                                 for k in self.parents[ell]))

        return V
    
    def viterbi_traceback(self, V):
        """Computes a most probable path given the (log) Viterbi dynamic programming matrix V.
        
        Uses a traceback procedure that does not require traceback pointers.  In the case of
        ties, this traceback prefers the state with the largest index.
        """
        
        L = len(V[0])
        if L == 0: return ""
        state_indices = [None] * L
        # determine the state at the last position in a most probable path
        max_prob, max_state = max((V[k][L - 1], k) for k in range(len(self.states)))
        state_indices[L - 1] = max_state
        # traceback from this last state by redoing the recurrence calculation at each step
        # the emission probabilities are not included in the calculations because they are
        # irrelevant for determining the maximizing state
        for i in range(L - 1, 0, -1):
            max_prob, max_state = max((V[k][i - 1] + 
                                       self.log_transition_prob_matrix[k][max_state], k)
                                      for k in self.parents[max_state])
            state_indices[i - 1] = max_state
        return self.decode_states(state_indices)

    def backward_matrix(self, char_string):
        """Computes and returns the (log-transformed) Backward dynamic programming matrix b for
        the given observed sequence."""

        char_indices = self.encode_sequence(char_string)
        
        # Initialize the backward dynamic programming matrix
        # the entry b[k][i] corresponds to the subproblem b_k(i+1)
        # where i is a 0-based index. We will not explicitly represent the begin or end states.
        # As a result, the initialization at last position sets the backward probability to 1 (0 in log space).
        b = matrix(len(self.states), len(char_string))
        if not char_string: return b
        
        # initialization
        for ell in range(len(self.states)):
            b[ell][len(char_string) - 1] = 0.0

        # main fill stage
        for i in range(len(char_string) - 2, -1, -1):
            for k in range(len(self.states)):
                b[k][i] = sum_log_probs(self.log_transition_prob_matrix[k][ell] +
                                        self.log_emission_prob_matrix[ell][char_indices[i + 1]] +
                                        b[ell][i + 1]
                                        for ell in self.children[k])
        return b
     
    def log_probability(self, char_string, forward=None):
        """Calculates the (natural) log probability (log(P(observed_chars))) 
        of an observed sequence given this HMM"""
        f = forward if forward is not None else self.forward_matrix(char_string)
        return sum_log_probs(f[k][-1] for k in range(len(self.states)))

def sample_categorical(distribution):
    """Randomly sample from a categorical distribution (a discrete distribution over K categories).
    
    Args:
        distribution: a list of probabilities representing a discrete distribution over K categories.
    Returns:
        The index of the category sampled.
    """
    r = random.random()
    for i, prob in enumerate(distribution):
        if r < prob:
            return i
        else:
            r -= prob
    # in case we encounter floating point issues return the last index
    return len(distribution) - 1    

def log_transform_vector(v):
    """Returns a new vector (a list) with log-transformed values"""
    return [math.log(x) if x != 0 else float("-inf") for x in v]

def log_transform_matrix(m):
    """Returns a new matrix (a list of lists) with log-transformed values"""
    return list(map(log_transform_vector, m))

def round_matrix(m, digits=2):
    """Returns a new matrix (a list of lists) with rounded values"""
    return [round_vector(v, digits) for v in m]
    
def round_vector(v, digits=2):
    """Returns a new vector (a list) with rounded values"""
    return [round(x, digits) for x in v]

def matrix(num_rows, num_cols, initial_value=None):
    """Constructs a matrix (a list of lists)"""
    return [[initial_value] * num_cols for i in range(num_rows)]

def normalize_vector(v):
    """Returns a new vector with entries scaled such that the sum of the entries is one."""
    s = sum(v)
    return [x / s for x in v]

def normalize_matrix_rows(m):
    """Returns new matrix with entries scaled such that each row sums to one."""
    return list(map(normalize_vector, m))

def add_to_vector(v, x):
    """Returns a new vector with x added to each entry."""
    return [x + y for y in v]

def add_to_matrix(m, x):
    """Returns a new matrix with x added to each entry."""
    return [add_to_vector(v, x) for v in m]

def copy_matrix(m):
    """Returns a deep copy of the given matrix."""
    return [copy_vector(row) for row in m]

def copy_vector(v):
    """Returns a copy of the given vector."""
    return v[:]

def random_prob_vector(length):
    """Randomly samples a probability distribution."""
    return normalize_vector([random.expovariate(1) for i in range(length)])

def random_prob_matrix(num_rows, num_cols):
    """Returns a matrix with each row being a randomly sampled probability distribution."""
    return [random_prob_vector(num_cols) for i in range(num_rows)]

def print_matrix(m, precision=3, width=10):
    """Prints a matrix with values formatted to the given precision and spaced to the given width."""
    for row in m:
        print(''.join("{:{}.{}g}".format(x, width, precision) for x in row))

NEGATIVE_INFINITY = float("-inf")

def sum_log_probs(log_probs):
    """Computes the sum of an iterable of probabilities in log space"""
    return functools.reduce(add_log_probs, log_probs)