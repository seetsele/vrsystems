import os
# Add the sibling `python-tools` directory to the package search path so existing modules
# can be imported as `python_tools.module_name` in tests.
_root = os.path.dirname(os.path.dirname(__file__))
_alt = os.path.join(_root, 'python-tools')
if os.path.isdir(_alt):
    __path__.insert(0, _alt)
