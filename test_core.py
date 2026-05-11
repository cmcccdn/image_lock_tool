"""Lightweight tests — run on any platform.

Usage:  python test_core.py
"""
import os
import sys
import json
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from image_lock.core import config


class ConfigTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.mkdtemp(prefix="ilt_test_")
        self._orig_path = config.get_config_path
        config.get_config_path = lambda: os.path.join(self._tmp, "config.json")

    def tearDown(self):
        config.get_config_path = self._orig_path

    def test_normalise(self):
        self.assertEqual(config.normalise_ext("jpg"), "jpg")
        self.assertEqual(config.normalise_ext(".JPG"), "jpg")
        self.assertEqual(config.normalise_ext("*.PNG"), "png")
        self.assertEqual(config.normalise_ext("foo.WebP"), "webp")
        self.assertEqual(config.normalise_ext("C:/x/y.tiff"), "tiff")
        self.assertEqual(config.normalise_ext(""), "")

    def test_default_load_save(self):
        cfg = config.load_config()
        self.assertIn("jpg", cfg["extensions"])
        self.assertEqual(cfg["checkInterval"], 120)
        self.assertTrue(cfg["enabled"])

        cfg["extensions"]["jpg"] = True
        cfg["checkInterval"] = 300
        self.assertTrue(config.save_config(cfg))

        cfg2 = config.load_config()
        self.assertTrue(cfg2["extensions"]["jpg"])
        self.assertEqual(cfg2["checkInterval"], 300)

    def test_get_locked_exts(self):
        cfg = config.load_config()
        cfg["extensions"]["jpg"] = True
        cfg["extensions"]["png"] = True
        cfg["extensions"]["gif"] = False
        locked = sorted(config.get_locked_exts(cfg))
        self.assertEqual(locked, ["jpg", "png"])

    def test_custom_ext_persists(self):
        cfg = config.load_config()
        cfg["extensions"]["xyz"] = True
        config.save_config(cfg)
        cfg2 = config.load_config()
        self.assertTrue(cfg2["extensions"]["xyz"])


if __name__ == "__main__":
    unittest.main()
