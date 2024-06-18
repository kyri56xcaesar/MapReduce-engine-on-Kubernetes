if __name__ == "__main__":


    import glob, json, os

    path = "/*.out"
    mapped_files = glob.glob(path)


    shuffled_data = {}

    for file_name in mapped_files:

        with open(file_name) as f:
                data = json.load(f)
                for key, value in data.items():
                    if key not in shuffled_data:
                        shuffled_data[key] = value
                    else:
                        shuffled_data[key].extend(value) 
            
    with open("shuffler.out", 'w') as out:
        json.dump(shuffled_data, out, indent=1, ensure_ascii=False)

