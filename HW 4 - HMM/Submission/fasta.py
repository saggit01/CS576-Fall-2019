def read_sequences_from_fasta_stream(stream):
    """Reads all sequence records from the FASTA-formatted file specified by filename
    and returns a list of records.  Each record is represented by a tuple (name, sequence)"""
    sequences = []
    current_record_lines = None
    for line in stream:
        if line.startswith(">"):
            if current_record_lines is not None:
                sequences.append(sequence_from_fasta_lines(current_record_lines))
            current_record_lines = []
        current_record_lines.append(line.rstrip())
        
    # Handle the last record in the file
    if current_record_lines is not None:
        sequences.append(sequence_from_fasta_lines(current_record_lines))
    return sequences

def read_sequences_from_fasta_file(filename):
    """Reads all sequence records from the FASTA-formatted file specified by filename
    and returns a list of records.  Each record is represented by a tuple (name, sequence)"""
    with open(filename) as f:
        return read_sequences_from_fasta_stream(f)

def sequence_from_fasta_lines(lines):
    # Strip the beginning '>'
    name = lines[0][1:]
    sequence = ''.join(lines[1:])
    return (name, sequence)

def wrap_sequence(s, width):
    return "\n".join(s[start: start + width] for start in range(0, len(s), width))

def write_sequences_to_fasta_file(sequences, filename, wrap_width=70):
    """Writes all sequence records in the list sequences
    to the file specified by filename in FASTA format.
    Each record should be represented by a tuple (name, sequence)"""
    with open(filename, 'w') as f:
        for name, sequence in sequences:
            print(">" + name, file=f)
            print(wrap_sequence(sequence, wrap_width), file=f)