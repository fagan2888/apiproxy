from sexpdata import car,cdr
def dictalise(sexp):
    """ Turn a deserialised s-expression into a python dict
    """
    retval = {}
    for entry in cdr(sexp):
        if len(cdr(entry)) > 1:
           retval[car(entry).value()] = cdr(entry)
        else:
           retval[car(entry).value()] = car(cdr(entry))
    return retval
