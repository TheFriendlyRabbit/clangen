import random
import os
import numpy as np
from scripts.game_structure.game_essentials import *
import ujson
from scripts.housekeeping.datadir import get_save_dir

EQUIAVLENCIES = {"newborn": "kitten"}

class Name():
    # Migrate this later
    """if os.path.exists('resources/dicts/names/names.json'):
        with open('resources/dicts/names/names.json') as read_file:
            names_dict = ujson.loads(read_file.read())

        if os.path.exists(get_save_dir() + '/prefixlist.txt'):
            with open(get_save_dir() + '/prefixlist.txt', 'r') as read_file:
                name_list = read_file.read()
                if_names = len(name_list)
            if if_names > 0:
                new_names = name_list.split('\n')
                for new_name in new_names:
                    if new_name != '':
                        if new_name.startswith('-'):
                            while new_name[1:] in names_dict["normal_prefixes"]:
                                names_dict["normal_prefixes"].remove(new_name[1:])
                        else:
                            names_dict["normal_prefixes"].append(new_name)

        if os.path.exists(get_save_dir() + '/suffixlist.txt'):
            with open(get_save_dir() + '/suffixlist.txt', 'r') as read_file:
                name_list = read_file.read()
                if_names = len(name_list)
            if if_names > 0:
                new_names = name_list.split('\n')
                for new_name in new_names:
                    if new_name != '':
                        if new_name.startswith('-'):
                            while new_name[1:] in names_dict["normal_suffixes"]:
                                names_dict["normal_suffixes"].remove(new_name[1:])
                        else:
                            names_dict["normal_suffixes"].append(new_name)

        if os.path.exists(get_save_dir() + '/specialsuffixes.txt'):
            with open(get_save_dir() + '/specialsuffixes.txt', 'r') as read_file:
                name_list = read_file.read()
                if_names = len(name_list)
            if if_names > 0:
                new_names = name_list.split('\n')
                for new_name in new_names:
                    if new_name != '':
                        if new_name.startswith('-'):
                            del names_dict["special_suffixes"][new_name[1:]]
                        elif ':' in new_name:
                            _tmp = new_name.split(':')
                            names_dict["special_suffixes"][_tmp[0]] = _tmp[1]"""

    def __init__(self,
                 status="warrior",
                 prefix=None,
                 suffix=None,
                 colour=None,
                 eyes=None,
                 pelt=None,
                 tortiepattern=None,
                 biome=None,
                 specsuffix_hidden=False,
                 load_existing_name=False
                 ):
        self.status = status
        self.prefix = prefix
        self.suffix = suffix
        self.specsuffix_hidden = specsuffix_hidden
        self.localized = None
        self.last_lang = ""
        
        name_fixpref = False
        
        if game.langman:
            game.langman.load_name_db()
            col_names = self.fetch_cols()
            
            # Set prefix
            if self.prefix is None:
                self.give_prefix(eyes, colour, biome, col_names)
                # needed for random dice when we're changing the Prefix
                name_fixpref = True

            # Set suffix
            if self.suffix is None:
                self.give_suffix(pelt, biome, tortiepattern, col_names)
                if name_fixpref and self.prefix is None:
                    # needed for random dice when we're changing the Prefix
                    name_fixpref = False
                    
            #self.localized = game.langman.fetch_localized_name(self.prefix, self.suffix)
            self.last_lang = game.langman.current_lang
            game.langman.close_name_db()
        
    def fetch_cols(self):
        return [col[0] for col in game.langman.db_cursor.execute("SELECT * FROM NAMES").description]
        
    def query_category(self, category):
        print(f"Querying {category}")
        name_query = np.array(game.langman.db_cursor.execute("SELECT name, loc, locgender, {field} FROM NAMES WHERE {field} > 0".format(field=category)).fetchall())
        return np.random.choice(name_query[:, 0], 1, p=name_query[:, 3].astype(np.float64))[0]

    # Generate possible prefix
    def give_prefix(self, eyes, colour, biome, col_names):
        possible_prefix_categories = []
        
        if game.config["cat_name_controls"]["always_name_after_appearance"] or not random.getrandbits(2):
            # Named after appearance. 1/4 chance if the setting is off.
            if eyes and game.config["cat_name_controls"]["allow_eye_names"] and "eye_brb_" + eyes in col_names:
                possible_prefix_categories.append("eye_prb_" + eyes)
            if colour and "col_prb_" + colour in col_names: possible_prefix_categories.append("col_prb_" + colour)
        elif not random.getrandbits(3) and biome and "biome_pre_prb_" + biome in col_names:
            # Named after biome. 1/8 chance.
            possible_prefix_categories = ["biome_pre_prb_" + biome,]
        
        if not possible_prefix_categories: possible_prefix_categories = ["std_pre_prb",]
            
        prefix_category = random.choice(possible_prefix_categories)
        self.prefix = self.query_category(prefix_category)
            
    def give_suffix(self, pelt, biome, tortiepattern, col_names):
        self.suffix = None
        
        # Get suffix category
        if pelt is None or pelt == 'SingleColour':
            suffix_category = "std_suf_prb"
        else:
            if not random.getrandbits(3):
                # Named after appearance. 1/8 chance.
                if pelt in ["Tortie", "Calico"] and "plt_prb_tort_" + tortiepattern in col_names:
                    suffix_category = "plt_prb_tort_" + tortiepattern
                elif "plt_prb_" + pelt in col_names:
                    suffix_category = "plt_prb_" + pelt
            else:
                suffix_category = "std_suf_prb"
                
        if suffix_category == "std_suf_prb" and not random.getrandbits(3) and biome and "biome_suf_prb_" + biome in col_names:
            suffix_category = "biome_suf_prb_" + biome
        
        if suffix_category not in col_names: suffix_category = "std_suf_prb"
        
        while not self.suffix:
            pot_suf = self.query_category(suffix_category)
            if pot_suf.lower() != self.prefix.lower():
                self.suffix = pot_suf

    def __repr__(self):
        if self.localized and self.last_lang == game.langman.current_lang:
            return self.localized
        else:
            if game.langman:
                self.last_lang = game.langman.current_lang
                if self.status not in ["deputy", "warrior", "medicine cat", "elder", "mediator", "mediator apprentice"] and not self.specsuffix_hidden:
                    if self.status in EQUIAVLENCIES:
                        return game.langman.fetch_localized_name(self.prefix, self.suffix, EQUIAVLENCIES[self.status])
                    return game.langman.fetch_localized_name(self.prefix, self.suffix, self.status)
                else:
                    if game.config['fun']['april_fools']:
                        return game.langman.fetch_localized_name(self.prefix, "egg")
                    return game.langman.fetch_localized_name(self.prefix, self.suffix)
            else:
                print("No language manager! Falling back on default concatentation...")
                return self.prefix + self.suffix
                
                
                

