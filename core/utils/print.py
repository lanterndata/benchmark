def print_row(*cols):
    row = ''.join([col.ljust(19) for col in cols])
    print(row)


def print_labels(*cols):
    print_row(*cols)
    print('-' * len(cols) * 19)


def get_title(extension, index_params, dataset, N=None, bulk=False):
    strings = [
        f"extension: {extension.value}",
        f"index params: {index_params}",
        f"dataset: {dataset.value}",
        f"bulk: {bulk}",
    ]
    if N:
        strings.append(f"N: {N}")
    return ', '.join(strings)
