#challenge.py

import difflib

class Challenge:
    """
    hello
    
    """
    def __init__(self, id, name, description, files):
        """ """
        self.id = id
        self.name = name
        self.description = description
        
        # split files into initial files and solution files
        self.sol_files = [ f for f in files if f.name.endswith('.sol') ]
        self.start_files = [ f for f in files if not f.name.endswith('.sol') ]
        
        self.num_solutions = len(self.sol_files)
    
    def check_file(self, result_file):
        """ """
        return "x", False
