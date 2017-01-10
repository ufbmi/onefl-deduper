"""
Goal: Implement convenience class for managing configurations.

Copied from https://github.com/pallets/flask/blob/master/flask/config.py#L110
"""
import os
import types
import errno
import importlib


class Config(dict):
    """"
    :arg root_path: the prefix for building
        paths to the config files when calling :meth:from_pyfile
    """
    def __init__(self, root_path, defaults=None):
        dict.__init__(self, defaults or {})
        self.root_path = root_path

    def from_pyfile(self, filename, silent=False):
        """Updates the values in the config from a Python file.

        :param filename: the filename of the config.  This can either be an
                         absolute filename or a filename relative to the
                         root path.
        :param silent: set to ``True`` if you want silent failure for missing
                       files.

        """
        filename = os.path.join(self.root_path, filename)
        d = types.ModuleType('config')
        d.__file__ = filename
        try:
            with open(filename) as config_file:
                exec(compile(config_file.read(), filename, 'exec'), d.__dict__)
        except IOError as e:
            if silent and e.errno in (errno.ENOENT, errno.EISDIR):
                return False
            e.strerror = 'Unable to load configuration file (%s)' % e.strerror
            raise
        self.from_object(d)
        return True

    def from_object(self, obj):
        """Updates the values from the given object.  An object can be of one
        of the following two types:
        -   a string: in this case the object with that name will be imported
        -   an actual object reference: that object is used directly
        :param obj: an import name or object
        """
        string_types = (str,)

        if isinstance(obj, string_types):
            # github.com/pallets/werkzeug/blob/master/werkzeug/utils.py+L399
            # obj = import_string(obj)
            obj = importlib.import_module(obj)

        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)

    def from_dictionary(self, dictionary):
        """
        Helper function for overriding config values
        """
        for key, value in dictionary.items():
            if key.isupper():
                self[key] = value
