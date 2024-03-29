#!/usr/bin/env python3
import os
import subprocess
import re
import time
import readline
import shlex
import atexit
import json
import getch

import interp
import servo


DELAY_TIME = 1 # Delay time in seconds


def print_help():
    print("Marble Maze UI v1.2")
    print("Type 'viewall' to view the current programs")
    print("Type 'listall' to list the team names and numbers of all of the current programs")
    print("Type 'edit <team> <maze number/color>' to edit a program")
    print("Type 'run [team] [maze number]' to run a specified program, or the one that was last edited")
    print("Type 'hold' to initialize the servos")
    print("Type 'stop' to stop the servos")
    print("Type 'orient' to set the tilt directions")
    print("Type 'help' to show this help")
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
    match = re.match(r'(.+)-(.+)\.txt', os.path.basename(filename))
    if not match:
        print("%s is not a valid file name?!" % filename)
        return ('?', '?')
    return match.groups()

def get_files_matching(pattern, files):
    patt = re.compile(pattern)
    out = []
    for f in files:
         if patt.match(f):
             out.append(f)
    return out

def view_all():
    files = get_files_matching(r'.+-.+\.txt', os.listdir('codes/'))
    while len(files) > 0:
        team_name = get_id_from_filename(files[0])[0]
        team_files = sorted(get_files_matching(r'%s-.+\.txt' % team_name, files))
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
                    col[i] = col[i][:int(len(col[i]) - col_width - 3)] + '...'
                print(col[i], end='\r') # End with \r to return to the beginning of the line
                coleslaw += 1
            print()

def list_all():
    files = get_files_matching(r'.+-.+\.txt', os.listdir('codes/'))
    while len(files) > 0:
        team_name = get_id_from_filename(files[0])[0]
        team_files = sorted(get_files_matching(r'%s-.+\.txt' % team_name, files))
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
    global DELAY_TIME
    interp.read_command('')
    print("Ready to go! Place the marble and press Enter to run")
    try:
        with open(filename, 'r') as file:
            input()
            for line in file:
                line = line.strip()
                print(line)
                if line.startswith('.'):
                    # . commands are special and parsed by the ui
                    directive = shlex.split(line[1:])
                    if directive[0] == 'time':
                        try:
                            DELAY_TIME = float(directive[1])
                        except ValueError:
                            print("Syntax error: '%s' is not a number" % directive[1])
                            break
                        except IndexError:
                            print("Syntax error: .time requires an argument")
                            break
                else:
                    retval = interp.read_command(line)
                    if retval != 0:
                        break
                time.sleep(DELAY_TIME)
    except KeyboardInterrupt:
        print()
    servo.disable_servos() # Comment this out to keep the servos initialized after finishing
#    if input('Success? y/N> ') == 'y':
#        # Create/modify the completion time
#        open('times/' + os.path.basename(filename), 'w').close()

prev_filename = None

def get_key():
    k = getch.getch()
    if k == '\x03':
        raise KeyboardInterrupt()
    if k == '\x1B':
        getch.getch() # [
        sub = getch.getch()
        return "\\" + sub
    else:
        return k

def get_orientation():
    dir = None
    while True:
        k = get_key()
        sub = ""
        if len(k) > 1:
            sub = k[1]
        # reset the orientation
        interp.orientation = {"down": "-x", "left": "-y"}
        # A=Up, B=Down, C=Right, D=Left
        if sub == "A":
            interp.read_command("U")
            dir = "+x"
        elif sub == "B":
            interp.read_command("D")
            dir = "-x"
        elif sub == "C":
            interp.read_command("R")
            dir = "+y"
        elif sub == "D":
            interp.read_command("L")
            dir = "-y"
        elif k == "\r":
            if dir is not None:
                break
    return dir

def orient():
    print("Set the tilt direction")
    print("Use the arrow keys to point the maze DOWN (towards you)")
    print("Press Enter when done")
    down = get_orientation()
    if down == "-x":   left = "-y"
    elif down == "+x": left = "+y"
    elif down == "-y": left = "+x"
    elif down == "+y": left = "-x"
    interp.read_command('')
#    print("Use the arrow keys to point the maze to the LEFT; press Enter to finish")
#    left = get_orientation()
#    print("Down: %s, left: %s" % (down, left))
    with open("/tmp/orientation.json", 'w') as f:
        conf = {"down": down, "left": left}
        json.dump(conf, f)
    servo.disable_servos()
    # Reload everything
    servo.init_outputs()
    interp.init()

def parse_input(line):
    global prev_filename
    line = line.strip()
    if len(line) == 0:
        return
    elif line == 'help':
        print_help()
    elif line == 'viewall':
        view_all()
    elif line == 'listall':
        list_all()
    elif line == 'hold':
        interp.read_command('')
    elif line == 'stop':
        servo.disable_servos()
    elif line == 'orient':
        orient()
    elif line == 'run':
        if prev_filename is None:
            print("You haven't edited or run any programs yet!")
            print("Edit a program or specify which file to run")
            return
        else:
            run(prev_filename)
    else: # These commands take arguments and need regexes to parse
        edit_match = re.match('edit (.+) (.+)', line)
        if edit_match:
            prev_filename = get_filename(edit_match.groups()[0], edit_match.groups()[1])
            edit(prev_filename)
            if not os.path.exists(prev_filename):
                print("The file you edited was not saved (and does not exist)--you will not be able to run it!")
                prev_filename = None
                return
        else:
            run_match = re.match('run (.+) (.+)', line)
            if run_match:
                prev_filename = get_filename(run_match.groups()[0], run_match.groups()[1])
                try:
                    run(prev_filename)
                except FileNotFoundError:
                    print("That program doesn't exist!")
            else:
                print("Unknown command: %s" % line)

def onexit():
    print("You are now exiting the maze challenge UI.")
    print("To start the UI again, type:")
    print("  python ui.py")
    print()
    print("To shut down, type:")
    print("  sudo halt")
    print("and wait for the green LED on the Pi to turn off.")

def init_readline():
    histfile = '.ui_history'
    try:
        readline.read_history_file(histfile)
        readline.set_history_length(1000)
    except FileNotFoundError:
        pass
    atexit.register(readline.write_history_file, histfile)
    atexit.register(onexit)

def mkdir_if_not_exists(dirname):
    if not os.path.exists(dirname):
        os.mkdir(dirname)

if __name__ == "__main__":
    mkdir_if_not_exists('codes/')
#    mkdir_if_not_exists('times/')

    interp.init()
    servo.init_outputs()
    if not os.path.exists('/tmp/orientation.json'):
        orient()

    init_readline()
    print_help()
    try:
        while True:
            parse_input(input('> '))
    except (KeyboardInterrupt, EOFError):
        print()
