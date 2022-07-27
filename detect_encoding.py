# -*- coding: utf-8 -*-
"""
Attempt to identify the encoding of a text file.

When the encoding is unknown check the encoding cookie or, if necessary, attempt to decode the
binary string using various codecs.
"""


__version__ = '1.0.1'  # major.minor.micro as specified in PEP 440
__status__ = 'Production'

__author__ = 'Jason Callahan'
__mail__ = ''
__credits__ = ['Jason Callahan']  # Additional contributors
__maintainer__ = 'Jason Callahan'

__license__ = 'MIT'
__copyright__ = '2022'


# Standard Libraries
import os
import sys
import tokenize

# Third Party Libraries
from colorama import Fore as TextColor
from colorama import Style as TextStyle
from colorama import init as InitColorama


# Python 3.7 codec list.
CODECS: list = [
    'ascii', 'utf-7', 'utf-8-sig', 'utf-8', 'utf-16', 'utf-16-be', 'utf-16-le', 'utf-32', 'utf-32-be',
    'utf-32-le', 'big5', 'big5hkscs', 'cp037', 'cp273', 'cp424', 'cp437', 'cp500', 'cp720', 'cp737',
    'cp775', 'cp850', 'cp852', 'cp855', 'cp856', 'cp857', 'cp858', 'cp860', 'cp861', 'cp862', 'cp863',
    'cp864', 'cp865', 'cp866', 'cp869', 'cp874', 'cp875', 'cp932', 'cp949', 'cp950', 'cp1006', 'cp1026',
    'cp1125', 'cp1140', 'cp1250', 'cp1251', 'cp1252', 'cp1253', 'cp1254', 'cp1255', 'cp1256', 'cp1257',
    'cp1258', 'cp65001', 'euc-jp', 'euc-jis-2004', 'euc-jisx0213', 'euc-kr', 'gb2312', 'gbk', 'gb18030',
    'hz', 'iso2022-jp', 'iso2022-jp-1', 'iso2022-jp-2', 'iso2022-jp-2004', 'iso2022-jp-3',
    'iso2022-jp-ext', 'iso2022-kr', 'latin-1', 'iso8859-2', 'iso8859-3', 'iso8859-4', 'iso8859-5',
    'iso8859-6', 'iso8859-7', 'iso8859-8', 'iso8859-9', 'iso8859-10', 'iso8859-11', 'iso8859-13',
    'iso8859-14', 'iso8859-15', 'iso8859-16', 'johab', 'koi8-r', 'koi8-t', 'koi8-u', 'kz1048',
    'mac-cyrillic', 'mac-greek', 'mac-iceland', 'mac-latin2', 'mac-roman', 'mac-turkish', 'ptcp154',
    'shift-jis', 'shift-jis-2004', 'shift-jisx0213'
]

InitColorama()  # Use Colorama console text colors on Windows. Uncessary for Linux.


def detect_encoding(file_path: str, **kwargs) -> str:
    """
    Attempt to identify the encoding of a text file.

    Parameters
    ----------
    file_path : str
        DESCRIPTION.
    **kwargs : dict
        full_check: Read the entire file contents for decoding attempts. If false only the first line
            will be read. Useful for very large files, but result in failure to identify text that
            improperly decodes later in the file. Defaults is True.
        size: The file size in mb to prevent very large text files from being read and processed.
            Default is None, which imports all file sizes.
        verbose: Prints each codec and True/False to the console as each decode attempt occurs.

    Returns
    -------
    str
        The detected codec.

    """
    codec_known: bool = False
    detected_codec: str = None
    py_version: tuple = sys.version_info

    params: dict = {
        'full_check': True,
        'size': None,
        'verbose': False
    }

    for key, value in kwargs.items():
        params[key] = value

    # This module may include codecs which are not included in Python versions less than 3.7.
    assert py_version[0] >= 3 and py_version[1] >= 7, 'Python version must be at least 3.7'

    file_size: float = round(os.path.getsize(file_path) / 1048576, 4)  # File size in MB

    if params['size'] is not None:
        assert file_size < params['size'], 'The file size is greater than the set limit.'
        sys.exit()

    with open(file_path, 'rb') as file:
        try:
            # Check the encoding cookie for encoding information.
            # Throw SyntaxError if it cannot be found.
            token: tuple = tokenize.detect_encoding(file.readline)

        except SyntaxError as err:
            # If the syntax error is not related to identifying the encoding, re-raise the error.
            if 'invalid or missing encoding declaration for' in str(err) is False:
                raise

            if params['verbose']:
                print(TextStyle.BRIGHT)
                print(TextColor.RED, 'No encoding cookie present. Starting decode attempts...')

        else:
            detected_codec = token[0]
            codec_known = True

    with open(file_path, 'rb') as file:
        if params['full_check']:
            contents: str = file.read()

        else:
            contents: str = file.readline()

    while codec_known is False:
        for codec in CODECS:
            codec_known = attempt_decode(contents, codec)

            if params['verbose']:
                if codec_known:
                    print(TextColor.GREEN, f'{codec}: True')

                else:
                    print(TextColor.RED, f'{codec}: False')

            if codec_known:
                detected_codec = codec

                break

    print(TextStyle.RESET_ALL)

    return detected_codec


def attempt_decode(text: bin, codec: str) -> bool:
    """
    Attempt to identify if the given codec is suitable for the file by decoding the contents.

    Parameters
    ----------
    text : bin
        The contents of the file, or text line, as a binary string.
    codec : str
        The codec to be used when attempting to decode the text.

    Returns
    -------
    str
        codec_found: bool
    """
    codec_found: bool = False

    try:
        text.decode(codec)

        codec_found = True

    except UnicodeDecodeError:
        pass

    finally:
        return codec_found
