from .validator import validate_startup


def main():

    print("=" * 50)
    print("VALIDATION TEST")
    print("=" * 50)

    # Valid record
    valid_data = {
        "recordType": "STARTUP",
        "entityName": "OpenAI",
        "employeeCount": None,
        "sourceUrl": "https://openai.com/"
    }

    print("\n--- VALID RECORD TEST ---")

    result = validate_startup(valid_data)

    if result:
        print(result.model_dump())

    # Invalid record
    invalid_data = {
        "recordType": "STARTUP",
        "entityName": "",
        "employeeCount": "not-a-number",
        "sourceUrl": "not-a-url"
    }

    print("\n--- INVALID RECORD TEST ---")

    result = validate_startup(invalid_data)

    print("\nValidation testing complete.")


if __name__ == "__main__":
    main()