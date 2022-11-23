import os
import subprocess
import threading

import paramiko
import yaml


class Cash:
    def __init__(self):
        pass


class Cp:
    Type = 1
    black = f'\033[{Type};30m'
    red = f'\033[{Type};31m'
    green = f'\033[{Type};32m'
    yellow = f'\033[{Type};33m'
    blue = f'\033[{Type};34m'
    magna = f'\033[{Type};35m'
    cyan = f'\033[{Type};36m'
    white = f'\033[{Type};1m'
    reset = f"\033[{Type};39m"


def fprint(*args, color: [Cp, str] = Cp.cyan, **kwargs):
    print(*(f'{color}{v}' for v in args), **kwargs)


def string_to_contract(string: str) -> str:
    contract, last_t, string = '', 0, string.replace(' ', '-')
    vocabs = [i for i, v in enumerate(string) if v == '-']
    cab = [s for i, s in enumerate(vocabs) if i != len(vocabs) - 1 if s + 1 != vocabs[i + 1]]
    for i, current in enumerate(cab):
        if string[last_t:current] == '-contract':
            if string[current:cab[i + 1]] == '-address:---':
                contract = string[cab[i + 1]:cab[i + 2]].replace('-', '')

        last_t = current
    return contract


def sys_run(command: str):
    os.system(command)


def clear_fn():
    sys_run('clear' if os.name == 'posix' else 'cls')


def get_logs(cmd: str = ''):
    s = subprocess.check_output(cmd, shell=True, universal_newlines=True)
    print(s)
    return s


def os_runer(command: [list, str], thread: int = -1):
    fprint('{:>25}'.format(
        f'{"Commands : " if isinstance(command, list) else "Command : "} {[v for v in command] if isinstance(command, list) else command}'))
    cash = Cash()
    threads = []
    setattr(cash, 'thread', [])
    if thread == -1:
        fprint('using default thread')
        if isinstance(command, list):
            for i, c in enumerate(command):
                v = threading.Thread(target=sys_run, args=(c,))
                cash.thread.append(v)
                fprint('{} Adding {:>30} Done'.format(i, c), color=Cp.yellow)
        else:
            # print(command)
            c = threading.Thread(target=sys_run, args=(command,))
            cash.thread.append(c)

        for t in cash.thread:
            t.start()
            # t.run()
            threads.append(t)
        for t in threads:
            fprint('Waiting Til Thread Ends')
            t.join()
            get_logs()

    else:
        if isinstance(command, list):
            for c in command:
                os.system(c)
                get_logs()
        else:
            os.system(command)
            get_logs()


def thread_runner(target, args, wtl: bool = False):
    t1 = threading.Thread(target=target, args=args)
    t1.start()
    if wtl: t1.join()


def hyp_loader(path: [str, os.PathLike]):
    with open(path, 'r') as r:
        data = yaml.full_load(r)
    return data


def print_client_out(outs):
    print(outs[1].read().decode())


def runcommand(client_server, command):
    return client_server.exec_command(command)


def connect(hostname, username, password, port: int = 22):
    client_server = paramiko.client.SSHClient()
    client_server.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client_server.connect(hostname, username=username, password=password, port=port)
    return client_server


def check_if_get_ok(req):
    req = str(req)
    return True if req == '<Response [200]>' else False