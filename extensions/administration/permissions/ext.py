__all__ = ("Permissions",)


from AlbertoX3.ipy_wrapper import Extension
from AlbertoX3.utils import get_logger


logger = get_logger(__name__)


class Permissions(Extension):
    requires = {"lib": [], "ext": ["administration.roles"]}
    # ToDo: manage/set
    # ToDo: view
