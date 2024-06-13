def reducer(entries):

    accumulator = dict()
    
    for key, value in entries.items():
        if key in accumulator:
            accumulator[key] += sum(value)
        else:
            accumulator[key] = sum(value)
    
    return accumulator




if __name__ == "__main__":
    
    import json
        
    input_data_path = "test.out"
    output_data_path = "out.out"
    
    with open(input_data_path, 'r') as f:
        file_content = f.read()
    
        data = json.loads(file_content)
    
        res = reducer(data)
        
        with open(output_data_path, 'w') as f:
            json.dump(res, f, indent=4)