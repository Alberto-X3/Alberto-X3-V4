__all__ = ("Maintenance",)


from AlbertoX3.ipy_wrapper import Extension
from AlbertoX3.utils import get_logger


logger = get_logger(__name__)


class Maintenance(Extension):
    requires = {"lib": [], "ext": ["administration.roles"]}
    # ToDo: start
    # ToDo: stop