# MIGRATE LATER
"""
    if self.suffix and not load_existing_name:
        # Prevent triple letter names from joining prefix and suffix from occuring (ex. Beeeye)
        triple_letter = False
        possible_three_letter = (self.prefix[-2:] + self.suffix[0], self.prefix[-1] + self.suffix[:2])
        if all(i == possible_three_letter[0][0] for i in possible_three_letter[0]) or \
                all(i == possible_three_letter[1][0] for i in possible_three_letter[1]):
            triple_letter = True
        # Prevent double animal names (ex. Spiderfalcon)
        double_animal = False
        if self.prefix in self.names_dict["animal_prefixes"] and self.suffix in self.names_dict["animal_suffixes"]:
            double_animal = True
        # Prevent the inappropriate names
        nono_name = self.prefix + self.suffix
        # Prevent double names (ex. Iceice)
        # Prevent suffixes containing the prefix (ex. Butterflyfly)
        
        i = 0
        while nono_name.lower() in self.names_dict["inappropriate_names"] or triple_letter or double_animal or \
                self.suffix.lower() == self.prefix.lower() or (self.suffix.lower() in self.prefix.lower() and not str(self.suffix) == ''):

            # check if random die was for prefix
            if name_fixpref:
                self.give_prefix(eyes, colour, biome)
            else:
                self.give_suffix(pelt, biome, tortiepattern)

            nono_name = self.prefix + self.suffix
            possible_three_letter = (self.prefix[-2:] + self.suffix[0], self.prefix[-1] + self.suffix[:2])
            if not (all(i == possible_three_letter[0][0] for i in possible_three_letter[0]) or \
                    all(i == possible_three_letter[1][0] for i in possible_three_letter[1])):
                triple_letter = False
            if not (self.prefix in self.names_dict["animal_prefixes"] and self.suffix in self.names_dict[
                "animal_suffixes"]):
                double_animal = False
            i += 1
        # Handles predefined suffixes (such as newborns being kit), then suffixes based on ages (fixes #2004, just trust me)
        if self.status in self.names_dict["special_suffixes"] and not self.specsuffix_hidden:
            return self.prefix + self.names_dict["special_suffixes"][self.status]
        if game.config['fun']['april_fools']:
            return self.prefix + 'egg'
        return self.prefix + self.suffix
"""


names = Name()
