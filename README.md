# PackTest

This module is designed to provide a strictly in-code implementation of MetaPathFinder that can be leveraged in unit
testing in order to simulate an entry point being created, as would be loaded by `importlib.metadata.entry_points()` 
in Python 3.8+ or by `importlib_metadata.entry_points()` in earlier versions. 

If there are requests, additional functionality aimed at testing plugin packages may be added in future releases.


## Usage
```python
import unittest
import packtest

class Test(unittest.TestCase):

    def test_me(self):
        # Could move some of this to be a test fixture instead
        
        # Finder on sys.meta_path
        finder = packtest.TestFinder()
        
        # Add it to sys.meta_path
        finder.register()
        
        # Create a package
        package = packtest.TestPackage("foobar")
        
        # Create entry points
        package.add_entry_point(
            # Equivalent to a module with the following in setup.cfg:
            # [options.entry_points]
            # myep.group = 
            #     foobar = myep.tests:test.attr  
            packtest.TestEntryPoint("foobar", "myep.group", "myep.tests", "test.attr")
        )

        package.add_entry_point(
            # Equivalent to a module with the following in setup.cfg:
            # [options.entry_points]
            # myep.group = 
            #     foobar2 = myep.tests:test.attr[bar]  
            packtest.TestEntryPoint("foobar2", "myep.group", "myep.tests", "test.attr", ["bar"])
        )
        finder.add_package(package)

        # ... do tests
        
        # Call this to remove your foobar test package
        finder.remove_package(package)

        # Remove all packages
        finder.clear()
        
        # It is necessary to clean up sys.meta_path after your test case with this:
        finder.unregister()

```
