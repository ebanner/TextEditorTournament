import sys
import difflib

with open('foo.txt', 'r') as f:
    with open('bar.txt', 'r') as g:
        f_lines = f.readlines()
        g_lines = g.readlines()

        for line in difflib.unified_diff(f_lines, g_lines, fromfile='foo.txt',
                tofile='bar.txt'):
            sys.stdout.write(line)
