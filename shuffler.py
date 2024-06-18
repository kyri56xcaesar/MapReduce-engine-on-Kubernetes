import glob
import json
import os

if __name__ == "__main__":


    path = os.path.join(os.getcwd(), "mapper-*.out")

    mapped_files = glob.glob(path)

    shuffled_data = {}

    for file_path in mapped_files:
        file_name = os.path.basename(file_path)
        print(file_name)
        
        with open(file_path) as f:
            data = json.load(f)
            for key, value in data.items():
                if key not in shuffled_data:
                    shuffled_data[key] = value
                else:
                    shuffled_data[key].extend(value)

    print(shuffled_data)

    # Optionally write the shuffled data to an output file
    # with open("shuffler.out", 'w') as out:
    #     json.dump(shuffled_data, out, indent=1, ensure_ascii=False)
