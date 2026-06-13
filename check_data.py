def check_data(data,required):
    if data is None:
        return False
    for field, ftype in required:
        if field not in data.keys():
            return False
        if not isinstance(data[field], ftype):
            return False
    return True
def check_data_nl(data,required):
    x = 0
    if data is None:
        return False
    for field, ftype in required:
        if field not in data.keys():
            x += 1
        if isinstance(data[field], ftype):
            return False
    if x == len(required):
        return False
    return True
