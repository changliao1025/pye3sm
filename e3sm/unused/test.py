import subprocess

def bash_command(cmd):
    subprocess.Popen(cmd, shell=True) #, executable='/bin/bash')
def bash_command2(cmd):
    subprocess.Popen(['/bin/bash', '-c', cmd])
bash_command2('a="Apples and oranges" && echo "${a/oranges/grapes}"')


