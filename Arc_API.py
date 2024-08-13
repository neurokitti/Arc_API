from tkinter import *
from tkinter import colorchooser, messagebox
import os, json, psutil
import subprocess
import time

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
        # following is useful for compatibility with MacOS
        self.isWindows = os.name == "nt"
        path_separator = '\\' if self.isWindows else '/'
        # use join function for easier string manipulation + performance
        path = path_separator.join((os.getenv("LOCALAPPDATA"), "Packages")) if self.isWindows else path_separator.join((os.getenv("HOME"), "Library", "Application Support"))
        dirs = os.listdir(path)
        arc_path = path
        # if not Mac, use Windows paths
        if self.isWindows:
            for dir in dirs:
                if not os.path.isfile(dir):
                    if "TheBrowserCompany" in dir:
                        arc_path = path_separator.join((os.path.join(path, dir), "LocalCache", "Local"))
        # finalize true Arc path
        arc_path = path_separator.join((arc_path, "Arc"))
        self.arc_theme_file = path_separator.join((arc_path, "StorableSidebar.json"))
        self.arc_executable = "Arc.exe" if self.isWindows else "Arc"
        self.data = ""
        with open(self.arc_theme_file, 'r', encoding='utf-8') as f:
            self.data = json.loads(f.read())
        self.spaces_data = []
        self.parse_spaces()
    def parse_spaces(self,):
        json_data = self.data["sidebar"]["containers"][1]
        index_proper = 0 
        self.spaces_data = []
        for index, space_data in enumerate(json_data["spaces"]):
            if index % 2 != 0:  # Check if the number is odd
                space_name = None
                space_theme = None
                space_theme_data = None
                if 'windowTheme' not in space_data["customInfo"]:
                    #print("empty_theme")
                    #print("AAAAAA:",space_data)
                    space_theme = None
                    space_theme_data = None
                elif 'blendedSingleColor' in space_data["customInfo"]['windowTheme']["background"]["single"]["_0"]["style"]["color"]["_0"]:
                    #print("has blendedSingleColor")
                    space_theme = "blendedSingleColor"
                    space_theme_data = space_data["customInfo"]['windowTheme']["background"]["single"]["_0"]["style"]["color"]["_0"]
                elif 'blendedGradient' in space_data["customInfo"]['windowTheme']["background"]["single"]["_0"]["style"]["color"]["_0"]:
                    #print("has blendedGradient")
                    space_theme = "blendedGradient"
                    space_theme_data = space_data["customInfo"]['windowTheme']["background"]["single"]["_0"]["style"]["color"]["_0"]
                
                if "iconType" in space_data["customInfo"]:
                    #print("has icon")
                    icon = space_data["customInfo"]['iconType']
                elif "iconType" not in space_data["customInfo"]:
                    #print("has no icon")
                    icon = None

                if "title" in space_data:
                    # only if space has a name
                    space_name = space_data['title']

                data = {"space_id": index_proper,
                    "space_name": space_name,
                    "space_theme_type": space_theme,
                    "space_theme_data": space_theme_data,
                    "space_icon": icon,
                    }
                    
                
                self.spaces_data.append(data)
                index_proper +=1
        
        return self.spaces_data
    def set_space_theme_color(self,space_id, type, rgba,mode, noiseFactor=0.3,intensityFactor=0.1,):
        print(rgba)
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
                print("A:",a)
                print("b:",b)
                print("g:",g)
                print("r:",r)
                if (not "blendedSingleColor" in self.gradientData):
                    self.gradientData["blendedSingleColor"] = self.gradientData.pop("blendedGradient")
                self.gradientData["blendedSingleColor"]["_0"] = {
                    "color": {
                    "alpha" : a,
                    "green" : g / 255,
                    "blue" : b / 255,
                    "red" : r / 255,
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
        if self.arc_executable in (p.name() for p in psutil.process_iter()):
            print("Arc is still open! In order to change your theme, please close Arc and try again.")
            return True
        return False
    def is_application_running(self,app_name):
        """
        Check if a process with the given name is running.
        
        :param app_name: The name of the application/process to check (e.g., 'notepad.exe').
        :return: True if the application is running, False otherwise.
        """
        for process in psutil.process_iter(['name']):
            #print(process.info['name'])
            if process.info['name'] == app_name:
                return True

        return False
    def close_arc(self,):
        if self.isWindows:
            subprocess.Popen(f"TASKKILL /IM {self.arc_executable}", shell=True)
        else:
            subprocess.Popen(f"osascript -e 'quit app \"{self.arc_executable}\"'", shell=True)
        print("start")
        while self.is_application_running(self.arc_executable):
            time.sleep(0.1)
        print("done")

    def kill_arc(self,):
        if self.isWindows:
            subprocess.call(f"TASKKILL /F /IM {self.arc_executable}", shell=True)
        else:
            subprocess.Popen(f"pkill -x {self.arc_executable}", shell=True)


    def open_arc(self,):
        if self.isWindows:
            subprocess.Popen(self.arc_executable, shell=True)
        else:
            subprocess.Popen(f"osascript -e 'tell application \"{self.arc_executable}\" to activate'", shell=True)
