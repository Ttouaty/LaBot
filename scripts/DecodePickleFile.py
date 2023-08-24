import pickle
import pprint
import os
import sys
from pathlib import Path
sys.path.append(Path(__file__).absolute().parents[1].as_posix())

import labot

def ConvertLogsToTxt():
    pathToLogs = Path(__file__).absolute().parents[1] / "LOGS"
    finalFolder = pathToLogs / "Decoded";
    if not os.path.exists(finalFolder):
        os.makedirs(finalFolder)

    for filename in os.listdir(pathToLogs):
        input_path = os.path.join(pathToLogs, filename)
        if not os.path.isfile(input_path):
            continue
        try:
            with open(input_path, 'rb') as f:
                data = []
                while True:
                    try:
                        data.append(pickle.load(f))
                    except EOFError:
                        break
            output_path = os.path.join(finalFolder, f"{filename[:filename.rfind('.')]} - decoded.txt")
            print(output_path)
            with open(output_path, "w") as f:
                f.write(str("\n".join([str(item) for item in data])))
            print(f"Converted {filename} to {output_path}")
        except (pickle.UnpicklingError, EOFError):
            print(f"Skipped {filename} - not a pickle file")

    


ConvertLogsToTxt();


# try:
#     with open(input_path, 'rb') as f:
#         data = pickle.load(f)

#     output_path = os.path.join(output_folder, f"{filename}.txt")

#     with open(output_path, 'w') as f:
#         f.write(str(data))  # Convert data to string and write to text file

#     print(f"Converted {filename} to {output_path}")

# except (pickle.UnpicklingError, EOFError):
#     print(f"Skipped {filename} - not a pickle file")
#     print(f"Skipped {filename} - not a pickle file")