def align_global_affine_hp_gaps(x, y, submatrix, g, h, s, t,
                                traceback_pref = {'M': 3,
                                                  'IX': 5,
                                                  'HX': 4,
                                                  'IY': 2,
                                                  'HY': 1}):
    m, ix, iy, hx, hy = compute_matrices_global_affine_hp_gaps(x, y, submatrix, g, h, s, t)
    score, alignment = traceback_global_affine_hp_gaps(x, y, submatrix, g, h, s, t,
                                                       m, ix, iy, hx, hy, traceback_pref)
    return score, alignment

def compute_matrices_global_affine_hp_gaps(x, y, submatrix, g, h, s, t):
    nrows = len(x) + 1
    ncols = len(y) + 1
    m = matrix(nrows, ncols, NEGATIVE_INFINITY)
    ix = matrix(nrows, ncols, NEGATIVE_INFINITY)
    iy = matrix(nrows, ncols, NEGATIVE_INFINITY)
    hx = matrix(nrows, ncols, NEGATIVE_INFINITY)
    hy = matrix(nrows, ncols, NEGATIVE_INFINITY)
    
    # initialization
    m[0][0] = 0
    for i in range(nrows):
        ix[i][0] = g + s * i
    for j in range(ncols):
        iy[0][j] = g + s * j
    
    # fill
    for i in range(1, nrows):
        for j in range(1, ncols):
            m[i][j] =  max( m[i - 1][j - 1], 
                           ix[i - 1][j - 1], 
                           iy[i - 1][j - 1],
                           hx[i - 1][j - 1], 
                           hy[i - 1][j - 1]) + submatrix[x[i - 1], y[j - 1]]                      
            ix[i][j] = max( m[i - 1][j] + g,
                           ix[i - 1][j]) + s
            iy[i][j] = max( m[i][j - 1] + g,
                           iy[i][j - 1]) + s
            if i > 1 and x[i - 1] == x[i - 2]:
                hx[i][j] = max( m[i - 1][j] + h,
                               hx[i - 1][j]) + t     
            if j > 1 and y[j - 1] == y[j - 2]:
                hy[i][j] = max( m[i][j - 1] + h,
                               hy[i][j - 1]) + t

    return m, ix, iy, hx, hy

def traceback_global_affine_hp_gaps(x, y, submatrix, g, h, s, t,
                                    m, ix, iy, hx, hy, traceback_pref):
    M, IX, IY, HX, HY = [traceback_pref[name] for name in ["M", "IX", "IY", "HX", "HY"]]
    i, j = len(x), len(y)
    total_score, state = max((m[i][j], M),
                             (ix[i][j], IX),
                             (iy[i][j], IY),
                             (hx[i][j], HX),
                             (hy[i][j], HY))
    columns = [('', '')] # start with one empty column to handle alignment of empty strings
    while i > 0 or j > 0:
        if state == M:
            columns.append((x[i - 1], y[j - 1]))
            score, state = max((m[i - 1][j - 1], M),
                               (ix[i - 1][j - 1], IX),
                               (iy[i - 1][j - 1], IY),
                               (hx[i - 1][j - 1], HX),
                               (hy[i - 1][j - 1], HY))
            i -= 1
            j -= 1
        elif state == IX:
            columns.append((x[i - 1], '-'))
            score, state = max((m[i - 1][j] + g, M),
                               (ix[i - 1][j], IX))
            i -= 1
        elif state == IY:
            columns.append(('-', y[j - 1]))
            score, state = max((m[i][j - 1] + g, M),
                               (iy[i][j - 1], IY))
            j -= 1
        elif state == HX:
            columns.append((x[i - 1], '-'))
            score, state = max((m[i - 1][j] + h, M),
                               (hx[i - 1][j], HX))
            i -= 1
        elif state == HY:
            columns.append(('-', y[j - 1]))
            score, state = max((m[i][j - 1] + h, M),
                               (hy[i][j - 1], HY))
            j -= 1
        else:
            assert False
    
    rows = zip(*reversed(columns))
    alignment = [''.join(row) for row in rows]
    return total_score, alignment

def matrix(nrows, ncols, init_value=None):
    return [[init_value] * ncols for i in range(nrows)]

def print_matrix(m, width=5):
    def print_row(fields):
        print("".join(["{:>{width}}".format(field, width=width) for field in fields]))
    for row in m:
        print_row(row)
    
NEGATIVE_INFINITY = float("-inf")