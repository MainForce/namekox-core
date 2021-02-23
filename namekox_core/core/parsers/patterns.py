#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import unicode_literals


import re


try:
    import regex
except ImportError:  # pragma: no cover
    ENV_VAR_MATCHER = re.compile(
        r"""
            \$\{       # match characters `${` literally
            ([^}:\s]+) # 1st group: matches any character except `}` or `:`
            :?         # matches the literal `:` character zero or one times
            ([^}]+)?   # 2nd group: matches any character except `}`
            \}         # match character `}` literally
        """, re.VERBOSE
    )
else:
    ENV_VAR_MATCHER = regex.compile(
        r"""
        \$\{                #  match ${
        (                   #  first capturing group: variable name
            [^{}:\s]+       #  variable name without {,},: or spaces
        )
        (?:                 # non capturing optional group for value
            :               # match :
            (               # 2nd capturing group: default value
                (?:         # non capturing group for OR
                    [^{}]   # any non bracket
                |           # OR
                    \{      # literal {
                    (?2)    # recursive 2nd capturing group aka ([^{}]|{(?2)})
                    \}      # literal }
                )*          #
            )
        )?
        \}                  # end of macher }
        """,
        regex.VERBOSE
    )


IMPLICIT_ENV_VAR_MATCHER = re.compile(
    r"""
        .*          # matches any number of any characters
        \$\{.*\}    # matches any number of any characters
                    # between `${` and `}` literally
        .*          # matches any number of any characters
    """, re.VERBOSE
)
