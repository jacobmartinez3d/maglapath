"""Path-Token Module for externalizing os-specific paths from your beautiful code.

A class for converting between tokens and their platform/location-specific
paths(described in 'paths.json'). Tokens can be made up of other
tokens and combined together to create more complex procedual paths.

A token can be described in the following form:

    <token_name>

        In this form, Path will look for a matching key in 'paths.json'.
"""
import os
import re
import platform
import json

# this should be an environment variable methinks
PATHS_CONFIG = r"C:\projects\msgv.testsite.laserdome\data\paths.json"

class Path(str):
    """str-wrapper to allow handaling of paths containing tokens."""
    
    SYSTEM = platform.system().lower()
    
    # match '\' or '/' only if not preceeded by '<'
    __sep_re = r"(?<!<)[\/|\\]"
    # match any tokens
    __match_many_re = r"<[\/|\\]?\w+>"
    # match a single token with groups for sep and token name
    __match_single_re = r"^\<([\/|\\])?(\S+)\>$"

    def __init__(self, str_):
        """Initialize a tokenable-string.

        :param str_: string which may contain tokens.
        :type  str_: str
        """
        self.__str = str_
        self.__sep = os.sep

    def __new__(cls, str_):
        """Create new str instance with the resolved result.

        :param str_: the str possiblly containing tokens.
        :type  str_: str
        :return: the resolved result.
        :rtype : Path
        """
        return super(Path, cls).__new__(cls, cls.resolve(str_))

    @classmethod
    def resolve(cls, str_, sep=""):
        r"""Recursively resolve string containing tokens to its associated path.

        :param str_: the string containing tokens to resolve.
        :type  str_: str
        :param sep: the defined separator('/', or '\') to use for path-construction
        :type  sep: str
        :return: resolved path.
        :rtype:  str
        """
        if cls.is_resolved(str_):
            # make sure to return with defined sep if one was supplied
            return str_ if not sep else re.sub(cls.__sep_re, sep, str_)
            # return str_

        segs = []
        # iterate over path-segments and resolve first level of tags detected
        for seg in re.split(cls.__sep_re, str_):

            if not cls.is_token(seg):
                segs.append(seg)
                continue

            result, sep_ = cls.process_token(seg)
            segs.extend(re.split(cls.__sep_re, result))
            sep = sep_ or sep

        # if we get here and still have no defined sep, use default os.sep
        sep = sep or os.sep.replace("\\", re.escape("\\"))

        # recurse
        return cls.resolve(sep.join(segs), sep)

    def unresolved(self):
        """Return the original string before being resolved.

        :return: the original string.
        :rtype:  str
        """
        return self.__str

    def sep(self):
        """Return the current os-specific sep.

        :return: the os-specific sep.
        :rtype:  str
        """
        return self.__sep

    @classmethod
    def process_token(cls, token_candidate):
        """Process a single token.

        :param token_candidate: the str to process.
        :type  token_candidate: str
        :return: the resolved token, or the unchanged input.
        :rtype:  str
        """
        if not cls.is_token(token_candidate):
            # not a valid token, leave segment as is
            return token_candidate, None

        match = re.match(cls.__match_single_re, token_candidate)
        sep, token_name = match.groups()

        return cls.__read_from_config(token_name), sep

    @classmethod
    def is_resolved(cls, str_):
        """Determine if given str is fully resolved.

        :param str_: the str to check.
        :type  str_: str
        :return: True if the string is fully resolved, False if there are still
            tokens detected.
        :rtype:  bool
        """
        return not re.search(cls.__match_many_re, str_)

    @classmethod
    def is_token(cls, str_):
        """Determine if given str is a token.

        :param str_: the str to check.
        :type  str_: str
        :return: True if the string is in token format, False if not.
        :rtype:  bool
        """
        return re.search(cls.__match_single_re, str_)

    @classmethod
    def __read_from_config(cls, token_name):
        """Retreive the value of token_name from paths.json.

        :param token_name: the token_name to retreieve the value for.
        :type  token_name: str
        :return: value, if it exists or token_name.
        :rtype:  str
        """
        result = token_name
        with open(PATHS_CONFIG, "r") as fobj:

            result = json.load(fobj).get(token_name, token_name)
            # if we get a dict, it means we must select the platform
            if isinstance(result, dict):
                result = result[cls.SYSTEM]

        return result
