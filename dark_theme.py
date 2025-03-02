from Arc_API import arc_API

if __name__ == "__main__":
    arc_api = arc_API()
    arc_api.close_arc()
    arc_api.set_space_theme_color(0,"blendedSingleColor",[(0,0,0,1)],"dark")
    print(arc_api.get_number_of_spaces())
    arc_api.open_arc()
