from pwd import getpwnam
from os import setuid, setgid
from multiprocessing import Process, Pipe

import logging
logger = logging.getLogger(__name__)

from time import time

def sudef(func):
    """
    Executes `func` as another unix user, determined by the first parameter.
    Caution: if you are using this on class/object methods, changes are not
    reflected in the parent process
    """
    def wrapper(*args, **kwargs):
        try:
            user = args[0] if isinstance(args[0], str) or not any((
                isinstance(args[0], object),
                isinstance(args[0], type)
            )) else args[1]
        except IndexError:
            raise ValueError("Calling {} without parameters".format(func))
        parent_conn, child_conn = Pipe()

        def target(*args, **kwargs):
            passwd = getpwnam(user)
            uid = passwd[2]
            gid = passwd[3]

            setgid(gid)
            setuid(uid)

            # prevent exceptions from running into nowhere
            try:
                ret = func(*args, **kwargs)
            except Exception as e:
                ret = e
            child_conn.send(ret)

        process = Process(target=target, args=args, kwargs=kwargs)

        t = time()
        process.start()
        ret = parent_conn.recv()
        process.join()

        logger = logging.getLogger(__name__)        
        logger.debug("Time to run subprocess: {}".format(time() - t))
        
        # if it's a exception, re-raise it
        if isinstance(ret, Exception):
            raise ret
        else:
            return ret

    return wrapper
