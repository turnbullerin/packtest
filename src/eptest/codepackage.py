""" Code that supports 'installing' a package in a programmatic fashion. """
from importlib.abc import MetaPathFinder
import importlib
import re
import sys


class TestFinder(MetaPathFinder):
    """ Implementation of MetaPathFinder that allows for direct adding of Package objects """

    def __init__(self):
        """ Constructor """
        self._test_packages = {}

    def register(self):
        """ Register this finder with sys.meta_path """
        sys.meta_path.append(self)

    def unregister(self):
        """ Remove this finder from sys.meta_path """
        sys.meta_path.remove(self)

    def clear(self):
        """ Remove all test packages from the list """
        self._test_packages = {}

    def remove_package(self, package_name):
        """ Remove a specific test package from the list """
        if package_name in self._test_packages:
            del self._test_packages[package_name]

    def add_package(self, package):
        """ Add a package to the list """
        self._test_packages[package.name] = package

    def find_spec(self, fullname, path, target=None):
        """ Stub implementation """
        return None

    def find_module(self, fullname, path):
        """ Stub implementation """
        return None

    def invalidate_caches(self):
        """ Stub implementation """
        pass

    def find_distributions(self, context=None):
        """ Implementation of find_distributions() to work with importlib.metadata """
        return [package for package in self._test_packages.values() if package.matches(context)]


class TestPackage:
    """ Bare-bones implementation of a package object as returned by the finder """

    def __init__(self, name):
        """ Constructor """
        self.name = name
        self.entry_points = EPList()

    def add_entry_point(self, ep):
        """ Add an entry point to the package """
        self.entry_points.add_entry_point(ep)

    def _normalized_name(self):
        """ Normalize the name for unique() """
        return re.sub(r"[-_.]+", "-", self.name).lower().replace('-', '_')

    def matches(self, context):
        """ Stub implementation """
        return True


class EPList:
    """ importlib_metadata uses an enhanced list object to support other methods on entry points"""

    def __init__(self):
        """ Constructor """
        self._eps = []

    def add_entry_point(self, ep):
        """ Add an entry point to the list"""
        self._eps.append(ep)

    def names(self):
        """ Get all of the names of entry points"""
        return set(ep.name for ep in self._eps)

    def __iter__(self):
        """ Iterate through all the entry points """
        return iter(self._eps)

    def select(self, **kwargs):
        """ Select entry points that match the keyword arguments """
        return set(ep for ep in self._eps if ep.matches(**kwargs))


class TestEntryPoint:
    """ Programmatic version of EntryPoint for testing

        :param name: The name of the entry point
        :type name: str
        :param group: The group the entry point belongs to
        :type group: str
        :param module: The module the entry point should load
        :type module: str
        :param attr: Optionally, an attribute from the module to load
        :type attr: str
        :param extras: Optionally, a list of extra tokens to provide
        :type extras: iterable
    """

    def __init__(self, name, group, module, attr="", extras=[]):
        """ Constructor"""
        self.name = name
        self.group = group
        self.module = module
        self.attr = attr
        self.extras = extras
        self.value = self.module
        if self.attr:
            self.value += ":{}".format(self.attr)
        if self.extras:
            self.value += " [{}]".format(", ".join(self.extras))

    def load(self):
        """ Loads the module (and, if specified, the attribute) and returns it """
        obj = importlib.import_module(self.module)
        if self.attr:
            for attr in self.attr.split('.'):
                obj = getattr(obj, attr)
        return obj

    def matches(self, **kwargs):
        """ Checks if the entry point has properties that all match the given keyword arguments"""
        for param in kwargs:
            if not kwargs.get(param) == getattr(self, param):
                return False
        return True

    def _key(self):
        """ Unique key for the module """
        return self.name, self.value, self.group
