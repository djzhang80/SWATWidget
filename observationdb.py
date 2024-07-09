import pandas as pd
import os

def read_csv_files_to_multilevel_df(directory):
    # Initialize an empty list to store DataFrames
    data_frames = []
    
    # Iterate over each file in the directory
    for file_name in os.listdir(directory):
        if file_name.endswith('.csv'):
            # Construct the full file path
            file_path = os.path.join(directory, file_name)
            
            # Read the CSV file, assuming each file can be treated as having multiple sheets
            file_df = pd.read_csv(file_path)
            print(file_df)
            
            # Iterate over each sheet in the file
            for sheet_name, sheet_df in file_df.items():
                # Set the multi-level index
                multi_index = pd.MultiIndex.from_product([[file_name], [sheet_name], sheet_df.columns])
                
                # Create a new DataFrame with the multi-level index
                indexed_df = pd.DataFrame(sheet_df.values, columns=multi_index)
                
                # Append the DataFrame to the list
                data_frames.append(indexed_df)
    
    # Concatenate all DataFrames into a single DataFrame
    combined_df = pd.concat(data_frames, axis=1)
    
    return combined_df

def read_all_xls_to_dict(directory):
    data = {}
    for filename in os.listdir(directory):
        if filename.endswith(".xls"):
            filepath = os.path.join(directory, filename)
            # Read each sheet of the XLS file
            xls_data = pd.read_excel(filepath, sheet_name=None, header=0)
            # Create a dictionary with sheet names as keys and DataFrames as values
            #sheet_data = {sheet_name: sheet for sheet_name, sheet in xls_data.items()}
            data[filename] = xls_data
    return data

data_dir = "observation"  # Replace with your directory path
observations = read_all_xls_to_dict(data_dir)

permap={ 
        "Nash-Sutcliffe Efficiency":"NSE",
        "Original Kling-Gupta Efficiency":"KGE",
        "Modified Kling-Gupta Efficiency":"kgeprime",
        "Non-Parametric Kling-Gupta Efficiency": "kgenp",
        "Root Mean Square Error":"RMSE",
        "Mean Absolute Relative Error":"MARE",
        "Percent Bias":"pbias",
        "Coefficient of Determination":"R2"
        }

if __name__ == "__main__":
    data_dir = "observation"  # Replace with your directory path
    da = read_all_xls_to_dict(data_dir)
    print(da)