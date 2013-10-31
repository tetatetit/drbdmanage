#!/usr/bin/python

__author__="raltnoeder"
__date__ ="$Sep 12, 2013 11:15:38 AM$"

"""
return code for successful operations
"""
DM_SUCCESS  = 0

"""
return codes for failed operations
"""
# function not implemented
DM_ENOTIMPL = 0x7fffffff

# invalid name for an object
DM_ENAME    = 100

# no entry = object not found
DM_ENOENT   = 101

# entry already exists
DM_EEXIST   = 102

# invalid IP type (not 4=IPv4 or 6=IPv6)
DM_EIPTYPE  = 103

# invalid minor number
DM_EMINOR   = 104

# Volume size out of range
DM_EVOLSZ   = 105

# Invalid option value
DM_EINVAL   = 106

# Cannot write configuration to or load configuration from persistent storage
DM_EPERSIST = 107

# Invalid node id or no free node id for auto-assignment
DM_ENODEID  = 108

# Invalid volume id or no free volume id for auto-assignment
DM_EVOLID   = 109

# Invalid port number or no free port numbers for auto-assignment
DM_EPORT    = 110

# An operation of the storage subsystem layer failed
DM_ESTORAGE = 111

# DEBUG value
DM_DEBUG    = 1023

_DM_EXC_TEXTS = dict()
_DM_EXC_TEXTS[DM_ENAME]    = "Invalid name"
_DM_EXC_TEXTS[DM_ENOENT]   = "Object not found"
_DM_EXC_TEXTS[DM_EEXIST]   = "Object already exists"
_DM_EXC_TEXTS[DM_EIPTYPE]  = "Invalid IP protocol type"
_DM_EXC_TEXTS[DM_EMINOR]   = "Minor number out of range or no " \
  "free minor numbers"
_DM_EXC_TEXTS[DM_EVOLSZ]   = "Volume size out of range"
_DM_EXC_TEXTS[DM_EINVAL]   = "Invalid option"
_DM_EXC_TEXTS[DM_DEBUG]    = "Debug exception / internal error"
_DM_EXC_TEXTS[DM_ENOTIMPL] = "Function not implemented"
_DM_EXC_TEXTS[DM_EPERSIST] = "I/O error while accessing persistent " \
  "configuration storage"
_DM_EXC_TEXTS[DM_ENODEID]  = "Invalid node id or no free node id number"
_DM_EXC_TEXTS[DM_ENODEID]  = "Invalid volume id or no free volume id number"
_DM_EXC_TEXTS[DM_EPORT]    = "Invalid port number or no free port numbers"
_DM_EXC_TEXTS[DM_ESTORAGE] = "The storage subsystem failed to perform the " \
  "requested operation"


def dm_exc_text(id):
    try:
        text = _DM_EXC_TEXTS[id]
    except KeyError:
        text = "<<No error message for id %d>>" % (str(id))
    return text


class InvalidNameException(Exception):
    def __init__(self):
        pass


class InvalidAddrFamException(Exception):
    def __init__(self):
        pass


class VolSizeRangeException(Exception):
    def __init__(self):
        pass


class InvalidMinorNrException(Exception):
    def __init__(self):
        pass


class InvalidMajorNrException(Exception):
    def __init__(self):
        pass


class IncompatibleDataException(Exception):
    def __init__(self):
        pass


class SyntaxException(Exception):
    def __init__(self):
        pass

class PersistenceException(Exception):
    def __init__(self):
        pass
