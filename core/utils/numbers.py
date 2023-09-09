import logging


def convert_string_to_number(s):
    s = s.strip().lower()  # remove spaces and convert to lowercase

    multiplier = 1  # default is 1
    if s.endswith('k'):
        multiplier = 10**3
        s = s[:-1]  # remove the last character
    elif s.endswith('m'):
        multiplier = 10**6
        s = s[:-1]
    elif s.endswith('b'):
        multiplier = 10**9
        s = s[:-1]

    try:
        return int(float(s) * multiplier)
    except ValueError:
        logging.error(f"Could not convert {s} to a number.")
        return None


def convert_number_to_string(num):
    if num % 10**9 == 0:
        return str(int(num // 10**9)) + 'b'
    elif num % 10**6 == 0:
        return str(int(num // 10**6)) + 'm'
    elif num % 10**3 == 0:
        return str(int(num // 10**3)) + 'k'
    else:
        return str(int(num))


def convert_number_to_bytes(num):
    if num > 2**20:
        return f"{(num // 2**20):.2f} MiB"
    elif num > 2**10:
        return f"{(num // 2**10):.2f} MiB"
    else:
        return str(int(num)) + ' B'
