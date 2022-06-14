import unittest
import importlib.util
import eptest
import sys

if importlib.util.find_spec("importlib.metadata"):
    from importlib.metadata import entry_points, Distribution
else:
    from importlib_metadata import entry_points, Distribution


class TestPackTest(unittest.TestCase):

    def test_finder_registration(self):
        finder = eptest.TestFinder()
        self.assertNotIn(finder, sys.meta_path)
        finder.register()
        self.assertIn(finder, sys.meta_path)
        finder.unregister()
        self.assertNotIn(finder, sys.meta_path)

    def test_package_registration(self):
        finder = eptest.TestFinder()
        finder.register()
        package = eptest.TestPackage("foobar")
        finder.add_package(package)
        installed_packages = [x for x in Distribution.discover()]
        self.assertIn(package, installed_packages)
        finder.unregister()

    def test_ep_registration(self):
        finder = eptest.TestFinder()
        finder.register()
        package = eptest.TestPackage("foobar")
        ep = eptest.TestEntryPoint("foo", "foobar", "eptest", "TestFinder", ["foo", "bar"])
        package.add_entry_point(ep)
        finder.add_package(package)
        self.assertIn(ep, entry_points(group="foobar"))
        finder.unregister()

    def test_finder_clearing(self):
        finder = eptest.TestFinder()
        finder.add_package(eptest.TestPackage("foobar"))
        finder.add_package(eptest.TestPackage("zazz"))
        self.assertIn("foobar", finder._test_packages)
        self.assertIn("zazz", finder._test_packages)
        finder.clear()
        self.assertNotIn("foobar", finder._test_packages)
        self.assertNotIn("zazz", finder._test_packages)

    def test_finder_remove(self):
        finder = eptest.TestFinder()
        finder.add_package(eptest.TestPackage("foobar"))
        finder.add_package(eptest.TestPackage("zazz"))
        self.assertIn("foobar", finder._test_packages)
        self.assertIn("zazz", finder._test_packages)
        finder.remove_package("foobar")
        self.assertNotIn("foobar", finder._test_packages)
        self.assertIn("zazz", finder._test_packages)


class TestEntryPoint(unittest.TestCase):

    def test_load_module(self):
        ep = eptest.TestEntryPoint("foobar", "foobar", "eptest")
        mod = ep.load()
        self.assertTrue(hasattr(mod, "TestPackage"))
        self.assertTrue(hasattr(mod, "TestEntryPoint"))
        self.assertTrue(hasattr(mod, "__version__"))

    def test_load_attribute(self):
        ep = eptest.TestEntryPoint("foobar", "foobar", "eptest.codepackage", "TestEntryPoint")
        cls = ep.load()
        self.assertEqual(cls, eptest.TestEntryPoint)

    def test_load_subattribute(self):
        ep = eptest.TestEntryPoint("foobar", "foobar", "eptest.codepackage", "TestEntryPoint.__init__")
        cls = ep.load()
        self.assertEqual(cls, eptest.TestEntryPoint.__init__)

    def test_properties(self):
        ep = eptest.TestEntryPoint("fb", "foobar", "eptest.codepackage", "TestEntryPoint", extras=["foo", "bar"])
        self.assertIn("foo", ep.extras)
        self.assertIn("bar", ep.extras)
        self.assertEqual(ep.name, "fb")
        self.assertEqual(ep.group, "foobar")
        self.assertEqual(ep.module, "eptest.codepackage")
        self.assertEqual(ep.attr, "TestEntryPoint")
