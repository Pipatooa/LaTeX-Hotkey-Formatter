import font_manager

# font_info = font_manager.FontInfo(('Whitney Light', 'HelveticaNeue', 'Helvetica', 'Arial', None))
font_info = font_manager.FontInfo(None)

print(font_info.get_text_width("—⎭"))

font_info.font.glyphs["—"].save("dash.png")
font_info.font.glyphs["⎭"].save("bar.png")
