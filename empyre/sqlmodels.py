def import_sqlmodel() -> None:
    global sqlmodel
    try:
        import sqlmodel
    except ImportError as e:
        raise ImportError('sqlmodel is not installed, run `pip install empyre[sqlmodel]`') from e
