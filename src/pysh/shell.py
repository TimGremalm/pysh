"""IPython shell wrapper class for making an interactive shell."""
from time import sleep

import IPython
from IPython.terminal import embed
from IPython.terminal.prompts import Prompts, Token


class CfgShell(object):
    def __init__(self, debug=False):
        """
        :param bool debug:
        """
        self.debug = debug


class ShellPrompts(Prompts):
    def in_prompt_tokens(self, cli=None):
        l = [(Token, 'PYSH$ ')]
        if hasattr(self.shell, "simple_pysh_prompt"):
            l = [(Token, self.shell.simple_pysh_prompt)]
        return l

    def continuation_prompt_tokens(self, cli=None, width=None):
        return [(Token, '   ')]

    def out_prompt_tokens(self):
        return [(Token, '')]


class Pysh:
    """IPython shell wrapper class for making an interactive PYSH shell."""

    def __init__(self, dict_to_include: dict = [], prompt: str = None, banner: list = None):
        """
        Constructor for PYSH shell.
        :type dict_to_include: dict of objects will be placed under self, so they can be accessed easy in interactive
         shell. {'that': that_object, 'list'}
        """
        # Default banner messages
        self.shell = None
        self._banner_messages = []
        if banner:
            self._banner_messages = banner
        else:
            self._banner_messages = ['PYSH interactive shell',
                                     'You may leave this shell by typing `exit`, `q` or pressing Ctrl+D',
                                     'Type `h <Command>` to get usage information for a given command,',
                                     'or `h` for looking into a brief description of all commands.']
        if prompt:
            self.simple_pysh_prompt = prompt

        self.dict_to_include = dict_to_include

        # Magic functions for IPython
        self._commands = []
        self._commands_dict = {}
        self.add_command('h', self.run_h)
        self.run()

    class Error(Exception):
        pass

    class Command(object):
        def __init__(self, name, cb, parser=None, usage=None):
            self.name = name
            self.cb = cb
            self.parser = parser
            self.usage = usage

        def get_description(self):
            return self.cb.__doc__

        def get_usage(self):
            if self.parser is not None:
                return self.parser.format_help()
            elif self.usage is not None:
                return 'Usage: %s %s' % (self.name, self.usage)
            else:
                return self.get_description()

    class CommandCallbackWrapper(object):
        def __init__(self, command):
            self.command = command

        def __call__(self, args_str):
            cmd = self.command
            if args_str == '-h':
                print(cmd.get_usage())
                return

            if cmd.parser is not None:
                args = cmd.parser.parse_args(args_str.split())
                return cmd.cb(args)
            else:
                args = args_str.split()
                return cmd.cb(*args)

    def add_banner_message(self, msg):
        """Adds a message in the shell header.

        :param str msg: The message to add.
        """
        self._banner_messages.append(msg)

    def add_command(self, name, callback, usage=None, parser=None):
        """Adds a command to the shell.

        :param str name: The function name.
        :param function callback: The callback function.
        :param str usage: The usage string.
        :param parser:
        """
        cmd = self.Command(name, callback)
        if parser is not None:
            cmd.parser = parser
        if usage is not None:
            cmd.usage = usage
        self._commands.append(cmd)
        self._commands_dict[name] = cmd

    def get_banner(self) -> str:
        if self._banner_messages:
            out = ''
            out += '* ' + str('*' * 78) + '\n'
            out += '\n'.join(['* %s' % msg for msg in self._banner_messages]) + '\n'
            out += '* ' + str('*' * 78) + '\n'
            return out
        else:
            return ''

    def run(self, script_path=None):
        """Run the shell.

        :param str script_path: Script to run.
        :raises Shell.Error: In case of error.
        """
        if IPython.get_ipython() is not None:
            # raise Shell.Error('Cannot run shell from within an IPython shell.')
            pass

        self.shell = embed.InteractiveShellEmbed(
            prompts_class=ShellPrompts,
            banner1=self.get_banner(),
            exit_msg='Leaving PYSH interactive...'
        )
        for entry in self._commands:
            self.shell.register_magic_function(
                self.CommandCallbackWrapper(entry),
                magic_name=entry.name
            )
        self.shell.define_macro('q', 'quit()')
        q = self.shell.user_ns['q']
        if hasattr(self, "simple_pysh_prompt"):
            setattr(self.shell, "simple_pysh_prompt", self.simple_pysh_prompt)

        # Add dict_to_include to root namespace
        if self.dict_to_include:
            for key in self.dict_to_include.keys():
                exec(f"{key} = self.dict_to_include['{key}']", globals(), locals())

        self.shell.events.register('post_execute', self.post_execute)

        if script_path is None:
            self.shell()
        else:
            self.shell.safe_execfile_ipy(script_path)

    def post_execute(self):
        # print(f"post_execute {self}")
        pass

    def run_h(self, definition=''):
        """Shows list of commands."""
        # Definition is defined :)
        if definition != '':
            if definition in self._commands_dict:
                entry = self._commands_dict[definition]
                print(entry.get_usage())
            else:
                help(str(definition))
            return

        # General help
        print('All commands explained:')
        print('\n'.join(
            [
                ' * %s: %s' % (e.name, e.get_description())
                for e in self._commands
            ]
        ))


if __name__ == '__main__':
    class DataClass:
        def __init__(self):
            self.property_int = 1
            self.param_list = ["first entry in list", 2, 3]

        def __str__(self):
            return f"{self.property_int} {self.param_list}"

        def __repr__(self):
            return str(self)

    obj = DataClass()
    Pysh(dict_to_include={'included_object': obj})

