from tkinter import *
from tkinter import colorchooser, messagebox
import os, json, psutil

def setting_wrapper_function(func):
    def inner_wrapper(self, *args, **kwargs):
        if self.arc_open_check():
            return "Arc_process_running"
        result = func(self, *args, **kwargs)
        self.update_json()
        self.parse_spaces()
        return result
    return inner_wrapper

class arc_API:
    def __init__(self):
        # in the future, if the app ever comes to linux, this might need to use the `platform` library to differentiate from Mac and Linux, but this should be fine for now
        isWindows = os.name == "nt"
        path_separator = '\\' if isWindows else '/'

        path = path_separator.join((os.getenv("LOCALAPPDATA"), "Packages")) if isWindows else path_separator.join((os.getenv("HOME"), "Library", "Application Support"))
        dirs = os.listdir(path)

        arc_path = 
        # if not Mac, use Windows paths
        if isWindows:
            for dir in dirs:
                if not os.path.isfile(dir):
                    if "TheBrowserCompany" in dir:
                        arc_path = path_separator.join((os.path.join(path, dir), "LocalCache", "Local"))

        self.arc_theme_file = path_separator.join((arc_path, "Arc", "StorableSidebar.json"))
        self.data = ""
        with open(self.arc_theme_file, 'r', encoding='utf-8') as f:
            self.data = json.loads(f.read())
        self.spaces_data = []
        self.parse_spaces()

    def parse_spaces(self,):
        json_data = self.data["sidebar"]["containers"][1]
        index_proper = 0 
        self.spaces_data = []
        for index, i in enumerate(json_data["spaces"]):
            if index % 2 != 0:  # Check if the number is odd
                space_theme = None
                space_theme_data = None
                if 'windowTheme' not in i["customInfo"]:
                    #print("empty_theme")
                    #print("AAAAAA:",i)
                    space_theme = None
                    space_theme_data = None

                elif 'blendedSingleColor' in i["customInfo"]['windowTheme']["background"]["single"]["_0"]["style"]["color"]["_0"]:
                    #print("has blendedSingleColor")
                    space_theme = "blendedSingleColor"
                    space_theme_data = i["customInfo"]['windowTheme']["background"]["single"]["_0"]["style"]["color"]["_0"]

                elif 'blendedGradient' in i["customInfo"]['windowTheme']["background"]["single"]["_0"]["style"]["color"]["_0"]:
                    #print("has blendedGradient")
                    space_theme = "blendedGradient"
                    space_theme_data = i["customInfo"]['windowTheme']["background"]["single"]["_0"]["style"]["color"]["_0"]
                
                if "iconType" in i["customInfo"]:
                        #print("has icon")
                        icon = i["customInfo"]['iconType']

                elif "iconType" not in i["customInfo"]:
                        #print("has no icon")
                        icon = None

                data = {"space_id": index_proper,
                    "space_name":i['title'],
                    "space_theme_type":space_theme,
                    "space_theme_data": space_theme_data,
                    "space_icon":icon,
                    }
                
                self.spaces_data.append(data)
                index_proper +=1
        
        return self.spaces_data
    def set_space_theme_color(self,space_id, type, rgba,mode, noiseFactor=0.3,intensityFactor=0.1,):
        if self.get_space_theme_type(space_id) != None:
            if isinstance(rgba, tuple):
                rgba = [rgba]
            self.gradientData = self.data["sidebar"]["containers"][1]["spaces"][self.index_json_index(space_id)]["customInfo"]["windowTheme"]["background"]["single"]["_0"]["style"]["color"]["_0"]
            if type == "blendedGradient":
                colors = []
                for color in rgba:
                    colors.append({"red": color[0] / 255 , "green": color[1] / 255 , "blue": color[2] / 255 , "alpha": color[3], "colorSpace": "extendedSRGB"},)
                print(colors)
                if (not "blendedGradient" in self.gradientData):
                    self.gradientData["blendedGradient"] = self.gradientData.pop("blendedSingleColor")
                
                self.gradientData["blendedGradient"]["_0"] = {
                    "overlayColors": [],
                    "translucencyStyle": mode,
                    "wheel": {
                    "complimentary": {}
                    },
                    "baseColors": colors,
                    "modifiers": {"intensityFactor": intensityFactor, "overlay": "grain", "noiseFactor": noiseFactor}
                }
            if type == "blendedSingleColor":
                r,g,b,a = rgba[0]
                if (not "blendedSingleColor" in self.gradientData):
                    self.gradientData["blendedSingleColor"] = self.gradientData.pop("blendedGradient")
                self.gradientData["blendedSingleColor"]["_0"] = {
                    "color": {
                    "alpha" : a,
                    "green" : r,
                    "blue" : g,
                    "red" : b,
                    "colorSpace" : "extendedSRGB"
                    },
                    "modifiers" : {
                    "overlay" : "sand",
                    "noiseFactor" : 1,
                    "intensityFactor" : 1
                    },
                    "translucencyStyle" : mode
                }
            print("aaasdf")
            self.update_json()
        else:
            print("blank space. could not set!")
    def json_index_to_index(self, json_index):
        proper_index = json_index + (json_index - 1)
        return proper_index

    def index_json_index(self, json_index):
        proper_index = json_index + (json_index + 1)
        return proper_index

    def update_json(self):
        with open(self.arc_theme_file, "w", encoding='utf-8') as fi:
            fi.write(json.dumps(self.data))

    def get_number_of_spaces(self):
        return len(self.spaces_data)

    def get_space_name(self, space_id):
        if space_id < self.get_number_of_spaces():
            return self.spaces_data[space_id]['space_name']

    def get_space_theme_type(self, space_id):
        if space_id < self.get_number_of_spaces():
            return self.spaces_data[space_id]['space_theme_type']

    def get_space_theme_data(self, space_id):
        if space_id < self.get_number_of_spaces():
            return self.spaces_data[space_id]['space_theme_data']
        
    @setting_wrapper_function
    def set_space_name(self, space_id, space_name):
        if space_id < self.get_number_of_spaces():
            space_id = self.index_json_index(space_id)
            self.data["sidebar"]["containers"][1]["spaces"][space_id]['title'] = str(space_name)


    @setting_wrapper_function
    def set_space_icon(self, space_id, icon):
        if space_id < self.get_number_of_spaces():
            space_id = self.index_json_index(space_id)
            self.data["sidebar"]["containers"][1]["spaces"][space_id]["customInfo"]['iconType'] = {'emoji_v2': icon, 'emoji': 0}

    def arc_open_check(self):
        if "Arc.exe" in (p.name() for p in psutil.process_iter()):
            print("Arc is still open! In order to change your theme, please close Arc and try again.")
            return True
        return False


if __name__ == "__main__":
    arc_api = arc_API()
    arc_api.set_space_theme_color(0,"blendedSingleColor",[(255,0,255,1),(0,255,0,1)])
    print(arc_api.get_number_of_spaces())
    arc_api.set_space_name(0, "aaaaaaaaaaaaaaaaaaaaaaaaa")
    arc_api.set_space_icon(0, '😍')
    print(arc_api.get_space_name(0))
    print(arc_api.get_space_theme_type(0))
    print(arc_api.get_space_theme_data(0))
