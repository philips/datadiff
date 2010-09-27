from difflib import SequenceMatcher

def diff(a, b):
    if type(a) == type(b) == list:
        return diff_list(a, b)
    elif type(a) == type(b) == dict:
        return diff_dict(a, b)
    else:
        raise Exception("not implemented")

class DataDiff(object):
    
    def __init__(self, datatype, diffs):
        self.datatype = datatype
        self.diffs = diffs
    
    def __str__(self):
        output = []
        if self.datatype == list:
            output.append('[')
        else:
            raise Exception(self.datatype)
        for change, values in self.diffs:
            if change == 'delete':
                ch = '-'
            elif change == 'insert':
                ch = '+'
            elif change == 'equal':
                ch = ' '
            else:
                raise Exception(value)
            for value in values:
                output.append("%s%s," % (ch, value))
        if self.datatype == list:
            output.append(']')
        else:
            raise Exception(self.datatype)
        return '\n'.join(output)

def diff_list(a, b):
    sm = SequenceMatcher(a=a, b=b)
    diff = []
    for chunk in sm.get_grouped_opcodes():
        for change, i1, i2, j1, j2 in chunk:
            value = a[i1:i2]
            if change == 'replace':
                diff.append(('insert', a[i1:i2]))
                diff.append(('delete', b[j1:j2]))
            else:
                diff.append((change, value))
    return DataDiff(list, diff)

def diff_dict(a, b):
    pass

##
## gutenberg
##
def dict_diff(a, b):
    diff = {'first_dict_missing':{},'second_dict_missing':{},'different_values':{}}
    for key in b:
        if key not in a:
            diff['first_dict_missing'][key] = b[key]
        elif a[key] != b[key]:
            diff['different_values'][key] = (a[key], b[key])
    for key in a:
        if key not in b:
            diff['second_dict_missing'][key] = a[key]
    return diff

def list_diff(a,b):
    r = []
    for aa, bb in zip(a, b):
        if aa == bb:
            r.append('  ' + pformat(aa))
        elif pformat(aa) == pformat(bb):
            r.append('- ' + type(aa) + ' ' + aa)
            r.append('+ ' + type(bb) + ' ' + aa)
        else:
            r.append('- ' + pformat(aa))
            r.append('+ ' + pformat(bb))
    if len(a) > len(b):
        r += ['- ' + pformat(aa) for aa in a[len(b):]]
    if len(b) > len(a):
        r += ['- ' + pformat(bb) for bb in b[len(a):]]
    return '\n'.join(r)