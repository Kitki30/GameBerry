list_files_command = """
import os
def list_all_files(directory):
    for root, dirs, files in os.walk(directory):
        for name in files:
            print(os.path.join(root, name))
list_all_files('/')
"""