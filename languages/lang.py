import json

class LanguageManager():
    # obv a way of changing this eventually, but for now
    CURRENT_LANG = 'en'
    
    language_json = ""
    
    def __init__(self):
        with open("languages/" + self.CURRENT_LANG + ".json", mode="r", encoding="utf-8") as f:
            self.language_json = json.load(f)
        
    def localize(self, dict_str, lookup_str):
        if not dict_str in self.language_json:
            return "INVALID LOOKUP DICT"
        if not lookup_str in self.language_json[dict_str]:
            return "INVALID DICT KEY"
        return self.language_json[dict_str][lookup_str]
        
    def fetch_table(self, dict_str):
        return self.language_json[dict_str]
        