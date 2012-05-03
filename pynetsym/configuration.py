import collections
import argparse
import sys


class ConfigurationError(RuntimeError):
    pass


class _ListTask(object):
    def __init__(self, parser, lst):
        self.lst = lst
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
        self._consider_defaults()

    def consider_command_line(self):
        self.tasks.append(_ListTask(self.parser, sys.argv))

    def consider(self, entity):
        if isinstance(entity, collections.Mapping):
            self._consider_dict(entity)
        elif isinstance(entity, basestring):
            self._consider_seq(entity.split())
        elif hasattr(entity, 'read'):
            self._consider_file(entity)
        elif isinstance(entity, collections.Sequence):
            self._consider_seq(entity)
        elif entity is None:
            pass
        else:
            raise TypeError("Don't know what to do with %s" % entity)

    def _consider_defaults(self):
        self.tasks.append(_ListTask(self.parser, []))

    def _consider_dict(self, dct):
        if dct:
            self.tasks.append(_DictTask(self.parser, dct))

    def _consider_seq(self, seq):
        if seq:
            self.tasks.append(_ListTask(self.parser, seq))

    def _consider_file(self, file_handle):
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

