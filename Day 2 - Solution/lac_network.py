def lacI_bound(lactose, lacI):
    return not lactose and lacI

def CAP_bound(glucose, CAP):
    return not glucose and CAP

def lacZ(is_lacI_bound, is_CAP_bound):
    if is_lacI_bound:
        return "absent"
    elif is_CAP_bound:
        return "high"
    else:
        return "low"

def lacZ_full_circuit(lactose, lacI, glucose, CAP):
    return lacZ(lacI_bound(lactose, lacI), CAP_bound(glucose, CAP))
