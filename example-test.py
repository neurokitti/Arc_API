from Arc_API import arc_API

if __name__ == "__main__":
    arc_api = arc_API()
    arc_api.close_arc()
    arc_api.set_space_theme_color(0,"blendedSingleColor",[(0,0,255,1)],"light")
    print(arc_api.get_number_of_spaces())
    arc_api.set_space_name(0, "aaaaaaaaaaaaaaaaaaaaaaaaa")
    arc_api.set_space_icon(0, '😍')
    print(arc_api.get_space_name(0))
    print(arc_api.get_space_theme_type(0))
    print(arc_api.get_space_theme_data(0))
    arc_api.open_arc()
