init -10 python:
    bg_day = False #Changed by '01bg.rpy', if the current BG has day/high light
    s_ypos = 0
    
    if not persistent.customization:
        persistent.customization = {
            'hair': 'usual', # Hair Style
            'body': 'school', # Body Style
            'asec_head': None, # Head accessory (e.g. glasses)
        }

    import re
    
    MOD_IMAGES_PATH = 'mod_assets/images'
    
    
    EXP_PATHS = {
        0: "s_new/body",
        1: "s_new/skin",
        2: "s_new/mouth",
        3: "s_new/eyes",
        4: "s_new/brows"
    }
    
    CUSTOM_PATHS = {
        'hair': "s_new/hair"
    }
    
    def get_asset_path(part, file = 'a', paths = EXP_PATHS, day = False):
        """Part codes:
            0 = body
            1 = skin modification
            2 = mouth
            3 = eyes
            4 = eyebrows
        """
        if day:
            file += "_d"
            path = "%s/%s/%s.png" % (MOD_IMAGES_PATH, paths[part], file)
            try:
                f = renpy.file(path)
                f.close()
                return path
            except:
                file = file[:-2]
        return "%s/%s/%s.png" % (MOD_IMAGES_PATH, paths[part], file)
    
    def l_range(t, *args):
        """Creates a letter list. Uses a range()-like agrument syntax."""
        al = len(args)
        f = 97
        s = args[1] if al > 1 else 1
        
        if al == 0:
            t = ord(t)
        else:
            f, t = ord(t), ord(args[0])
        
        return [chr(x) for x in range(f, t, s)]
    
    #Sprite Info Classes
    class SpriteInfo:
        def __init__(self, part, filename, pos, size = None, paths = EXP_PATHS, day = None):
            self.path = get_asset_path(part, filename, paths)
            self.path_day = day or get_asset_path(part, filename, paths, True)
            self.pos = pos
            self.size = size
        
        def __str__(self):
            return str(self.pos) + ', "%s"' % self.path
    
    class DummySprite(SpriteInfo):
        def __init__(self):
            self.path = ""
            self.pos = (0, 0)
            self.size = (0, 0)

    
    exp_codes = [{}, {}, {}, {}] ## Updated by sprites.rpy
    
    CUSTOM_TEMPLATES = {
        'hair': {},
        'hair_front': {},
        'hair_back': {}
    }
    
    def get_custom(t, name):
        if not (t is None or name is None):
            return CUSTOM_TEMPLATES[t].get(name)
    
    class Body:
        def __init__(self, back, front = None):
            self.back = back
            self.front = front or []
        
        def add_front(self, sprite):
            self.front.append(sprite)
        
        def get_composite(self, exp_code = "", custom_dict = {}, day = False):
            global s_ypos
            
            comp_arg = [(self.back.size[0], 720), self.back.pos, self.back.path]
            offset = list(self.back.pos)
            
            #hair
            hair = get_custom('hair', custom_dict.get('hair'))
            hair_front = get_custom('hair_front', custom_dict.get('hair'))
            hair_back = get_custom('hair_back', custom_dict.get('hair'))
            hair_layers = [hair_back, hair, hair_front]
            
            for h in hair_layers:
                if h:
                    h = h[0]
                    if h.pos[1] < offset[1]:
                        offset[1] = -h.pos[1]
            
            if day:
                comp_arg[2] = self.back.path_day
            
            
            for i in range(len(exp_code)):
                exp = exp_codes[i][exp_code[i]]
                if len(exp.path):
                    pos = (exp.pos[0] + offset[0], exp.pos[1] + offset[1])
                    comp_arg.append(pos)
                    if day:
                        comp_arg.append(exp.path_day)
                    else:
                        comp_arg.append(exp.path)
            for i in self.front:
                if len(i.path):
                    pos = (i.pos[0] + offset[0], i.pos[1] + offset[1])
                    comp_arg.append(pos)
                    if day:
                        comp_arg.append(i.path_day)
                    else:
                        comp_arg.append(i.path)
            
            for i in range(2):
                if hair_layers[i]:
                    h = hair_layers[i][0]
                    comp_arg.insert(1 + i * 2, (h.pos[0], 0))
                    if day:
                        comp_arg.insert((1 + i) * 2, h.path_day)
                    else:
                        comp_arg.insert((1 + i) * 2, h.path)
            
            if hair_front:
                last = 0
                if len(self.front):
                    last = len(comp_arg) - 3
                    last -= len(self.front)
                else:
                    last = len(comp_arg)
                
                hair_front = hair_front[0]
                
                #comp_arg.insert(last, (hair_front.pos[0], 0))
                #if day:
                    #comp_arg.insert(last + 1, hair_front.path_day)
                #else:
                    #comp_arg.insert(last + 1, hair_front.path)
            
            comp_arg[0] = (comp_arg[0][0] + offset[0], comp_arg[0][1] + offset[1])
            comp_arg[1] = (comp_arg[1][0] + offset[0], comp_arg[1][1] + offset[1])
            s_ypos = -offset[1]
            return im.Composite(*comp_arg)
        
        def dyn_d(self, exp):
            def f(st, at):
                if bg_day:
                    return self.get_composite(exp, persistent.customization, True), None
                return self.get_composite(exp, persistent.customization), None

            return DynamicDisplayable(f)
         
    bodies = {} ## Updated by new_exp.rpy

init -8 python: ## new_exp.rpy code must have order -10<x<-8
    exps = []
    try:
        f = renpy.file('exp.txt')
        for line in f.readlines():
            limit = re.search('\s', line)
            limit = limit and limit.start() or len(line)
            exps.append(line[:limit])
        f.close()
    except:
        for body in bodies:
            for s in exp_codes[0]:
                for m in exp_codes[1]:
                    for e in exp_codes[2]:
                        for b in exp_codes[3]:
                            exps.append(body+s+m+e+b)
    
    for exp in exps:
        dl = len(exp) - 4
        body = exp[:dl]
        renpy.image("sayori "+ exp, bodies[body].dyn_d(exp[dl:]))
