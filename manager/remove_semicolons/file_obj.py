# file_obj.py

class File:
    """
    
    """
    def __init__(self, name, lines):
        self.name = name;
        self.lines = lines;
        # test print lines
        for line in lines:
            print(line);

    def __eq__(self, other):
        return self.name.split('.sol')[0] == other.name.split('.sol')[0];

    def __str__(self):
        s = '--{}--'.format(self.name);
        s += "\n";
        for line in self.lines:
            ''.join([s, line+"\n"]);

        return s;
