# -*- coding: utf-8 -*-
#
#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2010 Stéphane Bonhomme (stephane@exselt.com)
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""Kolekti exception classes"""

__author__  = '''Stéphane Bonhomme <stephane@exselt.com>'''


class OK(Exception):
    """ Class for handling HTTP 200 Satus codes

    """
    def __init__(self, *args):
        if len(args) == 1:
            self.args = (args[0], "")
        else:
            self.args = args

class Status(Exception):
    """ Class for handling HTTP 3xx Satus codes
    in general we can have the following arguments:

    """

    def __init__(self, *args):
        if len(args) == 1:
            self.args = (args[0], "")
        else:
            self.args = args

class Error(Exception):
    """ Class for handling HTTP 4xx and 5xx errors
    in general we can have the following arguments:

    1. the error code
    2. the error result element, e.g. a <multistatus> element
    """

    def __init__(self, *args):
        if len(args) == 1:
            self.args = (args[0], "")
        else:
            self.args = args

class Secret(Error):
    """ the user is not allowed to know anything about it

    returning this for a property value means to exclude it
    from the response xml element.
    """

    def __init__(self):
        Error.__init__(self, 0)
        pass


class Multistatus(Exception):
    """ Multistatus answer
    """

    def __init__(self, body):
        self.args = (body,)



class NotModified(Status):
    """ Resource was not modified"""

    def __init__(self, *args):
        if len(args):
            Status.__init__(self, 304, args[0])
        else:
            Status.__init__(self, 304)

        pass


class BadRequest(Error):
    """ invalid HTTP Query syntax"""

    def __init__(self, *args):
        if len(args):
            Error.__init__(self, 400, args[0])
        else:
            Error.__init__(self, 400)

        pass


class AuthError(Error):
    def __init__(self):
        Error.__init__(self, 401, "Authorization Requested")

class Forbidden(Error):
    """ a method on a resource is not allowed """

    def __init__(self, *args):
        if len(args):
            Error.__init__(self, 403, args[0])
        else:
            Error.__init__(self, 403, "Forbidden")


class NotFound(Error):
    """ a requested property was not found for a resource """
    def __init__(self, *args):
        if len(args):
            Error.__init__(self, 404, args[0])
        else:
            Error.__init__(self, 404, '<p>kOLEKTi could not found the requested object<br/><a href="/">Please return to kOLEKTi</a></p>')

class MethodNotAllowed(Error):
    """ The method specified in the Request-Line is not allowed
    for the resource identified by the Request-URI.
    """
    def __init__(self):
        Error.__init__(self, 405, "Method Not Allowed")


class Conflict(Error):
    def __init__(self, *args):
        if len(args):
            Error.__init__(self, 409, args[0])
        else:
            Error.__init__(self, 409, 'Conflict')
        pass

class PreconditionFailed(Error):
    """ trying to perform a MKCOL with a unsupported request body
    """
    def __init__(self):
        Error.__init__(self, 412, "Precondition Failed")

class UnsupportedMediaType(Error):
    """ trying to perform a MKCOL with a unsupported request body
    """
    def __init__(self):
        Error.__init__(self, 415, "Unsupported Media Type")


class Locked(Error):
    """ trying to perform a write on a locked resource/collection,
        without a lock in the If header
    """

    def __init__(self, *args):
        if len(args):
            Error.__init__(self, 423, args[0])
        else:
            Error.__init__(self, 423, 'Locked')

class FailedDependency(Error):
    """ Erreur de dependance
    """

    def __init__(self, *args):
        if len(args):
            Error.__init__(self, 424, args[0])
        else:
            Error.__init__(self, 424, 'Failed Dependency')

class AppError(Error):
    def __init__(self, *args):
        if len(args):
            Error.__init__(self, 500, args[0])
        else:
            Error.__init__(self, 500, "Application Error")


class UnsupportedMethod(Error):
    """ an uninplemented http method has been called """

    def __init__(self, *args):
        if len(args):
            Error.__init__(self, 501, args[0])
        else:
            Error.__init__(self, 501, "Not implemented")


class InsufficientStorage(Error):
    """ method could not be performed on the resource because the server is
    unable to store the representation needed to successfully complete the
    request.
    """
    def __init__(self, *args):
        if len(args):
            Error.__init__(self, 507, args[0])
        else:
            Error.__init__(self, 507, "Insufficient Storage")
