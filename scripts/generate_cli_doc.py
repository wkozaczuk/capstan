#
# This script is meant to be run manually when you introduce a change in capstan API.
# It stores capstan --help texts into markdown file so that user is able to read them without
# having Capstan even installed. Please note that if you think some command/argument is not
# explained well enough, then you should UPDATE CAPSTAN to print better description (not this
# script).
#
# Before running the script:
#   * make sure that latest capstan executable is in folder $GOPATH/bin
#   *
#
# Run like this:
#   $ cd $HOME/go/src/github.com/mikelangelo-project/capstan
#   $ ./scripts/generate_cli_doc.py
# The result is Documentation/generated/CLI.md file (overrides the old file completely).
#


import subprocess
import os
from datetime import datetime


class Command:
    def __init__(self, cmd):
        self.cmd = cmd


class Group:
    def __init__(self, title, description, commands):
        self.title = title
        self.description = description
        self.commands = commands


RESULT_FILE = os.path.join('.', 'Documentation', 'generated', 'CLI.md')
CAPSTAN_DIR = os.path.join(os.environ['GOPATH'], 'bin')
GROUPS = [
    Group('Working with application packages',
          'These commands are useful when packaging my application into Capstan package.', [
              Command('capstan package init'),
              Command('capstan package collect'),
              Command('capstan package compose'),
          ]),
    Group('Integrating existing packages',
          'These commands are useful when we intend to use package from remote repository.', [
              Command('capstan package list'),
              Command('capstan package search'),
              Command('capstan package pull'),
          ]),
    Group('Working with runtimes',
          'Runtime-related commands.', [
              Command('capstan runtime list'),
              Command('capstan runtime preview'),
              Command('capstan runtime init'),
          ]),
    Group('Executing unikernel',
          'Commands used to run composed package.', [
              Command('capstan run'),
          ]),
    Group('Executing unikernel on OpenStack',
          'Commands used to compose unikernel, upload it to OpenStack Glance and run it with OpenStack Nova.', [
              Command('capstan stack push'),
              Command('capstan stack run'),
          ]),
    Group('Configuring Capstan tool',
          'Commands used to configure Capstan.', [
              Command('capstan config print'),
          ]),
]


def get_command_description(command, flags=['--help']):
    stdout, stderr = subprocess.Popen(
        command.cmd.split() + flags,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={'PATH': CAPSTAN_DIR}
    ).communicate()

    if stderr:
        print ('STDERR: %s' % stderr)
        return None
    return stdout


def generate_cli_documentation():
    res = '''
<!---

THIS FILE IS AUTOGENERATED USING `./scripts/generate_cli_doc.py`.
DO NOT MODIFY IT MANUALLY, MODIFY THE SCRIPT INSTEAD.

-->

# CLI Reference
Here we describe Capstan CLI in detail. Please note that this very same information can be obtained
by adding --help flag to any of the listed commands.
'''

    for group in GROUPS:
        res += '''
## %s
%s
''' % (group.title, group.description)

        for command in group.commands:
            descr = get_command_description(command)
            if descr is not None:
                res += '''
### %s
```
%s
```
''' % (command.cmd, descr)

    # Append some visible metadata
    res += '\n---\n'  # vertical space
    res += '<sup>'
    res += '  Documentation compiled on: %s\n' % datetime.utcnow().strftime('%Y/%m/%d %H:%M')
    res += '  <br>\n'
    res += '  %s' % get_command_description(Command('capstan'), flags=['--version'])
    res += '</sup>'

    with open(RESULT_FILE, 'w') as f:
        f.write(res)


if __name__ == '__main__':
    # verify that Capstan executable exists
    try:
        get_command_description(Command('capstan'))
    except:
        print('Capstan executable could not be found inside %s' % CAPSTAN_DIR)
        exit()

    print('Generating CLI documentation into %s' % RESULT_FILE)
    generate_cli_documentation()
    print('CLI documentation dumped into: %s' % RESULT_FILE)