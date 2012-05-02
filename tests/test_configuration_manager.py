from unittest import TestCase
from pynetsym import configuration


class TestConfigurationManager(TestCase):

    def testDefault(self):
        default_value = 100
        options = (
            ('--alpha', dict(default=default_value)),
        )
        configuration_manager = configuration.ConfigurationManager(options)
        configuration_manager.consider_line('')
        arguments = configuration_manager.process()
        self.assertDictEqual(dict(alpha=default_value), arguments)

