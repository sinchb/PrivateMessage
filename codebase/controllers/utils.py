#-*- coding=utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
try:
    from ujson import dumps, loads
except ImportError:
    print 'Warning: Unable to import ujson'
    from json import dumps, loads

from zlib import compress, decompress

__all__ = ('enc', 'dec')

def enc(event, args, binary=None, compression_minsize=1024):
    '''
    Encode event into string; compress if too large
    ``compression_minsize``: data compression minimal size, in bytes
    '''
    if not isinstance(event, basestring):
        raise TypeError, 'event name must be a string.'
    if not isinstance(args, dict):
        raise TypeError, 'args must be a dictionary.'
    if not isinstance(binary, (type(None), basestring)):
        raise TypeError, 'binary must be a basestring.'

    msg = {'name': event, 'args': args}
    raw_msg = dumps(msg)
    if len(raw_msg) > compression_minsize:
        return 'GZIP' + compress(raw_msg)[2:-4]
    else:
        return 'JSON' + raw_msg

def dec(msg):
    '''Decode received message.'''
    if msg.startswith('JSON'):
        value = loads(msg[4:])
    elif msg.startswith('GZIP'):
        try:
            value = loads(unicode(decompress(msg[4:], -15), errors='replace'))
        except Exception as err:
            raise ValueError('Cannot decompress/decode msg: ' + str(err))
    else:
        raise ValueError('Unsupported NetProtocol.')

    if not isinstance(value, dict):
        raise ValueError('Msg must a json.')

    if not 'name' in value:
        raise ValueError('Missing event name')
    if not 'args' in value:
        raise ValueError('Missing event args')

    event = value['name']
    args = value['args']

    if not isinstance(event, basestring):
        raise TypeError('Event name must be a string.')
    if not isinstance(args, dict):
        raise TypeError('Args must be a dictionary.')

    return event, args
