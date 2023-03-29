__all__ = (
    "get_lib_version",
    "get_installed_libraries",
)


import re
import subprocess  # noqa S404

from ..constants import LIB_PATH


_VERSION_REGEX: re.Pattern[str] = re.compile(r"^__version__\s*=\s*[\'\"]([^\'\"]*)[\'\"]", re.MULTILINE)


def get_lib_version() -> str:
    file = LIB_PATH.joinpath("__init__.py").read_text("utf-8")
    version: str
    if (result := _VERSION_REGEX.search(file)) is None:
        version = "0.0.0"
    else:
        version = result.group(1)

    try:
        out: bytes
        err: bytes

        # commit count
        p = subprocess.Popen(  # noqa S603, S607
            ["git", "rev-list", "--count", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = p.communicate()
        if out:
            version += f"+{out.decode('utf-8').strip()}"

        # commit sha
        p = subprocess.Popen(  # noqa S603, S607
            ["git", "rev-parse", "--short", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = p.communicate()
        if out:
            version += f"+g{out.decode('utf-8').strip()}"

    except Exception as e:  # noqa: F841  # ToDo: logging
        ...

    return version


def get_installed_libraries() -> dict[str, str]:
    """
    Gets every installed library via ``pip list``

    Returns
    -------
    dict[str, str]
        A dictionary with {package: version}.
    """
    out: bytes
    err: bytes
    p: str
    v: str
    libraries: dict[str, str] = {}

    out, err = subprocess.Popen(  # noqa S603, S607
        ["pip", "list"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).communicate()

    if out:
        for pkg in out.decode().splitlines(keepends=False):
            p, v = pkg.split()
            if p == "Package" and v == "Version":
                continue
            if max(len(s.replace("-", "")) for s in [p, v]) == 0:
                continue
            libraries[p] = v

    return libraries
