green_shades = [
  'rgb(153,255,153)', 
  'rgb(102,255,102)',  
  'rgb(51,255,51)',  
  'rgb(0,255,0)',
  'rgb(0,204,0)',  
  'rgb(0,153,0)',  
]

red_shades = [
  'rgb(255,153,153)',  
  'rgb(255,102,102)',  
  'rgb(255,51,51)',  
  'rgb(255,0,0)',
  'rgb(204,0,0)',  
  'rgb(153,0,0)',
]

blue_shades = [
  'rgb(153,153,255)',
  'rgb(102,102,255)',
  'rgb(51,51,255)',
  'rgb(0,0,255)',
  'rgb(0,0,204)',
  'rgb(0,0,153)',
]

def get_color_from_extension(extension, index=0):
  if extension == 'lantern':
      return green_shades[index]
  elif extension == 'pgvector':
      return blue_shades[index]
  else:
      return red_shades[index]