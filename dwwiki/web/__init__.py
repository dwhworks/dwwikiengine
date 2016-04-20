# -*- coding: utf-8 -*-

def _fixup_deps():
    """
    Alter the system path to import some 3rd party dependencies from
    inside support package. This is meant for deps
    used inside this package
    """
    import sys, os
    from dwwiki import support
    dirname = os.path.dirname(support.__file__)
    dirname = os.path.abspath(dirname)
    found = False
    for path in sys.path:
        if os.path.abspath(path) == dirname:
            found = True
            break
    if not found:
        sys.path.insert(0, dirname)

try:
    _fixup_deps()
finally:
    del _fixup_deps
