def print_row(*cols):
    row = ''.join([col.ljust(10) for col in cols])
    print(row)

def print_labels(title, *cols):
    print_row(title)
    print('-' * len(cols) * 10)
    print_row(*cols)
    print('-' * len(cols) * 10)