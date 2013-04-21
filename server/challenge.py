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
        """Returns the diff of the result file or False if no corresponding
        solution file exists."""
        if result_file not in self.sol_files:
            print('No solution file found for: {}'.format(result_file.name))
            print(result_file.name)
            print(result_file.lines)
            for sol_file in self.sol_files:
                print(sol_file.name)
                print(sol_file.lines)
            return False

        # Get the corresponding solution file
        solution_file = self.sol_files[self.sol_files.index(result_file)]

        diff = []
        for line in difflib.unified_diff(
                result_file.lines,
                solution_file.lines, 
                fromfile=result_file.name, 
                tofile=solution_file.name+'.sol'
                ):
            diff.append(line.strip())

        return diff
