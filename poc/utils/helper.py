import configparser, ast


class ConfigsParser:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.file = './config/config.ini'

    def get(self, section, options):
        try:
            self.config.read(self.file, encoding='utf-8')
            return ast.literal_eval(self.config.get(section, options))
        except configparser.NoOptionError:
            print("can't find key in config.ini")




