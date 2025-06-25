

def age2int(age: str):
    try:
        return int(age.strip().replace('YO', ''))
    except (ValueError, AttributeError):
        return None  # or raise an error if you prefer


sex_map = {
    'Gelding': 0,
    'Filly': 1,
    'Mare': 2,
    'Horse': 3
}


def sex2int(sex: str):
    return sex_map.get(sex, -1)


colour_map = {
    'Bay': 0,
    'Chestnut': 1,
    'Bay or Brown': 2,
    'Brown': 3
}


def colour2int(colour: str):
    return colour_map.get(colour, -1)


country_map = {
    'NZ': 2,
    'IRE': 3,
    'FR': 4,
    'USA': 5,
    'GB': 6
}


def country2int(country: str):
    if not country:
        return 1
    # Remove parentheses and whitespace, then uppercase
    normalized = country.strip().replace('(', '').replace(')', '').upper()
    return country_map.get(normalized, 0)


def money2int(money: str):
    if not money:
        return 0
    # Remove $ and commas, then convert to int
    cleaned = money.replace('$', '').replace(',', '').strip()
    try:
        return int(cleaned)
    except ValueError:
        return 0
