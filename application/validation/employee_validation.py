def validate_employee(data):
    errors =[]
    phone_number = data['phone_number']
    if len(phone_number) > 13:
        errors.append("Phone number must can't be more than 13")
    salary = float(data['salary'])
    if salary < 0:
        errors.append("Salary can't be negative")
    return errors