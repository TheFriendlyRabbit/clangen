import json
import sqlite3

LANG_DICT = {\
             'english': 'en',
             'spanish': 'es',
             'german': 'de',
             'french': 'fr'
            }

LANG_CALLBACKS = ["es", "fr"]

class LanguageManager():
    language_json = ""
    current_lang = ""
    
    name_db = None
    db_cursor = None
    
    def __init__(self, game):
        self.reload_lang(game.settings['language'])
        self.current_lang = LANG_DICT[game.settings['language']]
            
    def reload_lang(self, language):
        with open("languages/" + LANG_DICT[language] + ".json", mode="r", encoding="utf-8") as f:
            self.language_json = json.load(f)
        with open("languages/name/" + LANG_DICT[language] + ".json", mode="r", encoding="utf-8") as f:
            loc_names = json.load(f)
        self.load_name_db()
        for name, metadata in loc_names.items():
            if "locgender" in metadata.keys():
                self.db_cursor.execute("UPDATE NAMES set loc=?, locgender=? WHERE name=?", (metadata["loc"], metadata["locgender"], name))
            else:
                self.db_cursor.execute("UPDATE NAMES set loc=? WHERE name=?", (metadata["loc"], name))
        self.name_db.commit()
        self.close_name_db()
        
    def localize(self, dict_str, lookup_str):
        if not dict_str in self.language_json:
            return "INVALID LOOKUP DICT"
        if not lookup_str in self.language_json[dict_str]:
            return "INVALID DICT KEY"
        return self.language_json[dict_str][lookup_str]
        
    def fetch_table(self, dict_str):
        return self.language_json[dict_str]
        
    def load_name_db(self):
        self.name_db = sqlite3.connect("languages/names.db")
        self.db_cursor = self.name_db.cursor()
        
    def close_name_db(self):
        self.name_db.close()
        
    def fetch_localized_name(self, prefix, suffix, status=None):
        self.load_name_db()
        pref_loc = self.db_cursor.execute("SELECT loc, locgender FROM NAMES WHERE name==?", [prefix]).fetchone()
        if not status:
            suf_loc = self.db_cursor.execute("SELECT loc, locgender FROM NAMES WHERE name==?", [suffix]).fetchone()
        else:
            suf_loc = self.localize("NAME.SPECIAL_SUFFIX", status)
        self.close_name_db()
        if self.current_lang not in LANG_CALLBACKS:
            return pref_loc[0] + (suf_loc if status else suf_loc[0])
        else:
            try:
                return getattr(self, "lang_name_callback_" + self.current_lang)
            except:
                print("Woah! You tried to run special localization on a language that doesn't support it. Falling back to default concatenation...")
                return pref_loc[0] + (suf_loc if status else suf_loc[0])
        