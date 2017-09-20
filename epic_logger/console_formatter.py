
from colorlog import ColoredFormatter, escape_codes

RESERVED_ATTRS = (
    'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
    'funcName', 'levelname', 'levelno', 'lineno', 'module',
    'msecs', 'message', 'msg', 'name', 'pathname', 'process',
    'processName', 'relativeCreated', 'stack_info', 'thread', 'threadName', 'ctx')

RESERVED_ATTR_HASH = dict(zip(RESERVED_ATTRS, RESERVED_ATTRS))

def append(color_code='', parent='', message=None, key=None, value=None):
    """
    Merges extra props to message string
    :param color_code: the color of the key
    :param parent: parent key
    :param message: string to append to
    :param key: key to use when appending
    :param value: value to use when appending. It can be a string, dict or an object
    """

    if isinstance(value, str):
        if parent != '':
            parent = parent + '.'
        message += "\n" + color_code + parent + key + escape_codes['reset'] + "=" + value
    elif isinstance(value, dict):
        for k, v in value.items():
            message = append(color_code=color_code, parent=key, message=message, key=k, value=v)
    elif isinstance(value, (list, tuple)):
        value = ', '.join(map(str, value))
        message = append(color_code=color_code, parent=parent, message=message, key=key, value=value)
    elif hasattr(value, '__dict__'):
        for k, v in value.__dict__.items():
            message = append(color_code=color_code, parent=key, message=message, key=k, value=v)
    return message

class ConsoleFormatter(ColoredFormatter, object):
    def __init__(self, fmt=None, datefmt=None, style='%',
                log_colors=None, reset=True,
                secondary_log_colors=None):
        ColoredFormatter.__init__(self, fmt=fmt, datefmt=datefmt, 
                                style=style, log_colors=log_colors, reset=reset,
                                secondary_log_colors=secondary_log_colors)

    def format(self, record):
        """Format a message from a record object."""
        message = super(ConsoleFormatter, self).format(record)
        color_code = self.color(self.log_colors, record.levelname)
        if hasattr(record, 'ctx'):
            metadata = record.ctx.invocation_metadata()
            for item in metadata:
                if item.key == 'author_name':
                    setattr(record, 'user', item.value)
                elif item.key == 'correlation_id':
                    setattr(record, 'correlationId', item.value)

        for key, value in record.__dict__.items():
            #this allows to have numeric keys
            if (key not in RESERVED_ATTR_HASH
                and not (hasattr(key, "startswith")
                        and key.startswith('_'))):
                message = append(color_code=color_code, message=message, key=key, value=value)
        return message
