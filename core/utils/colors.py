from .constants import Extension

red_shades = [
    'rgb(255,153,153)',
    'rgb(204,0,0)',
]

orange_shades = [
    'rgb(255,204,153)',
    'rgb(204,102,0)',
]

green_shades = [
    'rgb(153,255,153)',
    'rgb(0,204,0)',
]

blue_shades = [
    'rgb(153,153,255)',
    'rgb(0,0,204)',
]

purple_shades = [
    'rgb(204,153,255)',
    'rgb(51,0,204)',
]


def get_color_from_extension(extension: Extension, index=0):
    if extension == Extension.LANTERN:
        return green_shades[index]
    elif extension == Extension.PGVECTOR_IVFFLAT:
        return orange_shades[index]
    elif extension == Extension.PGVECTOR_HNSW:
        return blue_shades[index]
    elif extension == Extension.NEON:
        return purple_shades[index]
    else:
        return red_shades[index]


def get_transparent_color(color: str):
    return 'rgba' + color[3:-1] + f",0.3)"
