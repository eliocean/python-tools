import subprocess
import sys


def run_shell(shell):
    """执行shell并随时打印输出"""
    cmd = subprocess.Popen(shell, stdin=subprocess.PIPE, stderr=sys.stderr, close_fds=True,
                           stdout=sys.stdout, universal_newlines=True, shell=True, bufsize=1)

    cmd.communicate()
    return cmd.returncode

if __name__ == '__main__':
    print(run_shell("ping www.baidu.com"))