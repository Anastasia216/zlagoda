from datetime import datetime, date
def validate_employee(data):
    errors =[]
    phone_number = data['phone_number']
    if len(phone_number) > 13:
        errors.append("Phone number must can't be more than 13")
    try:
        salary = float(data['salary'])

        if salary < 0:
            errors.append("Salary can't be negative")

    except ValueError:
        errors.append("Salary must be a number")
    try:
        birth_date = datetime.strptime(
            data["date_of_birth"],
            "%Y-%m-%d"
        ).date()

        start_date = datetime.strptime(
            data["date_of_start"],
            "%Y-%m-%d"
        ).date()

        age_at_start = (
                start_date.year
                - birth_date.year
                - (
                        (start_date.month, start_date.day)
                        < (birth_date.month, birth_date.day)
                )
        )

        if age_at_start < 18:
            errors.append(
                "Employee must be at least 18 years old on the start date."
            )
    except ValueError:
        errors.append("Invalid date.")
    return errors
