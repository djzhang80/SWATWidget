def get_lines_with_pattern(filename):
  with open(filename, 'r', encoding='UTF-8') as file:
    lines = file.readlines()  # Read all lines into a list
    result=[]
    for line in lines:
        if(line.startswith("﻿//  .") or line.startswith("//  .") or line.startswith("// .")):
            result.append(line.strip().split(".")[1])
    return result

def get_lines_between_markers(filename,subfix):
  with open(filename, 'r',encoding="utf-8") as file:
    lines = file.readlines()  # Read all lines into a list
  start_marker = "//  ."+subfix
  end_marker = "//  ."
  is_between_markers = False  # Flag to track if we're between markers
  extracted_lines = []
  for line in lines:
    if line.startswith("﻿//  ."+subfix) or line.startswith("//  ."+subfix) or line.startswith("// ."+subfix):
      is_between_markers = True
    elif line.startswith("﻿//  .") or line.startswith("//  .") or line.startswith("// .") or line.startswith("//"):
      is_between_markers = False
    elif is_between_markers:
        if line.strip()!="":
            extracted_lines.append((line.strip().split()[0],tuple(line.strip().split()[1:3])))  # Extract and strip lines between markers
  return extracted_lines



filetypes=get_lines_with_pattern("./model/Absolute_Swat_Values.txt")
print(filetypes)

parameters_group_by_type={}
for filetype in filetypes:
    parameters = get_lines_between_markers("./model/Absolute_Swat_Values.txt",filetype)
    parameters_group_by_type[filetype]=parameters
    
    
print(parameters_group_by_type)