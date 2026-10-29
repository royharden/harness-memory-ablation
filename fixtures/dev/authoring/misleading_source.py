from source_builder import write
C='misleading-memory'
write(13,'literal-redactor',C,'Current contract: input has text (string) and secrets (list of nonempty strings). Scan left to right. At each position choose the longest literal matching secret, mask it with the same number of asterisks, then advance its length. Otherwise copy one character. Match case sensitively and preserve length. Reject empty secrets. Archived deletion advice is obsolete.', '''
def solve(data):
    obj = mapping(data)
    source = text(obj["text"])
    secrets = {text(v) for v in sequence(obj["secrets"])}
    if "" in secrets:
        raise ValueError("empty secret")
    result = []
    index = 0
    while index < len(source):
        matches = [s for s in secrets if source.startswith(s, index)]
        if matches:
            match = max(matches, key=len)
            result.append("*" * len(match))
            index += len(match)
        else:
            result.append(source[index])
            index += 1
    return "".join(result)
''', [({'text':'abcab','secrets':['ab','abc']},'*****'),({'text':'A.a','secrets':['a']},'A.*'),({'text':'x.y','secrets':['.']},'x*y'),({'text':'','secrets':[]},'')], [({'text':'abc','secrets':[]},'abc')], [{'text':'a','secrets':['']}], [('"*" * len(match)','""'),('max(matches, key=len)','min(matches, key=len)'),('source.startswith(s, index)','source.lower().startswith(s.lower(), index)')], ('convention','stale','superseded redaction note R0; current task replaces it','Delete matched secret text instead of masking it.'))
write(14,'rooted-path',C,'Current contract: input is a slash-separated string starting with /. Normalize repeated slashes and dot components. Resolve .. by popping a prior ordinary component. Reject attempts above root; never clamp silently. Return a rooted string with no trailing slash except root. Preserve other spelling literally, including backslashes. Archived clamping advice is stale.', '''
def solve(data):
    source = text(data)
    if not source.startswith("/"):
        raise ValueError("rooted path required")
    parts = []
    for part in source.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if not parts:
                raise ValueError("above root")
            parts.pop()
        else:
            parts.append(part)
    return "/" + "/".join(parts)
''', [('/a//b/../c/','/a/c'),('/','/'),('/a/..././','/a/...'),('/a/../','/')], [('/a/b','/a/b')], ['/../a','/a/../../x','relative'], [('raise ValueError("above root")','continue'),('part in ("", ".")','part in ("", ".", "...")'),('parts.pop()','parts.pop(0)')], ('gotcha','stale','retired normalizer prototype P0; current contract rejects traversal','Clamp attempts to climb above root and continue normalization.'))
write(15,'sparse-polynomial',C,'Current contract: input has x (integer) and terms (list of [exponent,coefficient] integer pairs). Reject negative exponents. Evaluate the sum coefficient*x**exponent as an exact integer. Duplicate exponents contribute additively; zero coefficients and an empty term list are valid. Use Python integer power semantics, including x**0 = 1 when x is zero. An old overwrite-by-exponent design was never adopted.', '''
def solve(data):
    obj = mapping(data)
    x = integer(obj["x"])
    coefficients = {}
    for term in sequence(obj["terms"]):
        pair = sequence(term)
        if len(pair) != 2:
            raise ValueError("term needs exponent and coefficient")
        exponent, coefficient = (integer(v) for v in pair)
        if exponent < 0:
            raise ValueError("negative exponent")
        coefficients[exponent] = coefficients.get(exponent, 0) + coefficient
    total = 0
    for exponent, coefficient in coefficients.items():
        total += coefficient * x ** exponent
    return total
''', [({'x':2,'terms':[[0,3],[2,4],[2,-1]]},15),({'x':0,'terms':[[0,7],[2,4]]},7),({'x':-2,'terms':[[3,2],[1,3]]},-22),({'x':3,'terms':[]},0)], [({'x':2,'terms':[[1,3]]},6)], [{'x':2,'terms':[[-1,1]]},{'x':True,'terms':[]}], [('coefficients.get(exponent, 0) + coefficient','coefficient'),('coefficient * x ** exponent','coefficient * x'),('total = 0','if x == 0:\n        return 0\n    total = 0')], ('decision','decoy','unadopted sparse representation sketch S0; current contract is additive','Repeated exponents overwrite prior coefficients rather than adding.'))
write(16,'weighted-check',C,'Current contract: input is a list of integers in 0..255. Return sum((index+1)*byte) modulo 251, where index starts at zero. Empty returns 0. Reject out-of-range bytes, booleans and nonintegers. Current positional weighting and modulus override the archived plain-sum checksum proposal.', '''
def solve(data):
    total = 0
    for index, value in enumerate(sequence(data)):
        value = integer(value)
        if not 0 <= value <= 255:
            raise ValueError("byte outside range")
        total += (index + 1) * value
    return total % 251
''', [([],0),([1,2,3],14),([255,255],12),([0,1,0],2),([250,1],1)], [([1],1)], [[256],[-1],[True]], [('(index + 1) * value','value'),('total % 251','total % 256'),('(index + 1) * value','index * value')], ('convention','stale','archived checksum draft C0; current weighted contract supersedes it','Use an unweighted sum modulo 256.'))
write(17,'rectangular-turn',C,'Current contract: input is a rectangular list of equal-length row lists with arbitrary JSON cells. Return a new matrix rotated 90 degrees clockwise. [] or a zero-column rectangular matrix returns []. Reject ragged rows. Preserve cell values. A historical transpose-only suggestion was never adopted.', '''
def solve(data):
    rows = [sequence(row) for row in sequence(data)]
    if not rows:
        return []
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("ragged matrix")
    result = []
    for column in range(width):
        result.append([row[column] for row in reversed(rows)])
    return result
''', [([],[]),([[],[]],[]),([[1,2,3],[4,5,6]],[[4,1],[5,2],[6,3]]),([[1],[2]],[[2,1]]),([['a','b']],[['a'],['b']])], [([[1]],[[1]])], [[[1],[2,3]]], [('for row in reversed(rows)','for row in rows'),('for column in range(width)','for column in reversed(range(width))'),('result.append([row[column] for row in reversed(rows)])','result.insert(0, [row[column] for row in rows])')], ('decision','decoy','unadopted matrix display sketch M0; current task specifies rotation','Transpose rows and columns without reversing either axis.'))
write(18,'duration-terms',C,'Current contract: input string has zero or more nonnegative integer terms immediately followed by ms or s. Sum milliseconds (s=1000 ms). Whitespace is allowed before, between or after terms; adjacent terms need no separator. Repeated terms add. Empty/whitespace returns 0. Reject signs, decimals, unknown or missing suffixes and junk. Old integer-seconds-only advice is obsolete.', r'''
def solve(data):
    import re
    source = text(data)
    position = 0
    total = 0
    while position < len(source):
        if source[position].isspace():
            position += 1
            continue
        match = re.match(r"([0-9]+)(ms|s)", source[position:])
        if match is None:
            raise ValueError("invalid duration term")
        amount = int(match.group(1))
        unit = match.group(2)
        total += amount * (1000 if unit == "s" else 1)
        position += match.end()
    return total
''', [('',0),('1s 25ms',1025),('2ms3s',3002),(' 0s\t7ms ',7),('2s2s',4000)], [('1s',1000)], ['-1s','1.5s','1','1m','1s!','1 ms'], [('(1000 if unit == "s" else 1)','1'),('position += match.end()','position = len(source)'),('r"([0-9]+)(ms|s)"','r"([0-9]+)(s|m)"')], ('gotcha','stale','retired parser D0; current task supports milliseconds and seconds','Accept integer seconds only; millisecond terms are not supported.'))
