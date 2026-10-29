from source_builder import write
C='memory-independent'
write(1,'span-fusion',C,'Input is a list of [start,end] integer half-open spans. Reject reversed endpoints. Omit empty spans. Sort by start then end and merge overlaps AND touching spans. Return sorted disjoint spans.', '''
def solve(data):
    prepared = []
    for span in sequence(data):
        pair = sequence(span)
        if len(pair) != 2:
            raise ValueError("two endpoints required")
        start, end = (integer(v) for v in pair)
        if start > end:
            raise ValueError("reversed span")
        if start != end:
            prepared.append([start, end])
    result = []
    for start, end in sorted(prepared):
        if result and start <= result[-1][1]:
            result[-1][1] = max(result[-1][1], end)
        else:
            result.append([start, end])
    return result
''', [([],[]),([[3,6],[1,3],[9,9],[5,8]],[[1,8]]),([[0,10],[2,3],[12,14]],[[0,10],[12,14]]),([[-4,-2],[-2,0]],[[-4,0]])], [([[1,2]],[[1,2]])], [[[2,1]],[[True,2]]], [('start <= result[-1][1]','start < result[-1][1]'),('max(result[-1][1], end)','end'),('if start != end:','if start <= end:')])
write(2,'dependency-order',C,'Input maps string node names to lists of prerequisite names. All prerequisite names must be declared. Return a topological order, always choosing the lexicographically smallest currently ready node. Duplicate prerequisites have no extra effect. Reject cycles and unknown names.', '''
def solve(data):
    graph = mapping(data)
    pending = {}
    for node, dependencies in graph.items():
        text(node)
        pending[node] = {text(v) for v in sequence(dependencies)}
        if not pending[node] <= graph.keys():
            raise ValueError("unknown prerequisite")
    order = []
    while pending:
        ready = sorted(node for node, deps in pending.items() if not deps)
        if not ready:
            raise ValueError("cycle")
        node = ready[0]
        order.append(node)
        del pending[node]
        for deps in pending.values():
            deps.discard(node)
    return order
''', [({},[]),({'b':[],'a':[]},['a','b']),({'a':['b','b'],'b':[],'c':[]},['b','a','c']),({'x':['y'],'y':['z'],'z':[]},['z','y','x'])], [({'a':[]},['a'])], [{'a':['b']},{'a':['a']}], [('node = ready[0]','node = ready[-1]'),('deps.discard(node)','deps.clear()'),('pending[node] = {text(v) for v in sequence(dependencies)}','pending[node] = set()')])
write(3,'escaped-fields',C,'Input is a string of fields delimited by vertical bars. Backslash escapes exactly the next character, whether bar, backslash, or any other character. Preserve empty and trailing fields. Return decoded fields. Reject a trailing unpaired backslash.', r'''
def solve(data):
    fields = []
    current = []
    escaped = False
    for char in text(data):
        if escaped:
            current.append(char)
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == "|":
            fields.append("".join(current))
            current = []
        else:
            current.append(char)
    if escaped:
        raise ValueError("unfinished escape")
    fields.append("".join(current))
    return fields
''', [('', ['']),('a|',['a','']),('a\\|b|c',['a|b','c']),('x\\\\|y',['x\\','y']),('||',['','',''])], [('a|b',['a','b'])], ['a\\'], [('fields.append("".join(current))\n    return fields','if current:\n        fields.append("".join(current))\n    return fields'),('current.append(char)\n            escaped = False','current.extend(["\\\\", char])\n            escaped = False'),('if escaped:\n        raise ValueError("unfinished escape")','if escaped:\n        current.append("\\\\")')])
write(4,'adjacent-runs',C,'Input is a list of strings. Return [token,count] pairs for maximal consecutive equal runs. Empty input returns []. Equality is case sensitive. Tokens separated by another token form separate runs. Preserve spelling.', '''
def solve(data):
    tokens = [text(value) for value in sequence(data)]
    runs = []
    for token in tokens:
        if runs and runs[-1][0] == token:
            runs[-1][1] += 1
        else:
            runs.append([token, 1])
    return runs
''', [([],[]),(['a','a','b','a'],[['a',2],['b',1],['a',1]]),(['A','a'],[['A',1],['a',1]]),(['','','x'],[['',2],['x',1]])], [(['x'],[['x',1]])], [[1]], [('runs[-1][0] == token','runs[-1][0].lower() == token.lower()'),('for token in tokens:','for token in sorted(tokens):'),('runs[-1][1] += 1','runs[-1][1] = 1')])
write(5,'trailing-maxima',C,'Input has values (integer list) and width (positive integer). For each position return the maximum of that value and up to width-1 immediately preceding values. Initial windows may be shorter; width above length is allowed. Empty values returns [].', '''
def solve(data):
    obj = mapping(data)
    values = [integer(v) for v in sequence(obj["values"])]
    width = integer(obj["width"])
    if width <= 0:
        raise ValueError("positive width required")
    result = []
    for index in range(len(values)):
        start = max(0, index - width + 1)
        result.append(max(values[start:index + 1]))
    return result
''', [({'values':[],'width':2},[]),({'values':[5,1,2,0],'width':2},[5,5,2,2]),({'values':[-4,-8,-3],'width':8},[-4,-4,-3]),({'values':[4,1,3],'width':1},[4,1,3])], [({'values':[3],'width':1},[3])], [{'values':[1],'width':0}], [('index - width + 1','index - width'),('values[start:index + 1]','values[:index + 1]'),('max(values[start:index + 1])','min(values[start:index + 1])')])
write(6,'record-overlay',C,'Input has base (object) and edits (list of [key,value]). Keys are strings. Apply edits in order to a copy. A null value deletes the key (missing deletes are harmless); all other JSON values overwrite or insert. Return resulting object.', '''
def solve(data):
    obj = mapping(data)
    result = dict(mapping(obj["base"]))
    for edit in sequence(obj["edits"]):
        pair = sequence(edit)
        if len(pair) != 2:
            raise ValueError("edit needs key and value")
        key = text(pair[0])
        value = pair[1]
        if value is None:
            result.pop(key, None)
        else:
            result[key] = value
    return result
''', [({'base':{},'edits':[]},{}),({'base':{'a':1},'edits':[['a',None],['b',0]]},{'b':0}),({'base':{},'edits':[['x',1],['x',2],['z',None]]},{'x':2}),({'base':{'a':2},'edits':[['a',False]]},{'a':False})], [({'base':{},'edits':[['a',1]]},{'a':1})], [{'base':{},'edits':[['x']]}], [('if value is None:','if not value:'),('for edit in sequence(obj["edits"]):','for edit in reversed(sequence(obj["edits"])):'),('result.pop(key, None)','result[key] = None')])
