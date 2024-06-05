def reducer(entries):
    
    accumulator = dict()
    
    for d in entries:
        for key, value in d.items():
            if key in accumulator:
                accumulator[key] += value
            else:
                accumulator[key] = value
    
    return accumulator
    
