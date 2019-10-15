def read_substitution_matrix(filename):
    """Reads a substitution matrix from a file.

    Args:
        filename: the name of the substitution matrix file
    Returns:
        A substitution matrix represented by a dictionary object indexed by
        character pair tuples. (e.g., ('S', 'A'))
    """
    matrix = dict()
    colnames = None
    with open(filename) as f:
        for line in f:
            if line.startswith("#"): 
                continue
            elif colnames is None: # first line
                colnames = line.split()
            else:
                row = line.split()
                rowname = row[0]
                for colname, value in zip(colnames, row[1:]):
                    matrix[(rowname, colname)] = int(value)
    return matrix
