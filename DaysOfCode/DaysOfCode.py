import os
import subprocess
import datetime
import re
import shutil
import contextlib
from .Git import Git

days_of_code_remote = 'https://github.com/kallaway/100-days-of-code'
name_of_repo = '100-days-of-code'

log_template = """### Day {0}: {1}

**Today's Progress** {2}

**Thoughts** {3}

**Link to work** [{4}]({5})"""


class DaysOfCodeException(Exception):
    pass


class DaysOfCode:
    __slots__ = ['_config', '_git', '_path']

    def __init__(self, path: str) -> None:
        self._set_path(path)
        self._config = os.path.join(os.path.expanduser('~'), '.100DaysOfCode')
        self._git = Git(self._path)

    def start(self):
        self._update_config()
        self._git.clone_remote(days_of_code_remote)
        self._write_log_header()
        self._print_message(os.linesep +
                            'Congratulations, you are now ready to start the 100 Days Of Code challenge.' +
                            os.linesep + os.linesep +
                            'Good Luck' +
                            os.linesep
                            )

    def restart(self):
        self._write_log_header()

    def new_day(self):
        if not os.path.isfile(self._config):
            raise DaysOfCodeException('Log file does not exist.')
        current_date = datetime.datetime.now()
        day = self._get_next_day()
        date = '{}'.format(current_date.strftime('%B %d, %Y'))
        progress = input('What progress have you made today? ')
        while progress == '':
            progress = input('Please ensure you log your progress, no point keeping a journal otherwise: ')
        thoughts = input('What were the highlights (good or bad)? ')
        if thoughts == '':
            thoughts = input('No thoughts today? '
                             'Logging your thoughts can help identify what you need to work on at a later date: ')

        project_name = input('What is the name of the project you have been working on? ')
        while project_name == '':
            project_name = input('Your project needs a name, how else will you remember what you were working on? ')
        project_url = input('What is the URI for the project? ')
        if project_url == "":
            project_url = '#'
        log_entry = log_template.format(day, date, progress, thoughts, project_name, project_url)
        log_path = os.path.join(self._get_repo_path(), 'log.md')
        file = open(log_path, 'a')
        file.write('\r\n\r\n{}'.format(log_entry))
        file.close()
        self._git.add_file(repository='100-days-of-code')
        self._git.commit(repository='100-days-of-code', message='Day {} added'.format(day))
        self._print_message(os.linesep +
                            'Congratulations on completing day ' +
                            str(day) +
                            ' of your 100 Days of code challenge.' +
                            os.linesep
                            )

    def display_day(self, day: int = 0) -> None:
        regex_parse_day = r'### (?:Day )([0-9]*)(?::)([^*]*)(?:\s)' \
                          r'(?:\*\*Today\'s Progress\*\*)([^*]*)(?:\s)' \
                          r'(?:\*\*Thoughts\*\*)([^*]*)(?:\s)' \
                          r'(?:\*\*Link to work\*\*)([^#]*)'
        if day != 0:
            regex_parse_day = r'### (?:Day )({})(?::)([^*]*)' \
                              r'(?:\s)(?:\*\*Today\'s Progress\*\*)([^*]*)(?:\s)' \
                              r'(?:\*\*Thoughts\*\*)([^*]*)(?:\s)' \
                              r'(?:\*\*Link to work\*\*)([^#]*)'.format(day)
        days_matches = re.findall(regex_parse_day, self._get_log_content())
        if len(days_matches) == 0:
            print('Days not found.')
        for day_matches in days_matches:
            print('###### DAY {} ######'.format(day_matches[0]))
            print('Date: {}'.format(day_matches[1].rstrip()))
            print('Progress: {}'.format(day_matches[2].rstrip()))
            print('Thoughts: {}'.format(day_matches[3].rstrip()))
            print('Link to work: {}'.format(day_matches[4].rstrip()))
            print('')

    def edit_day(self):
        pass

    def end(self):
        pass

    def _set_path(self, path: str) -> None:
        path_input = os.path.expanduser(path)
        while not os.path.exists(path_input):
            path_input = input('The specified path does not exist (' + path_input + '): ')
            path_input = os.path.expanduser(path_input)
        self._path = path_input

    def _get_path(self) -> str:
        if not os.path.isfile(self._config):
            raise DaysOfCodeException('No path identified. Have you started yet?')
        file = open(file=self._config, mode='r')
        path = file.read()
        file.close()
        return path

    def _update_config(self):
        file = open(file=self._config, mode='w')
        file.write(self._get_repo_path())
        file.close()

    def _get_repo_path(self):
        return os.path.join(self._path, name_of_repo)

    def _write_log_header(self) -> None:
        log_path = os.path.join(self._get_repo_path(), 'log.md')
        text = '# 100 Days Of Code - Log'
        if not os.path.isfile(log_path):
            raise DaysOfCodeException('Log file does not exist.')
        file = open(file=log_path, mode='w')
        file.write(text)
        file.close()

    def _delete_project(self) -> None:
        shutil.rmtree(self._get_repo_path())
        with contextlib.suppress(FileNotFoundError):
            os.remove(self._config)

    def _get_next_day(self) -> int:
        """Returns the number of the next day from the log file. If no day can be found returns 1."""
        day = 1
        regex = r'(?:### Day )([0-9]+)'
        matches = re.findall(regex, self._get_log_content())
        if matches:
            day = int(matches[-1]) + 1
        return day

    def _get_log_content(self) -> str:
        log_path = os.path.join(self._get_repo_path(), 'log.md')
        file = open(log_path, 'r')
        log_text = file.read()
        file.close()
        return log_text

    @staticmethod
    def _print_message(message: str, error: bool = False) -> None:
        if error:
            """Do something to change color"""
            pass
        print(message)
