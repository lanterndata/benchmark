from urllib.parse import urlparse

def convert_string_to_number(s):
    """
    Convert a string to a number. The string can end with 'k', 'm', or 'b',
    denoting thousands, millions, and billions, respectively.

    :param s: A string to convert to a number.
    :return: The converted number.
    """

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
        print(f"Could not convert {s} to a number.")
        return None

def convert_number_to_string(num):
    """
    Convert a number to a string. If the number is a multiple of 1000, it will 
    end with 'k'. If it's a multiple of 1000000, it will end with 'm'. And if 
    it's a multiple of 1000000000, it will end with 'b'.

    :param num: A number to convert to a string.
    :return: The converted string.
    """

    if num % 10**9 == 0:
        return str(int(num // 10**9)) + 'b'
    elif num % 10**6 == 0:
        return str(int(num // 10**6)) + 'm'
    elif num % 10**3 == 0:
        return str(int(num // 10**3)) + 'k'
    else:
        return str(int(num))

def convert_bytes_to_number(bytes):
    if 'kB' in bytes:
        return float(bytes.replace(' kB', '')) / 1024
    elif 'MB' in bytes:
        return float(bytes.replace(' MB', ''))
    else:
        return None
  
def extract_connection_params(db_url):
    parsed_url = urlparse(db_url)
    host = parsed_url.hostname
    port = parsed_url.port
    user = parsed_url.username
    password = parsed_url.password
    database = parsed_url.path.lstrip("/")

    return host, port, user, password, database