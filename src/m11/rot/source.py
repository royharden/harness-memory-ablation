"""Frozen clones/1 and complexity/1 source calculations, without execution."""

import ast
import io
import keyword
import math
import tokenize
from collections import defaultdict


_FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)
_SCOPES = _FUNCTIONS + (ast.ClassDef,)
_SKIP = {
    tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT,
    tokenize.DEDENT, tokenize.ENDMARKER, tokenize.ENCODING,
}


def _span(node):
    return (node.lineno, node.col_offset), (node.end_lineno, node.end_col_offset)


def _body_span(node):
    if isinstance(node, ast.Lambda):
        return _span(node.body)
    return _span(node.body[0])[0], _span(node.body[-1])[1]


def _inside(position, span):
    return span[0] <= position < span[1]


def _nested_scopes(node):
    """Nearest scopes only: their bodies remove all deeper scopes too."""
    body = [node.body] if isinstance(node, ast.Lambda) else node.body
    pending = list(body)
    while pending:
        child = pending.pop()
        if isinstance(child, _SCOPES):
            yield child
        else:
            pending.extend(ast.iter_child_nodes(child))


def _complexity(node):
    total = 1
    pending = [node.body] if isinstance(node, ast.Lambda) else list(node.body)
    while pending:
        child = pending.pop()
        if isinstance(child, _SCOPES):
            continue
        if isinstance(child, (ast.If, ast.IfExp, ast.For, ast.AsyncFor,
                              ast.While, ast.ExceptHandler)):
            total += 1
        if isinstance(child, ast.comprehension):
            total += len(child.ifs)
        if isinstance(child, ast.BoolOp):
            total += len(child.values) - 1
        if isinstance(child, ast.Match):
            for index, case in enumerate(child.cases):
                bare_final = (
                    index == len(child.cases) - 1 and case.guard is None
                    and isinstance(case.pattern, ast.MatchAs)
                    and case.pattern.pattern is None and case.pattern.name is None
                )
                total += not bare_final
        pending.extend(ast.iter_child_nodes(child))
    return total


def _subtract_reference(metric, reference, fields):
    if reference is None:
        metric["reference_excess"] = None
        metric["reference_reason"] = "reference_not_supplied"
        return
    if not isinstance(reference, dict) or reference.get("definition") != metric["definition"]:
        raise ValueError("reference must use the matching frozen metric definition")
    if reference.get("unavailable_reason") is not None:
        metric["reference_excess"] = None
        metric["reference_reason"] = "reference_unavailable"
        return
    excess = {}
    for field in fields:
        value = reference.get(field)
        if (isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(value)):
            raise ValueError("reference metric values must be numeric")
        excess[field] = metric[field] - value if metric[field] is not None else None
    metric["reference_excess"] = excess
    metric["reference_reason"] = metric["unavailable_reason"]


def analyze_python(source: str, *, reference: dict | None = None) -> dict:
    """Analyze text, optionally subtracting an explicitly supplied checkpoint reference.

    ``reference`` is another analyze_python result for the same checkpoint; the
    caller owns checkpoint binding. Syntax errors produce unavailable metrics.
    Names/positions are evidence, not executable objects. AST columns count UTF-8
    bytes, so token columns are converted before comparing source positions.
    """
    if not isinstance(source, str):
        raise TypeError("source must be str")
    if reference is not None and (not isinstance(reference, dict)
                                  or not {"clones", "complexity"} <= reference.keys()):
        raise ValueError("reference must contain clones and complexity results")
    try:
        tree = ast.parse(source)
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except (SyntaxError, tokenize.TokenError, IndentationError) as error:
        return {
            "clones": {"definition": "clones/1", "value": None,
                       "unavailable_reason": "syntax_error"},
            "complexity": {"definition": "complexity/1", "value": None,
                           "unavailable_reason": "syntax_error"},
            "syntax_error": {"line": getattr(error, "lineno", None),
                             "message": str(error)},
        }
    lines = source.splitlines(keepends=True)
    significant = []
    for token in tokens:
        if token.type in _SKIP:
            continue
        line, column = token.start
        position = (line, len(lines[line - 1][:column].encode("utf-8")))
        spelling = "ID" if token.type == tokenize.NAME and not keyword.iskeyword(token.string) else token.string
        significant.append((position, (token.type, spelling)))
    functions = sorted((node for node in ast.walk(tree) if isinstance(node, _FUNCTIONS)),
                       key=lambda node: _span(node))
    scopes = [node for node in ast.walk(tree) if isinstance(node, _SCOPES)]
    ownership = defaultdict(list)
    for position, spelling in significant:
        candidates = [node for node in scopes if _inside(position, _body_span(node))]
        if candidates:
            # The most deeply contained body owns a position. Classes reserve
            # their body tokens but contribute no function denominator; nested
            # methods/lambdas still own their own contained body tokens.
            owner = max(candidates, key=lambda node: (
                _body_span(node)[0], tuple(-value for value in _body_span(node)[1])))
            if isinstance(owner, _FUNCTIONS):
                ownership[id(owner)].append((position, spelling))
    windows = defaultdict(list)
    owned_positions = set()
    function_results = []
    for index, node in enumerate(functions):
        nested = list(_nested_scopes(node))
        own = ownership[id(node)]
        owned_positions.update(position for position, _ in own)
        for start in range(max(0, len(own) - 29)):
            block = own[start:start + 30]
            windows[tuple(spelling for _, spelling in block)].append(
                (index, tuple(position for position, _ in block)))
        excluded_lines = set()
        for child in nested:
            excluded_lines.update(range(child.lineno, child.end_lineno + 1))
        length = len(set(range(node.lineno, node.end_lineno + 1)) - excluded_lines)
        function_results.append({
            "scope_id": index, "name": getattr(node, "name", "<lambda>"),
            "line": node.lineno, "column": node.col_offset,
            "complexity": _complexity(node), "length": length,
            "significant_tokens": len(own),
        })
    cloned_positions = set()
    for matches in windows.values():
        if len({index for index, _ in matches}) > 1:
            for _, positions in matches:
                cloned_positions.update(positions)
    denominator = len(owned_positions)
    clones = {"definition": "clones/1", "value": len(cloned_positions) / denominator if denominator else None,
              "numerator": len(cloned_positions), "denominator": denominator,
              "unavailable_reason": None if denominator else "zero_function_tokens"}
    values = [row["complexity"] for row in function_results]
    complexity = {"definition": "complexity/1", "sum": sum(values), "count": len(values),
                  "max": max(values) if values else None,
                  "longest_length": max((row["length"] for row in function_results), default=None),
                  "functions": function_results,
                  "unavailable_reason": None if values else "no_functions"}
    _subtract_reference(clones, reference["clones"] if reference else None, ["value"])
    _subtract_reference(complexity, reference["complexity"] if reference else None,
                        ["sum", "count", "max", "longest_length"])
    return {"clones": clones, "complexity": complexity, "syntax_error": None}
