import pandas as pd

def data_process_in(file_path):
    data = pd.read_csv(file_path)
    data = data.dropna(axis=1, how="all")
    print(data)
    
    desired_country_code = input("Enter the country code you want to analyze and get a report: ")
    
    row_data, input_code, code_exists, column_name = country_code(desired_country_code, data)
    
    if code_exists:
        print(f"The country code '{desired_country_code}' exists in the data.")
        print(f"It is located in the column '{column_name}'.")
        print(f"The data for this country is: {row_data}")
    else:
        print(f"The country code '{desired_country_code}' does not exist in the data.")
    return data

def country_code(cuncode, data):
    for column in data.columns:
        if cuncode in data[column].tolist():
            column_name = column
            code_exists = True
            break
    else:
        code_exists = False
        column_name = None
    
    if code_exists:
        row_data = data.loc[data[column_name] == cuncode].values.tolist()[0]
    else:
        row_data = None
    
    return row_data, cuncode, code_exists, column_name

processed_data = data_process_in(file_path="country_arrival_data.csv")
