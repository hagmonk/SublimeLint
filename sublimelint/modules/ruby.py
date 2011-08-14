# ruby.py - sublimelint package for checking ruby files

import os
import subprocess


def check(codeString, filename):
    info = None
    if os.name == 'nt':
        info = subprocess.STARTUPINFO()
        info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        info.wShowWindow = subprocess.SW_HIDE

    process = subprocess.Popen(('env', 'ruby', '-wc'),
                  stdin=subprocess.PIPE,
                  stdout=subprocess.PIPE,
                  stderr=subprocess.STDOUT,
                  startupinfo=info)
    result = process.communicate(codeString)[0]

    return result

# start sublimelint Ruby plugin
import re
__all__ = ['run', 'language']
language = 'Ruby'
description =\
'''* view.run_command("lint", "Ruby")
        Turns background linter off and runs the default Ruby linter
        (ruby -c, assumed to be on $PATH) on current view.
'''


def run(code, view, filename='untitled'):
    errors = check(code, filename)

    lines = set()
    underline = []  # leave this here for compatibility with original plugin

    messages = {"error": {}, "warning": {}}

    def addMessage(lineno, message, message_type):
        message = str(message)
        if lineno in messages[message_type]:
            messages[message_type][lineno].append(message)
        else:
            messages[message_type][lineno] = [message]

    for line in errors.splitlines():
        match = re.match(r'^.+:(?P<line>\d+):\s+(?P<error>.+)', line)

        if match:
            error, line = match.group('error'), match.group('line')

            lineno = int(line) - 1
            lines.add(lineno)

            if (re.match(r'^warning', error) != None):
                addMessage(lineno, error, "warning")
            else:
                addMessage(lineno, error, "error")

    return lines, underline, [], [], messages["error"], {}, messages["warning"]
