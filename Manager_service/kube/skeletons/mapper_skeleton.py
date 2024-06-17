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
    from mapper_input import mapper

    parser = argparse.ArgumentParser(description="Process input and output paths")
    parser.add_argument('-i', '--input', type=str, default="word_count_data.txt", help='Input data file path')
    parser.add_argument('-o', '--output', type=str, default="mapper.out", help='Output data file path')
    args = parser.parse_args()
    
    # Should be changed
    input_data_path = args.input
    output_data_path = args.output

    with open(input_data_path, 'r') as inp:
        lines = inp.readlines()
        mapped_lines = []

        
        for j, line in enumerate(lines):
            line = line.strip()
            res = mapper(line.split(" "))
            mapped_lines.append(res)
            
        # flatten data inside and shuffler them 
        shuffled_data = shuffler([item for sublist in mapped_lines for item in sublist])

        with open(output_data_path, 'w') as out:
            json.dump(shuffled_data, out, indent=4, ensure_ascii=False)

        
