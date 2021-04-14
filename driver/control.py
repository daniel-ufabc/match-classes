import os
import subprocess
import psutil
import signal

import config
from utils.files import data_filename as fn

CLEAN, RUNNING, SUCCESS, FAILURE, ZOMBIE = range(5)
names = ['CLEAN', 'RUNNING', 'SUCCESS', 'FAILURE', 'ZOMBIE']

# ######################################################################### ACTIONS:


def peek():
    if os.path.exists(fn(config.SCHEDULER_RESULT_FILE)):
        return SUCCESS
    pid = running_pid()
    if pid:
        try:
            process = psutil.Process(pid)
            if process.status() == psutil.STATUS_ZOMBIE:
                return ZOMBIE
            return RUNNING
        except psutil.NoSuchProcess:
            clear_running_file()
    if os.path.exists(fn(config.SCHEDULER_OUTPUT_FILE)):
        return FAILURE
    return CLEAN


def reset():
    state = peek()
    assert state != RUNNING, 'Cannot reset a running job: use stop instead or wait for it to finish.'
    pid = running_pid()
    if pid:
        try:
            process = psutil.Process(pid)
            if process.status() == psutil.STATUS_ZOMBIE:
                kill_process(pid)
        except psutil.NoSuchProcess:
            pass

    clear_files()


def stop():
    state = peek()
    assert state == RUNNING or state == ZOMBIE, 'Cannot stop job if it is not running.'

    pid = running_pid()
    kill_process(pid)


def start(max_search=None, default_parameter=None):
    assert max_search is not None, 'Field max_search is missing.'
    assert default_parameter is not None, 'Field default_parameter is missing.'
    assert peek() == CLEAN, 'Cannot start job if state is not clean.'

    p = subprocess.Popen([
        'python',
        '-m',
        config.SCHEDULER_EXECUTE_MODULE,
        str(max_search),
        str(default_parameter)
    ], start_new_session=True)

    with open(config.SCHEDULER_RUNNING_FILE, 'w') as f:
        f.write(f'{p.pid}\n')

# ######################################################################### PLUMBING:


def get_result_filenames():
    return config.SCHEDULER_RESULT_FILE, fn(config.SCHEDULER_RESULT_FILE)


def get_logs_filenames():
    return config.SCHEDULER_OUTPUT_FILE, fn(config.SCHEDULER_OUTPUT_FILE)


def clear_running_file():
    try:
        os.remove(fn(config.SCHEDULER_RUNNING_FILE))
    except IOError:
        pass


def clear_files():
    files = [
        config.SCHEDULER_RUNNING_FILE,
        config.SCHEDULER_OUTPUT_FILE,
        config.SCHEDULER_ERROR_FILE,
        config.SCHEDULER_RESULT_FILE
    ]
    for file in files:
        try:
            os.remove(fn(file))
        except FileNotFoundError:
            pass


def running_pid():
    try:
        with open(config.SCHEDULER_RUNNING_FILE) as f:
            return int(f.readline().strip())
    except (FileNotFoundError, ValueError):
        return None


def kill_process(pid):
    try:
        os.killpg(os.getpgid(pid), signal.SIGTERM)
        os.waitpid(pid, 0)
    except PermissionError:
        os.waitpid(pid, 0)
    except ProcessLookupError:
        pass


def get_progress():
    if not os.path.exists(fn(config.SCHEDULER_OUTPUT_FILE)):
        return 0

    def read_feedback(enc='utf-8'):
        last_line = ''
        with open(fn(config.SCHEDULER_OUTPUT_FILE), encoding=enc) as h:
            for line in h:
                last_line = line
                if '+' in line:
                    # Vinícius imprime um char para cada 2% de progresso
                    return 2 * len(line.strip())

        return last_line

    try:
        return read_feedback()
    except UnicodeDecodeError:
        return read_feedback('latin1')


# ######################################################################### TESTS:


def current_dir():
    """
    Returns the iturmas folder
    :return: "/home/daniel/PycharmProjects/iturmas/iturmas"
    """
    # return os.getcwd()
    pass
