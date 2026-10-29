from source_builder import write
C='decision-dependent'
NOTE=' This artificial intervention withholds exactly one synthetic project choice in treatment memory; visible examples do not select it.'
write(7,'quantized-ties',C,'Input has values (integer list) and step (positive integer). Return each value rounded to its nearest multiple of step. Exact halfway ties follow the retained project choice: select the adjacent smaller or larger numeric multiple.'+NOTE, '''
def solve(data):
    obj = mapping(data)
    step = integer(obj["step"])
    if step <= 0:
        raise ValueError("positive step required")
    result = []
    for value in sequence(obj["values"]):
        value = integer(value)
        low, remainder = divmod(value, step)
        if remainder * 2 >= step:
            low += 1
        result.append(low * step)
    return result
''', [({'values':[5,-5,15,-15],'step':10},[10,0,20,-10]),({'values':[1,9,-9],'step':10},[0,10,-10]),({'values':[],'step':3},[])], [({'values':[2,8],'step':10},[0,10])], [{'values':[1],'step':0}], [('remainder * 2 >= step','remainder * 2 > step'),('remainder * 2 >= step','remainder > 0'),('low, remainder = divmod(value, step)','low, remainder = divmod(abs(value), step)')], ('decision','current','synthetic project choice Q17','TIE_CEILING: exact ties select the larger numeric multiple, including for negative values.'))
write(8,'frontier-walk',C,'Input has graph (object of string names to lists of adjacent names) and start (declared string name). Return reachable names once in breadth-first order. Reject unknown references. Ignore duplicate edges. Within each node process unseen neighbors in the retained lexical priority, either ascending or descending. Start comes first.'+NOTE, '''
def solve(data):
    obj = mapping(data)
    graph = mapping(obj["graph"])
    start = text(obj["start"])
    if start not in graph:
        raise ValueError("unknown start")
    for node, neighbors in graph.items():
        text(node)
        if not {text(v) for v in sequence(neighbors)} <= graph.keys():
            raise ValueError("unknown neighbor")
    queue = [start]
    seen = {start}
    result = []
    while queue:
        node = queue.pop(0)
        result.append(node)
        for neighbor in sorted(set(graph[node]), reverse=True):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return result
''', [({'graph':{'s':['a','b'],'a':['c'],'b':['c'],'c':[]},'start':'s'},['s','b','a','c']),({'graph':{'x':['x']},'start':'x'},['x']),({'graph':{'a':['b','b'],'b':[],'z':[]},'start':'a'},['a','b'])], [({'graph':{'a':['b'],'b':[]},'start':'a'},['a','b'])], [{'graph':{'a':['b']},'start':'a'}], [('reverse=True','reverse=False'),('node = queue.pop(0)','node = queue.pop()'),('result.append(node)','result.insert(0, node)')], ('decision','current','synthetic project choice F28','NEIGHBOR_DESCENDING: sort newly considered neighbors in descending lexical order.'))
write(9,'word-joiner',C,'Input is a string. Split on runs of Unicode whitespace, lowercase every word with str.lower and join words using the retained separator choice (hyphen, underscore or period). Empty/whitespace-only input returns an empty string. Preserve nonwhitespace punctuation inside words.'+NOTE, '''
def solve(data):
    source = text(data)
    words = source.split()
    normalized = []
    for word in words:
        normalized.append(word.lower())
    return ".".join(normalized)
''', [(' A B ','a.b'),('Hello\tWORLD\nNow','hello.world.now'),('',''),('ÉCOLE X','école.x'),('a-b c','a-b.c')], [('Solo','solo')], [1], [('".".join','"-".join'),('word.lower()','word'),('words = source.split()','words = source.strip().split(" ")')], ('decision','current','synthetic project choice W39','JOIN_PERIOD: use one literal period between normalized words.'))
write(10,'revision-choice',C,'Input is a list of records with key (string), revision (integer) and value (JSON). For each key keep the greatest revision and return key-to-value mapping. Equal greatest revisions follow the retained encounter rule (first or last).'+NOTE, '''
def solve(data):
    winners = {}
    for record in sequence(data):
        record = mapping(record)
        key = text(record["key"])
        revision = integer(record["revision"])
        if key not in winners or revision > winners[key][0]:
            winners[key] = (revision, record["value"])
    return {key: entry[1] for key, entry in winners.items()}
''', [([],{}),([{'key':'x','revision':2,'value':'first'},{'key':'x','revision':2,'value':'last'}],{'x':'first'}),([{'key':'x','revision':3,'value':0},{'key':'x','revision':1,'value':1}],{'x':0}),([{'key':'a','revision':-1,'value':None},{'key':'b','revision':0,'value':False}],{'a':None,'b':False})], [([{'key':'a','revision':1,'value':7}],{'a':7})], [[{'key':'a','revision':True,'value':1}]], [('revision > winners[key][0]','revision >= winners[key][0]'),('revision > winners[key][0]','revision < winners[key][0]'),('if key not in winners or revision > winners[key][0]:','if True:')], ('decision','current','synthetic project choice R41','TIE_FIRST: among equal greatest revisions retain the first encountered record.'))
write(11,'grid-adjacency',C,'Input has rows, cols (nonnegative integers), row and col (integer position). Reject a position outside the grid. Return in-bounds orthogonal neighbors as [row,col] coordinates, in the retained direction priority (one permutation of N,E,S,W). Filter boundaries without changing priority.'+NOTE, '''
def solve(data):
    obj = mapping(data)
    rows = integer(obj["rows"])
    cols = integer(obj["cols"])
    row = integer(obj["row"])
    col = integer(obj["col"])
    if not (0 <= row < rows and 0 <= col < cols):
        raise ValueError("position outside grid")
    offsets = [(0, -1), (-1, 0), (0, 1), (1, 0)]
    result = []
    for dr, dc in offsets:
        nr, nc = row + dr, col + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            result.append([nr, nc])
    return result
''', [({'rows':3,'cols':3,'row':1,'col':1},[[1,0],[0,1],[1,2],[2,1]]),({'rows':2,'cols':2,'row':0,'col':0},[[0,1],[1,0]]),({'rows':1,'cols':1,'row':0,'col':0},[]),({'rows':2,'cols':3,'row':1,'col':2},[[1,1],[0,2]])], [({'rows':1,'cols':1,'row':0,'col':0},[])], [{'rows':1,'cols':1,'row':1,'col':0}], [('[(0, -1), (-1, 0), (0, 1), (1, 0)]','[(-1, 0), (0, 1), (1, 0), (0, -1)]'),('0 <= nr < rows and 0 <= nc < cols','0 <= nr <= rows and 0 <= nc <= cols'),('result.append([nr, nc])','result.append([nc, nr])')], ('decision','current','synthetic project choice G52','DIRECTION_WNES: examine west, north, east, south in that order.'))
write(12,'threshold-buckets',C,'Input has cuts (strictly increasing integer list) and values (integer list). Return bucket indices in 0..len(cuts). Values not equal to cuts cross all strictly smaller cuts. Equality uses the retained project choice: cross that cut or stay in its lower bucket.'+NOTE, '''
def solve(data):
    obj = mapping(data)
    cuts = [integer(v) for v in sequence(obj["cuts"])]
    if any(a >= b for a, b in zip(cuts, cuts[1:])):
        raise ValueError("cuts must strictly increase")
    result = []
    for value in sequence(obj["values"]):
        value = integer(value)
        result.append(sum(value > cut for cut in cuts))
    return result
''', [({'cuts':[0,10],'values':[-1,0,1,10,11]},[0,0,1,1,2]),({'cuts':[],'values':[1,2]},[0,0]),({'cuts':[-5,5],'values':[-5,5]},[0,1])], [({'cuts':[0,10],'values':[-1,1,11]},[0,1,2])], [{'cuts':[1,1],'values':[]}], [('value > cut','value >= cut'),('sum(value > cut for cut in cuts)','sum(value < cut for cut in cuts)'),('result.append(sum(value > cut for cut in cuts))','result.append(min(1, sum(value > cut for cut in cuts)))')], ('decision','current','synthetic project choice T63','EQUALITY_LOWER: equality stays in the lower bucket; count strictly smaller cuts.'))
