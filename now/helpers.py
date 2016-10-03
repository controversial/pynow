"""Miscellaneous helper functions used by Now."""
import os


def get_file_contents(path):
    """Return the contents of a file at a given path."""
    with open(path) as f:
        return f.read()


def recursive_folder_list(path):
    """Recursively list files inside a folder.

    Given a folder, return a list of paths to all its files and a list of
    these paths relative to the given folder.
    """
    all_files = []
    for root, dirs, files in os.walk(path):
        all_files.extend(os.path.join(root, f) for f in files)

    return (all_files, [os.path.relpath(f, path) for f in all_files])


class cachedproperty:
    def __init__(self, func):
        self.func = func
        self.cache = None
    
    # http://www.rafekettler.com/magicmethods.html#descriptor

    def __get__(self, instance, cls):
        if not self.cache:
            self.cache = self.func(instance)

        return self.cache
