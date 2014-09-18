try:
    from .prod import *
except ImportError:
    from warnings import warn
    msg = "You don't have a production settings file, using development settings."
    warn(msg, category=ImportWarning)
    from .dev import *
