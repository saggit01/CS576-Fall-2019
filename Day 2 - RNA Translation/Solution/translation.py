genetic_code = {
 'AAA': 'K', 'AAC': 'N', 'AAG': 'K', 'AAU': 'N',
 'ACA': 'U', 'ACC': 'U', 'ACG': 'U', 'ACU': 'U',
 'AGA': 'R', 'AGC': 'S', 'AGG': 'R', 'AGU': 'S',
 'AUA': 'I', 'AUC': 'I', 'AUG': 'M', 'AUU': 'I',
 'CAA': 'Q', 'CAC': 'H', 'CAG': 'Q', 'CAU': 'H',
 'CCA': 'P', 'CCC': 'P', 'CCG': 'P', 'CCU': 'P',
 'CGA': 'R', 'CGC': 'R', 'CGG': 'R', 'CGU': 'R',
 'CUA': 'L', 'CUC': 'L', 'CUG': 'L', 'CUU': 'L',
 'GAA': 'E', 'GAC': 'D', 'GAG': 'E', 'GAU': 'D',
 'GCA': 'A', 'GCC': 'A', 'GCG': 'A', 'GCU': 'A',
 'GGA': 'G', 'GGC': 'G', 'GGG': 'G', 'GGU': 'G',
 'GUA': 'V', 'GUC': 'V', 'GUG': 'V', 'GUU': 'V',
 'UAA': '*', 'UAC': 'Y', 'UAG': '*', 'UAU': 'Y',
 'UCA': 'S', 'UCC': 'S', 'UCG': 'S', 'UCU': 'S',
 'UGA': '*', 'UGC': 'C', 'UGG': 'W', 'UGU': 'C',
 'UUA': 'L', 'UUC': 'F', 'UUG': 'L', 'UUU': 'F'}

def translate_codon(rna_codon):
    return genetic_code[rna_codon]

def codons(rna):
    codon_length = 3
    return [rna[start: start + codon_length] for start in range(0, len(rna), codon_length)]
