def print_row(*cols):
    row = ''.join([col.ljust(20) for col in cols])
    print(row)


def print_labels(*cols):
    print_row(*cols)
    print('-' * len(cols) * 20)


def get_title(extension, index_params, dataset, N=None):
    strings = [
        f"extension: {extension.value}",
        f"index params: {index_params}",
        f"dataset: {dataset.value}",
    ]
    if N:
        strings.append(f"N: {N}")
    return ', '.join(strings)
