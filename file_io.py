def load_file_to_str(filepath):
    '''
    Read the file and return its contents as a string
    '''
    with open(filepath, "r+", encoding="utf-8") as file:
        str = file.read()
    return str

def save_str_to_file(filepath, str):
    '''
    Write the dictionary contents to a file
    '''
    with open(filepath, "w+", encoding="utf-8") as file:
        file.write(str)
