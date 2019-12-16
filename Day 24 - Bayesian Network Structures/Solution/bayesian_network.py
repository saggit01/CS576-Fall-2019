import graph

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
                distribution over the variables possible values.
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
