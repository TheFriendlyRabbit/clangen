import json

LANG_DICT = {\
             'english': 'en',
             'spanish': 'es',
             'german': 'de'
            }

class LanguageManager():
    language_json = ""
    
    def __init__(self, game):
        self.reload_lang(game.settings['language'])
            
    def reload_lang(self, language):
        with open("languages/" + LANG_DICT[language] + ".json", mode="r", encoding="utf-8") as f:
            self.language_json = json.load(f)
        
    def localize(self, dict_str, lookup_str):
        if not dict_str in self.language_json:
            return "INVALID LOOKUP DICT"
        if not lookup_str in self.language_json[dict_str]:
            return "INVALID DICT KEY"
        return self.language_json[dict_str][lookup_str]
        
    def fetch_table(self, dict_str):
        return self.language_json[dict_str]
        