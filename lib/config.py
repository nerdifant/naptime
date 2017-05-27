import os
import configparser

class config:
    def __init__ (self):
        self.cfg = configparser.ConfigParser()

    def read(self, path):
        if os.path.isfile(path):
            self.cfg.read(path)
            print("> Reading " + path + ".")
            return True
        else:
            print("> " + path + " not found!")
            return False

    def sections(self):
        sections = self.cfg.sections()
        return sections

    def map(self, section):
        dict1 = {}
        options = self.cfg.options(section)
        for option in options:
            try:
                dict1[option] = self.cfg.get(section, option)
                if dict1[option] == -1:
                    DebugPrint("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                dict1[option] = None
        return dict1
