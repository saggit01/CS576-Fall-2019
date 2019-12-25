import math
import itertools

import graph
import random_sample

class BayesianNetwork(graph.AdjacencyListDirectedGraph, graph.VertexLabeledDirectedGraph):
    def __init__(self, random_variable_names):
        """Inits a BayesianNetwork
        
        The initial network will have a set of variables/vertices labeled by the given names
        but without any edges or CPDs.  set_cpd should be called for each variable to 
        specify the edges and CPDs of the network.
        """
        # Call the parent graph class constructor, giving it the number of vertices
        super().__init__(len(random_variable_names))
        
        # Set the labels of the vertices to the names of the variables
        for i, name in enumerate(random_variable_names): self.set_vertex_label(i, name)
        
        # The cpds member variable is a list of the conditional probability distributions
        # for the variables.  self.cpds[i] will be the CPD for the ith random variable.
        self.cpds = [None] * len(random_variable_names)
        
        # The possible_values member variable is a list of lists of the possible values
        # that each variable may take.  self.possible_values[i] will be a list of the 
        # possible values for the ith random variable.
        self.possible_values = [None] * len(random_variable_names)
    
    def set_cpd(self, name, parent_names, possible_values, cpd=None):
        """Sets the CPD for a random variable in the network.
        
        The CPDs for the parents of the named random variables should be set prior to this call.
        Args:
            name: the name (a string) of the random variable
            parent_names: a list of the names of the parents of the random variable 
            possible_values: a list of the values that this random variable may take on
            cpd: the CPD for the random variable.  The CPD should be a dictionary mapping
                tuples of parent variable values to conditional probability distributions
                over the possible values.  Each conditional probability distribution should 
                be a list of probabilities for a categorial distribution over the possible 
                values.  If the random variable has no parents, the CPD dictionary should have
                a single entry, with the key being the empty tuple and the value being the 
                distribution over the variables possible values.  If the cpd is None, then a 
                CPD with uniform distributions will be used by default.
        """
        # convert from variable names to vertex indices
        i = self.vertex_index(name)
        parent_indices = [self.vertex_index(name) for name in parent_names]
        
        # add edges to the graph
        for j in parent_indices:
            self.add_edge(j, i)

        # check that the CPDs for the parents have been set already
        # this is important because we need to know the possible values for the parents
        # in order to encode the CPD for this random variable
        assert None not in [self.possible_values[j] for j in parent_indices], "Parent CPDs need to be set first"
        
        # Set the possible values for this random variable
        self.possible_values[i] = possible_values[:]

        if cpd is None:
            self.cpds[i] = self._cpd_table(i)
        else:
            # Set the CPD for this random variable, converting it to use encoded parent values
            self.cpds[i] = {self.encode_values(parent_values, parent_indices): distribution[:]
                            for parent_values, distribution in cpd.items()}

    def encode_values(self, values, variable_indices=None):
        """Encodes variable values by their indices into the possible values lists.
        
        Args:
            values: a list of variable values
            variable_indices: a list of variable indices corresponding to the values list.  If this
                is None, it is assumed that values is a configuration of all variables in the network.
        Returns:
            A list of encoded variable values.
        """
        indices = variable_indices if variable_indices else range(len(values))
        return tuple(self.possible_values[i].index(value) for i, value in zip(indices, values))

    def decode_values(self, encoded_values):
        """Decodes variable values from indices (the inverse of encode_values).
        
        Args:
            encoded_values: a list of encoded variable values, one per variable in the network.
        Returns:
            A list of variable values.
        """
        return tuple(self.possible_values[i][encoded_values[i]] for i in range(len(encoded_values)))

    def log_probability(self, values):
        """Computes the log joint probability of a single configuration of values for the random variables.
        
        Args:
            values: a list of observed values for the random variables, one value per variable, with
                the ith entry giving the value for the ith random variable (vertex)
        """
        encoded_values = self.encode_values(values)
        log_prob = 0
        for i, value in enumerate(encoded_values):
            parent_values = tuple(encoded_values[j] for j in self.parents(i))
            log_prob += math.log(self.cpds[i][parent_values][value])
        return log_prob

    def sample(self):
        """Samples a single configuration of values for the random variables in the network.
        
        Returns:
            A list of sampled values for the random variables, one value per variable, with the
            the ith entry giving the value for the ith random variable (vertex).
        """
        values = [None] * self.num_vertices()
        for i in self.topological_order():
            parent_values = tuple(values[j] for j in self.parents(i))
            values[i] = random_sample.sample_categorical(self.cpds[i][parent_values])
        return self.decode_values(values)
   
    def probability(self, values):
        """Computes the joint probability of a single configuration of values for the random variables.
        
        Only to be used for small networks because of numerical issues.  For large networks, use 
        the log_probability method instead.
        Args:
            values: a list of observed values for the random variables, one value per variable, with
                the ith entry giving the value for the ith random variable (vertex)
        """
        encoded_values = self.encode_values(values)
        prob = 1
        for i, value in enumerate(encoded_values):
            parent_values = tuple(encoded_values[j] for j in self.parents(i))
            prob *= self.cpds[i][parent_values][value]
        return prob
    
    def joint_dist(self):
        """Returns the joint probability distribution represented by this network.
        
        This shoud only be used for very small networks, as the number of configurations
        in the joint distribution is exponential in the number of random variables
        
        Returns:
            The joint distribution, represented as a dictionary mapping tuples
            (configurations of the random variables) to probabilities.
        """
        return {config: self.probability(config) for config in itertools.product(*self.possible_values)}
    
    def sufficient_statistics(self, data):
        """Computes the sufficient statistics for each CPD given a set of data.
        
        The sufficient statistics for each parent configuration in a CPD are simply
        the counts of the number of times each possible value is observed in combination
        with that parent configuration.
        Args:
            data: a list of observations (tuples)
        """
        # initialize count tables, with entries starting at zero
        ss = [self._cpd_table(i, value=0) for i in range(self.num_vertices())]

        # add counts for each observation in the data
        for values in data:
            encoded_values = self.encode_values(values)
            for i, value in enumerate(encoded_values):
                parent_values = tuple(encoded_values[j] for j in self.parents(i))
                ss[i][parent_values][value] += 1

        return ss
    
    def estimate_parameters(self, data):
        """Estimates (and sets) the parameters of the model given the data using maximum likelihood.
        
        Args:
            data: a list of observations (tuples)
        """   
        ss = self.sufficient_statistics(data)
        self.cpds = list(map(max_likelihood_cpd, ss))
        
    def _cpd_table(self, i, value=None):
        """Returns a new CPD-like table for variable i.
        
        If value is None, then a uniform distribution is used for each entry in the table,
        otherwise a list of the same length as the distribution but with each entry set
        to value is used (e.g., a value of 0 can be used to initialize a count table).
        """
        parent_indices = self.parents(i)
        parent_possible_values = [self.possible_values[j] for j in parent_indices]
        k = len(self.possible_values[i])
        dist = uniform_dist(k) if value is None else [value] * k
        return {self.encode_values(parent_values, parent_indices): dist[:]
                for parent_values in itertools.product(*parent_possible_values)}

