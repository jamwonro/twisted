# -*- test-case-name: twisted.python.test.test_systemd -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Integration with systemd.

Currently only the minimum APIs necessary for using systemd's socket activation
feature are supported.
"""


__all__ = ["ListenFDs"]

from os import getpid
from typing import Iterable, List, Mapping, Optional


class ListenFDs:
    """
    L{ListenFDs} provides access to file descriptors inherited from systemd.

    Typically L{ListenFDs.fromEnvironment} should be used to construct a new
    instance of L{ListenFDs}.

    @cvar _START: File descriptors inherited from systemd are always
        consecutively numbered, with a fixed lowest "starting" descriptor.  This
        gives the default starting descriptor.  Since this must agree with the
        value systemd is using, it typically should not be overridden.

    @ivar _descriptors: A C{list} of C{int} giving the descriptors which were
        inherited.
    """

    _START = 3

    def __init__(self, descriptors: List[int]) -> None:
        """
        @param descriptors: The descriptors which will be returned from calls to
            C{inheritedDescriptors}.
        """
        self._descriptors = descriptors

    @classmethod
    def fromEnvironment(
        cls,
        environ: Optional[Mapping[str, str]] = None,
        start: Optional[int] = None,
    ) -> "ListenFDs":
        """
        @param environ: A dictionary-like object to inspect to discover
            inherited descriptors.  By default, L{None}, indicating that the
            real process environment should be inspected.  The default is
            suitable for typical usage.

        @param start: An integer giving the lowest value of an inherited
            descriptor systemd will give us.  By default, L{None}, indicating
            the known correct (that is, in agreement with systemd) value will be
            used.  The default is suitable for typical usage.

        @return: A new instance of C{cls} which can be used to look up the
            descriptors which have been inherited.
        """
        if environ is None:
            from os import environ as _environ

            environ = _environ
        if start is None:
            start = cls._START

        descriptors: List[int] = []

        try:
            pid = int(environ["LISTEN_PID"])
        except (KeyError, ValueError):
            pass
        else:
            if pid == getpid():
                try:
                    count = int(environ["LISTEN_FDS"])
                except (KeyError, ValueError):
                    pass
                else:
                    descriptors = list(range(start, start + count))
                    del environ["LISTEN_PID"], environ["LISTEN_FDS"]

        return cls(descriptors)

    def inheritedDescriptors(self) -> Iterable[int]:
        """
        @return: The configured descriptors.
        """
        return list(self._descriptors)
