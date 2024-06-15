# Shuffler get an input list of tuples with key value pairs
# it should return a dict for each unique key with value a list of all the values it had

def shuffler(arr):
    
    shuffled = dict()
    
    for element in arr:
        
        if element[0] not in shuffled:
            shuffled[element[0]] = [element[1]]
        else:
            shuffled[element[0]].append(element[1])
    
    return shuffled            


if __name__ == "__main__":
    
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Process input and output paths")
    parser.add_argument('-i', '--input', type=str, default='mapper.out', help='Input data file path')
    parser.add_argument('-o', '--output', type=str, default='shuffler.out', help='Output data file path')
    args = parser.parse_args()
    
    input_data_path = args.input
    output_data_path = args.output
    
    with open(input_data_path, 'r') as inp:
        lines = inp.readlines()
        
        input_data = []
        for line in lines:
            line = line.strip()
    
            if line.startswith("("):
                line = line.lstrip("(")
                key, value = line.split(", ")
                input_data.append((key.split('"')[1], int(value.split(")")[0])))
                


        shuffled_data = shuffler(input_data)

        with open(output_data_path, 'w') as out:
            json.dump(shuffled_data, out, indent=4, ensure_ascii=False)
