import random
import os
import numpy as np
from scripts.game_structure.game_essentials import *

class Name():
    special_suffixes = {
        "kitten": "kit",
        "apprentice": "paw",
        "medicine cat apprentice": "paw",
        "leader": "star"
    }

    # Migrate this later
    """if os.path.exists('saves/prefixlist.txt'):
        with open('saves/prefixlist.txt', 'r') as read_file:
            name_list = read_file.read()
            if_names = len(name_list)
        if if_names > 0:
            new_names = name_list.split('\n')
            for new_name in new_names:
                if new_name != '':
                    normal_prefixes.append(new_name)

    if os.path.exists('saves/suffixlist.txt'):
        with open('saves/suffixlist.txt', 'r') as read_file:
            name_list = read_file.read()
            if_names = len(name_list)
        if if_names > 0:
            new_names = name_list.split('\n')
            for new_name in new_names:
                if new_name != '':
                    normal_suffixes.append(new_name)"""

    def __init__(self,
                 status="warrior",
                 prefix=None,
                 suffix=None):
        self.status = status
        self.prefix = prefix
        self.suffix = suffix
        
    def gen_name(self,
                 colour=None,
                 eyes=None,
                 pelt=None,
                 tortiepattern=None):
        if self.prefix is None:
            if game.langman:
                game.langman.load_name_db()
                
                # Get prefix category 
                if not random.getrandbits(3) and (eyes and colour): # Chance for True is '1/8'.
                    possible_prefix_categories = ["eye_prb_" + eyes, "col_prb_" + colour]
                    prefix_category = random.choice(possible_prefix_categories)
                else:
                    prefix_category = "std_pre_prb"  
                        
                # Get suffix category
                if pelt is None or pelt == 'SingleColour':
                    suffix_category = "std_suf_prb"
                else:
                    if not random.getrandbits(3):  # Chance for True is '1/8'.
                        if pelt in ["Tortie", "Calico"]:
                            suffix_category = "plt_prb_" + tortiepattern
                        else:
                            suffix_category = "plt_prb_" + pelt
                    else:
                        suffix_category = "std_suf_prb"
                
                name_query = np.array(game.langman.db_cursor.execute("SELECT name, {field} FROM NAMES WHERE {field} > 0".format(field=prefix_category)).fetchall())
                self.prefix = np.random.choice(name_query[:, 0], 1, p=name_query[:, 1].astype(np.float64))[0]
                while not self.suffix:
                    name_query = np.array(game.langman.db_cursor.execute("SELECT name, {field} FROM NAMES WHERE {field} > 0".format(field=suffix_category)).fetchall())
                    pot_suf = np.random.choice(name_query[:, 0], 1, p=name_query[:, 1].astype(np.float64))[0]
                    if pot_suf.lower() != self.prefix.lower():
                        self.suffix = pot_suf
                        
                game.langman.close_name_db()

    def __repr__(self):
        if self.status in ["deputy", "warrior", "medicine cat", "elder"]:
            return self.prefix + self.suffix
        else:
            return self.prefix + self.special_suffixes[self.status]


names = Name()
