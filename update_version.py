import datetime
import pathlib
import re
import subprocess


_VERSION_REGEX: re.Pattern[str] = re.compile(r"(^__version__\s*=\s*[\'\"])([^\'\"]*)([\'\"]).*", re.MULTILINE)
_CLEAN_VERSION_REGEX: re.Pattern[str] = re.compile(r"^([^+]*)")
LIB_PATH: pathlib.Path = pathlib.Path(__file__).parent.joinpath("AlbertoX3")
FILE: pathlib.Path = LIB_PATH.joinpath("__init__.py")


# slightly adapted version of AlbertoX3.utils.terminal.get_lib_version
def get_lib_version() -> str:
    version: str
    if (result := _VERSION_REGEX.search(FILE.read_text("utf-8"))) is None:
        version = "0.0.0"
    else:
        version = result.group(2)

    if (result := _CLEAN_VERSION_REGEX.match(version)) is not None:
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

    except Exception:  # noqa
        pass

    return version


def main() -> int:
    notice = f"  # last updated: {datetime.datetime.utcnow()} UTC"

    new_file = _VERSION_REGEX.sub(rf"\g<1>{get_lib_version()}\g<3>{notice}", FILE.read_text("utf-8"), 1)
    FILE.write_text(new_file, "utf-8")

    return 0


if __name__ == "__main__":
    exit(main())
