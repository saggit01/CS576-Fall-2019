def lacI_bound(lactose, lacI):
    return not lactose and lacI

def CAP_bound(glucose, CAP):
    return not glucose and CAP

def lacZ(is_lacI_bound, is_CAP_bound):
    if not is_lacI_bound and not is_CAP_bound:
        return "low"
    if not is_lacI_bound and is_CAP_bound:
        return "high"
    
    return "absent"

def lacZ_full_circuit(lactose, lacI, glucose, CAP):
    is_lacI_bound = lacI_bound(lactose, lacI)
    is_CAP_bound = CAP_bound(glucose, CAP)
    return lacZ(is_lacI_bound, is_CAP_bound)