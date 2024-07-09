import pandas as pd
import os
from SWATUtil import SWATUtil
import warnings
warnings.filterwarnings("ignore")
def get_choro_data(variable:str,step:str,simulation:str):
    file_path = './model/'
    file_path=file_path+simulation+".output.sub"
    df=process_sub_file(file_path)
    #print(df)
    df=df.xs(step, level="MON")[variable]
    basinids = df.index.get_level_values("SUB")
    values=df.values
    return dict(zip(basinids,values))

def process_rch_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # The 9th line is the header
    header_line = lines[8][25:].replace("\n","")

    # Function to split the header line based on the defined column widths
    def split_by_length(line, chunk_size):
    # Using list comprehension to split the line into chunks of 'chunk_size'
        return [str(line[i:i + chunk_size]).strip() for i in range(0, len(line), chunk_size)]
    headers=split_by_length(header_line,12)
    headers.insert(0, "reach")
    headers.insert(1, "RCH")   
    headers.insert(2, "GIS")   
    headers.insert(3, "MON")   
    #print(headers)

    # Data starts from the 10th line
    data_lines = lines[9:]
    
    # Split each data line by spaces and handle joined column captions
    data = []
    for line in data_lines:
        split_line = line.split()
        data.append(split_line)
    
    # Create DataFrame
    df = pd.DataFrame(data, columns=headers)
    
    # Convert columns to appropriate data types if necessary
    # Assuming numerical data, convert them to floats/integers
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='ignore')
    
    
    # Set the indices
    df.set_index([df.columns[1], df.columns[3]], inplace=True)
    #df.drop(columns=['reach','GIS','AREAkm2'])
    return df


def process_sub_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # The 9th line is the header
    header_line = lines[8][24:].replace("\n","")

    # Function to split the header line based on the defined column widths
    def split_by_length(line, chunk_size):
    # Using list comprehension to split the line into chunks of 'chunk_size'
        return [str(line[i:i + chunk_size]).strip() for i in range(0, len(line), chunk_size)]
    headers=split_by_length(header_line,10)
    headers.insert(0, "subbasin")
    headers.insert(1, "SUB")   
    headers.insert(2, "GIS")   
    headers.insert(3, "MON")   
    #print(headers)

    # Data starts from the 10th line
    data_lines = lines[9:]
    
    # Split each data line by spaces and handle joined column captions
    data = []
    for line in data_lines:
        first_part = line[:24].split()
        second_part = line[24:].split()
        record=first_part+second_part
        data.append(record)
    # Create DataFrame
    df = pd.DataFrame(data, columns=headers)
    
    # Convert columns to appropriate data types if necessary
    # Assuming numerical data, convert them to floats/integers
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='ignore')
    
    
    # Set the indices
    df.set_index([df.columns[1], df.columns[3]], inplace=True)
    #df.drop(columns=['reach','GIS','AREAkm2'])
    return df


    
    #df=df.loc[(:,step),variable]
    
    
    

def collect_simulations(directory_path):
    """
    Reads a directory and adds all filenames ending with ".output.rch" to a set.

    Parameters:
        directory_path (str): The path of the directory to read.

    Returns:
        set: A set containing filenames ending with ".output.rch".
    """
    output_rch_files = set()

    # Walk through the directory
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".output.rch"):
                output_rch_files.add(file.split(".")[0])

    return output_rch_files

def generate_makerstrs():
    list1=['b','g','r','c','m','y','k']
    list2=[':','-.','--','-']
    combined_list = [element1 + element2 for element1 in list1 for element2 in list2]
    return combined_list


def get_timeseries(file_path):
    swatUtil= SWATUtil()
    startday=swatUtil.getStartDate(file_path)
    numdays=swatUtil.getDays(file_path)
    x = pd.date_range(start=startday, periods=numdays)
    return x.to_numpy()



