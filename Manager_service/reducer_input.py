# Example user input

def reducer(entries):

    accumulator = dict()
    
    for key, value in entries.items():
        if key in accumulator:
            accumulator[key] += sum(value)
        else:
            accumulator[key] = sum(value)
    
    return accumulator