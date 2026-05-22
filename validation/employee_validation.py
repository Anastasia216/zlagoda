def validate_employee(data):
    errors =[]
    phone_number = data['phone_number']
    if phone_number > 13:
        errors.append("Phone number must can't be more than 13")
    salary = data['salary']
    if salary < 0:
        errors.append("Salary can't be negative")
    return errors