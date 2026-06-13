from datetime import datetime, date
import re
def validate_employee(data):
    errors =[]
    phone_number = data['phone_number']
    if not re.fullmatch(r"\+380\d{9}", phone_number):
        errors.append(
            "Phone number must be in format +380XXXXXXXXX"
        )
    raw_salary = data.get('salary', '').strip()

    if not raw_salary:
        errors.append("Salary is required.")
    else:
        try:
            salary = float(raw_salary)
            if salary <= 0:
                errors.append("Salary must be greater than 0.")

            elif salary > 1000000:
                errors.append("Salary exceeds maximum allowed limit.")

            if '.' in raw_salary:
                decimals = raw_salary.split('.')[1]
                if len(decimals) > 2:
                    errors.append("Salary cannot have more than 2 decimal places.")

        except ValueError:
            errors.append("Salary must be a valid number.")
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
