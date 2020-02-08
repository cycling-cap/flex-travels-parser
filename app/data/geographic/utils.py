from typing import Iterable

from base.exceptions import PyrTypeError


def semicircle_to_degree(semicircles):
    """
    convert coordinate from semicircles to degree
    @:param semicircles, lat, lng or lat&lng pair value in semicircles, support str, int and iterable object
    """
    if isinstance(semicircles, str) and ',' in semicircles:
        semicircles = semicircles.split(',')
    if isinstance(semicircles, Iterable):
        return [semicircle_to_degree(i) for i in semicircles]
    if isinstance(semicircles, str) and semicircles.isdigit():
        semicircles = int(semicircles)
    if isinstance(semicircles, int):
        return semicircles * semicircles * (180 / 2 ** 31)
    else:
        raise PyrTypeError('semicircles must be a int, or int transformable object, but got %r ' % semicircles)


def mps_to_kph(value):
    """
    convert speed form m/s to km/h
    """
    try:
        if isinstance(value, str):
            value = float(value)
        ret = value * 3.6
    except TypeError as err:
        raise PyrTypeError('speed value must be a numeric, or numeric transformable object, but got %r ' % value)

    return ret


def m_to_km(value):
    """
    convert distance from m to kilometers
    """
    try:
        if isinstance(value, str):
            value = float(value)
        ret = value * 3.6
    except TypeError as err:
        raise PyrTypeError('distance value must be a numeric, or numeric transformable object, but got %r ' % value)

    return ret
