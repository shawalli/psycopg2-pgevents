""" this provides validation for certain input parameters, to try to mitigate any SQL errors"""
import string

allowed_id_charset = set(string.ascii_letters + string.digits)
allowed_rowid_types = ["smallint", "int", "serial", "float", "real", "numeric", "char", "varchar", "text"]


def valid_trigger_id(triggerid: str):
    """
    check for triggerid being valid in allowed_id_charset, which is nominally 
    [a-zA-Z0-9] as per allowed_id_charset
    """
    my_set = set(triggerid)
    return my_set - allowed_id_charset


def valid_rowid_type(rowidtype: str):
    """
    check for rowidtype being a valid postgres type, nominally for now restricted to 
    numeric(integer/float) and character as per allowed_rowid_types
    """
    return rowidtype.lower() in allowed_rowid_types
