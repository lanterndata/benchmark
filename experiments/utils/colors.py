from .constants import Extension

red_shades = [
    'rgb(255,153,153)',
    'rgb(255,102,102)',
    'rgb(255,51,51)',
    'rgb(255,0,0)',
    'rgb(204,0,0)',
    'rgb(153,0,0)',
]

orange_shades = [
    'rgb(255,204,153)',
    'rgb(255,178,102)',
    'rgb(255,152,51)',
    'rgb(255,128,0)',
    'rgb(204,102,0)',
    'rgb(153,76,0)',
]

green_shades = [
    'rgb(153,255,153)',
    'rgb(102,255,102)',
    'rgb(51,255,51)',
    'rgb(0,255,0)',
    'rgb(0,204,0)',
    'rgb(0,153,0)',
]

blue_shades = [
    'rgb(153,153,255)',
    'rgb(102,102,255)',
    'rgb(51,51,255)',
    'rgb(0,0,255)',
    'rgb(0,0,204)',
    'rgb(0,0,153)',
]

purple_shades = [
    'rgb(204,153,255)',
    'rgb(153,102,255)',
    'rgb(102,51,255)',
    'rgb(51,0,255)',
    'rgb(51,0,204)',
    'rgb(51,0,153)',
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
