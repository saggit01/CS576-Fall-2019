def read_sequences_from_fasta_file(filename):
    """Reads all sequence records from a FASTA-formatted file.

    Args:
        filename: the name of the FASTA-formatted file
    Returns:
        A list of records, where each record is represented by a tuple (name, sequence)
    """
    sequences = []
    current_lines = None
    with open(filename) as f:
        for line in f:
            if line.startswith(">"):
                if current_lines is not None:
                    sequences.append(sequence_from_fasta_lines(current_lines))
                current_lines = []
            current_lines.append(line.rstrip())
        
    # Handle the last record in the file
    if current_lines is not None:
        sequences.append(sequence_from_fasta_lines(current_lines))
    return sequences

def write_sequences_to_fasta_file(sequences, filename, wrap_width=70):
    """Writes a list of sequence records to a file in FASTA format.

    Args:
        sequences: A list of records, where each record represented by a tuple (name, sequence)
        filename: the name of the file to which to write the sequences.
    """
    with open(filename, 'w') as f:
        for name, sequence in sequences:
            print(">" + name, file=f)
            print(wrap_sequence(sequence, wrap_width), file=f)

def sequence_from_fasta_lines(lines):
    """Constructs a sequence record from a list of FASTA-formatted lines
    
    Args:
        lines: a list of FASTA-formatted lines representing one sequence record
    Returns:
        A sequence record, which is represented by a tuple (name, sequence)
    """
    # Strip the beginning '>'
    name = lines[0][1:]
    # Concatenate the sequence lines
    sequence = ''.join(lines[1:])
    return (name, sequence)

def wrap_sequence(s, width):
    """Wraps a string to multiple lines with a given maximum line length.
    
    Args:
        s: a string
        width: the maximum line length
    Returns:
        A string equivalent to s but wrapped such that lines are no longer than width
    """
    
    return "\n".join(s[start: start + width] for start in range(0, len(s), width))

