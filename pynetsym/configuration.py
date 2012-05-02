import argparse
import sys


class ConfigurationError(RuntimeError):
    pass

class _LineTask(object):
    def __init__(self, parser, line):
        self.line = line
        self.parser = parser

    def process(self):
        namespace = self.parser.parse_args(self.line.split())
        return vars(namespace)

class _ListTask(object):
    def __init__(self, parser, list):
        self.lst = list
        self.parser = parser

    def process(self):
        namespace = self.parser.parse_args(self.lst)
        return vars(namespace)

class _DictTask(object):
    def __init__(self, parser, dct):
        self.parser = parser
        self.dct = dct

    def process(self):
        return dict(self.dct)

class ConfigurationManager(object):
    def __init__(self, option_description):
        self.option_description = option_description
        self._check_duplicated_options(self.option_description)
        self.tasks = []
        self._build_parser()

    def consider_command_line(self):
        self.tasks.append(_ListTask(self.parser, sys.argv))

    def consider_line(self, line):
        if line:
            self.tasks.append(_LineTask(self.parser, line))

    def consider_list(self, lst):
        if lst:
            self.tasks.append(_ListTask(self.parser, lst))

    def consider_dct(self, dct):
        if dct:
            self.tasks.append(_DictTask(self.parser, dct))

    def consider_file(self, file_handle):
        raise NotImplementedError()

    def _build_parser(self):
        self.parser = argparse.ArgumentParser(
            add_help=True,
            description='Synthetic Network Generation Utility',
            argument_default=argparse.SUPPRESS)
        self._load_arguments(self.option_description)

    def _check_duplicated_options(self, options):
        #TODO: try to fix so that more informative stuff happens
        names = [option_line[0] for option_line in options]
        names.extend(option_line[1] for option_line in options
            if isinstance(option_line[1], basestring))
        if len(names) > len(set(names)):
            raise ConfigurationError(
                "Duplicated option name somewhere.")

    def _load_arguments(self, options):
        """
        Loads options sequence into parser.

        Each option line is in the form:
            1. (short_option_name, long_option_name, parameters)
            2. (long_option_name, parameters)

        @param options: sequence of options
        """
        for option_element in options:
            self._load_line(option_element)

    def _load_line(self, option_element):
        try:
            short_option, long_option, params = option_element
            self.parser.add_argument(short_option, long_option, **params)
        except ValueError:
            try:
                long_option, params = option_element
                self.parser.add_argument(long_option, **params)
            except ValueError:
                self.parser.add_argument(option_element[0])

    def process(self):
        final_arguments = {}
        for task in self.tasks:
            arguments = task.process()
            final_arguments.update(arguments)
        return final_arguments

