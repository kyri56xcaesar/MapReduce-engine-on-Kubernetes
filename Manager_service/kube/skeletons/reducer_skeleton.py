
if __name__ == "__main__":
    
    from json import loads, dump
    from argparse import ArgumentParser
    from reducer_input import reducer 

    parser = ArgumentParser(description="Process input and output paths")
    parser.add_argument('-i', '--input', type=str, default="shuffler.out", help='Input data file path')
    parser.add_argument('-o', '--output', type=str, default="reducer.out", help='Output data file path')
    args = parser.parse_args()
    
    input_data_path = args.input
    output_data_path = args.output
    
    with open(input_data_path, 'r') as f:
        file_content = f.read()
    
        data = loads(file_content)
    
        res = reducer(data)
        
        with open(output_data_path, 'w') as f:
            dump(res, f, indent=4)