def max_likelihood_cpd(variable_ss):
    """Computes a CPD with maximum likelihood parameters given the CPD sufficient statistics.
    
    If the sufficient statistics (counts) for a particular parent configuration are all zero,
    then a uniform distribution is used for the maximum likelihood parameters.
    """
    return {config: normalize_vector(counts) if any(counts) else uniform_dist(len(counts))
            for config, counts in variable_ss.items()}

def normalize_vector(v):
    """Returns a new vector with entries scaled such that the sum of the entries is one."""
    s = sum(v)
    return [x / s for x in v]

def uniform_dist(k):
    """Returns a uniform distribution over k possible values."""
    return [1 / k] * k

def make_lac_operon_network():
    """Constructs and returns the example Lac operon Bayesian network."""
    
    random_variables = ["L", "I", "G", "C", "lacI-unbound", "CAP-bound", "Z"]
    network = BayesianNetwork(random_variables)

    network.set_cpd("L",
                    [], ["absent", "present"],
                    {(): [0.9, 0.1]})

    network.set_cpd("I",
                    [], ["absent", "present"],
                    {(): [0.1, 0.9]})

    network.set_cpd("G",
                    [], ["absent", "present"],
                    {(): [0.5, 0.5]})

    network.set_cpd("C",
                    [], ["absent", "present"],
                    {(): [0.1, 0.9]})

    network.set_cpd("lacI-unbound",
                    ["L", "I"], ["true", "false"],
                    {("absent",   "absent"): [0.9, 0.1],
                    ("absent",  "present"): [0.1, 0.9],
                    ("present",  "absent"): [0.9, 0.1],
                    ("present", "present"): [0.9, 0.1]})

    network.set_cpd("CAP-bound",
                    ["G", "C"], ["true", "false"],
                    {("absent",   "absent"): [0.1, 0.9],
                     ("absent",  "present"): [0.9, 0.1],
                     ("present",  "absent"): [0.1, 0.9],
                     ("present", "present"): [0.2, 0.8]})

    network.set_cpd("Z",
                    ["lacI-unbound", "CAP-bound"], ["absent", "low", "high"],
                    {("true",  "false"): [0.1, 0.8, 0.1],
                     ("true",   "true"): [0.1, 0.1, 0.8],
                     ("false", "false"): [0.8, 0.1, 0.1],
                     ("false",  "true"): [0.8, 0.1, 0.1]})
    
    return network

def make_empty_lac_operon_network():
    """Constructs and returns an empty (no edge) Lac operon Bayesian network."""
    
    random_variables = ["L", "I", "G", "C", "lacI-unbound", "CAP-bound", "Z"]
    network = BayesianNetwork(random_variables)

    network.set_cpd("L", [], ["absent", "present"])
    network.set_cpd("I", [], ["absent", "present"])
    network.set_cpd("G", [], ["absent", "present"])
    network.set_cpd("C", [], ["absent", "present"])
    network.set_cpd("lacI-unbound", [], ["true", "false"])
    network.set_cpd("CAP-bound", [], ["true", "false"])
    network.set_cpd("Z", [], ["absent", "low", "high"])
    
    return network

def make_flight_weather_network():
    """Constructs and returns the example flight/weather/airline Bayesian network."""
    
    variables = ["airline", "weather", "flight_status"]
    network = BayesianNetwork(variables)

    network.set_cpd("airline",
                    [], ["United", "Delta"],
                    {(): [0.7, 0.3]})
    network.set_cpd("weather",
                    [], ["sun", "rain", "snow"],
                    {(): [0.5, 0.3, 0.2]})
    network.set_cpd("flight_status",
                    ["airline", "weather"], ["on-time", "delayed"],
                    {("United", "sun"):  [0.8, 0.2],
                     ("United", "rain"): [0.5, 0.5],
                     ("United", "snow"): [0.1, 0.9],
                     ("Delta",  "sun"):  [0.9, 0.1],
                     ("Delta",  "rain"): [0.4, 0.6],
                     ("Delta",  "snow"): [0.2, 0.8]})
    return network
