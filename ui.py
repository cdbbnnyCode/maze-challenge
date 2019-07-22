#!/usr/bin/env python3
import os
import subprocess
import re
import time
import readline
import atexit

import interp
import servo


DELAY_TIME = 1 # Delay time in seconds


def print_help():
    print("Marble Maze UI v1.0")
    print("Type 'viewall' to view the current programs")
    print("Type 'listall' to list the team names and numbers of all of the current programs")
    print("Type 'edit <team> <maze number>' to edit a program")
    print("Type 'run [team] [maze number]' to run a specified program, or the one that was last edited")
    print("Type Ctrl+C or Ctrl+D to exit")
    print()
    print("In the editor:")
    print("Use Ctrl+O to save and Ctrl+X to exit--more shortcuts are shown along the bottom")
    print()
    print("NOTE: Commands here ARE case sensitive, but programs are not!")

def edit(filename):
    subprocess.run(['/bin/nano', filename])

def get_filename(team, maze):
    team.replace(' ', '_')
    return 'codes/%s-%s.txt' % (str(team), str(maze))

def get_id_from_filename(filename):
    match = re.match('(.+)-([0-9]+).txt', os.path.basename(filename))
    if not match:
        print("%s is not a valid file name?!" % filename)
        return ('?', '0')
    return match.groups()

def get_files_matching(pattern, files):
    patt = re.compile(pattern)
    out = []
    for f in files:
         if patt.match(f):
             out.append(f)
    return out

def view_all():
    files = os.listdir('codes/')
    while len(files) > 0:
        team_name = get_id_from_filename(files[0])[0]
        team_files = sorted(get_files_matching('%s-[0-9]+.txt' % team_name, files))
        termwidth = int(subprocess.run(['tput', 'cols'], stdout=subprocess.PIPE).stdout.decode('utf-8'))
        print("Team %s:" % team_name)
        print('-' * (termwidth - 1))
        cols = []
        rows = 0
        for f in team_files:
            col = []
            height = 1 # Pre-count the header line
            file_num = get_id_from_filename(f)[1]
            col.append('Maze %s' % file_num)
            with open('codes/' + f) as fdata:
                for line in fdata:
                    line = line.strip()
                    col.append(line)
                    height += 1
            cols.append(col)
            files.remove(f)
            rows = max(rows, height)

        col_width = termwidth / len(cols) - len(cols)
        # print("Column width: %d" % col_width)
        for i in range(rows):
            coleslaw = 0
            for col in cols:
                x = (col_width + 1) * coleslaw
                # print(x)
                if x > 0:
                    print('\x1B[%dC' % x, end='')
                if i >= len(col):
                    print(end='\r')
                    coleslaw += 1
                    continue
                if len(col[i]) > col_width:
                    col[i] = col[i][:(len(col[i]) - col_width - 3)] + '...'
                print(col[i], end='\r') # End with \r to return to the beginning of the line
                coleslaw += 1
            print()

def list_all():
    files = os.listdir('codes/')
    while len(files) > 0:
        team_name = get_id_from_filename(files[0])[0]
        team_files = sorted(get_files_matching('%s-[0-9]+.txt' % team_name, files))
        print("Team %s: " % team_name, end='')
        i = 0
        for f in team_files:
            maze_num = get_id_from_filename(f)[1]
            print(maze_num, end='')
            if i < len(team_files) - 1:
                print(', ', end='')
            i += 1
            files.remove(f)
        print()

def run(filename):
    servo.init_outputs()
    interp.read_command('')
    print("Ready to go! Place the marble and press Enter to run")
    input()
    try:
        with open(filename) as file:
            for line in file:
                line = line.strip()
                print(line)
                retval = interp.read_command(line)
                if retval != 0:
                    break
                time.sleep(DELAY_TIME)
            servo.disable_servos()
    except KeyboardInterrupt:
        print()
        servo.disable_servos()
        return

prev_filename = None

def parse_input(line):
    global prev_filename
    line = line.strip()
    if line == 'help':
        print_help()
    elif line == 'viewall':
        view_all()
    elif line == 'listall':
        list_all()
    elif line == 'run':
        if prev_filename is None:
            print("You haven't edited or run any programs yet!")
            print("Edit a program or specify which file to run")
            return
        else:
            run(prev_filename)
    else: # These commands take arguments and need regexes to parse
        edit_match = re.match('edit (.+) ([0-9]+)', line)
        if edit_match:
            prev_filename = get_filename(edit_match.groups()[0], edit_match.groups()[1])
            edit(prev_filename)
            if not os.path.exists(prev_filename):
                print("The file you edited was not saved (and does not exist)--you will not be able to run it!")
                prev_filename = None
                return
        else:
            run_match = re.match('run (.+) ([0-9]+)', line)
            if run_match:
                prev_filename = get_filename(run_match.groups()[0], run_match.groups()[1])
                run(prev_filename)
            else:
                print("Unknown command: %s" % line)

def init_readline():
    histfile = '.ui_history'
    try:
        readline.read_history_file(histfile)
        readline.set_history_length(1000)
    except FileNotFoundError:
        pass
    atexit.register(readline.write_history_file, histfile)

if __name__ == "__main__":
    if not os.path.exists('codes/'):
        os.mkdir('codes/')
    init_readline()
    print_help()
    try:
        while True:
            parse_input(input('> '))
    except (KeyboardInterrupt, EOFError):
        print()
