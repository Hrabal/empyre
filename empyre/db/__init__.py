try:
    import sqlmodel  # noqa
except ImportError as e:
    raise ImportError("sqlmodel is not installed, run `pip install sqlmodel`") from e

from .db import EmpyreDb  # noqa
