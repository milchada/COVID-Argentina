def force_array(x):
    try:
        len(x)
    except TypeError:
        x = [x]
    return x
