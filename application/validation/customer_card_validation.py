def validate_customer_card(data):
    errors = []
    phone_number = data['phone_number']
    if len(phone_number) > 13:
        errors.append("Phone number must be less than 13")
    percent = float(data['percent'])
    if percent > 100 or percent < 0:
        errors.append("Percent must be between 0 and 100")
    return errors