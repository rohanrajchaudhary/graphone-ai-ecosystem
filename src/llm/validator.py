from pydantic import ValidationError

from ..schemas.records import StartupRecord


def validate_startup(data):
    """
    Validate one LLM-extracted startup record.

    Returns:
        StartupRecord on success
        None on validation failure
    """

    try:
        record = StartupRecord.model_validate(data)

        print("VALID RECORD")

        return record

    except ValidationError as error:
        print("INVALID RECORD")
        print(error)

        return None