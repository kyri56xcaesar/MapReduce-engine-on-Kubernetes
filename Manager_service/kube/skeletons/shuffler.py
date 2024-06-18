if __name__ == "__main__":
        
    
    import glob, json, argparse
    
    
    parser = argparse.ArgumentParser(description="Process input and output paths")
    parser.add_argument('-i', '--input', type=str, default="mapper.out", help='Input data file path')
    parser.add_argument('-o', '--output', type=str, default="shuffler.out", help='Output data file path')
    args = parser.parse_args()
        
    input_data_path = args.input
    output_data_path = args.output
    
    mapped_files = glob.glob(input_data_path)
    
    shuffled_data = {}
    
    for file_name in mapped_files:
        
        with open(file_name) as f:
                data = json.load(f)
                for key, value in data.items():
                    if key not in shuffled_data:
                        shuffled_data[key] = value
                    else:
                        shuffled_data[key].extend(value) 
            
    with open(output_data_path, 'w') as out:
        json.dump(shuffled_data, out, indent=1, ensure_ascii=False)
