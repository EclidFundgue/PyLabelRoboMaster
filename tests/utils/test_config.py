import os
import unittest

from src.utils.config import ConfigManager


class TestConfigManager(unittest.TestCase):
    def test_init(self):
        tmp_path = './tmp.json'
        config_manager = ConfigManager(tmp_path)

        self.assertTrue(os.path.exists(tmp_path))

        os.remove(tmp_path)

    def test_readAndWirte(self):
        tmp_path = './tmp.json'
        key = 'load_network'

        config_manager = ConfigManager(tmp_path)
        self.assertFalse(config_manager[key])
        config_manager[key] = True
        self.assertTrue(config_manager[key])

        config_manager2 = ConfigManager(tmp_path)
        self.assertTrue(config_manager2[key])

        os.remove(tmp_path)