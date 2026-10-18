"""Strict diagnostic parser for serial old-ExUnit trace logs, version 1.

Not suitable for interleaved parallel traces. Keep the original parser immutable.
Identity is a (module, test name) pair; failures always override completion lines.
"""
import re

MODULE = r'[A-Z][A-Za-z0-9_]*(?:\.[A-Z][A-Za-z0-9_]*)*'
HEADER = re.compile(r'^(' + MODULE + r')$')
DONE = re.compile(r'^\s+\* test (.+?) \([0-9]+(?:\.[0-9]+)?ms\)$')
FAIL = re.compile(r'^\s*\d+\) test (.+?) \((' + MODULE + r')\)$')
SUMMARY = re.compile(r'^(\d+) tests, (\d+) failures?$')


def parse(text):
    results = {}
    completed = set()
    module = None
    summaries = []
    for line in text.splitlines():
        match = HEADER.fullmatch(line)
        if match:
            module = match[1]
            continue
        match = DONE.fullmatch(line)
        if match:
            if module is None:
                raise ValueError('Completed test without module header')
            key = (module, match[1])
            if key in completed:
                raise ValueError('Duplicate completed identity: ' + repr(key))
            completed.add(key)
            results.setdefault(key, 'PASSED')
            continue
        match = FAIL.fullmatch(line)
        if match:
            results[(match[2], match[1])] = 'FAILED'
            continue
        match = SUMMARY.fullmatch(line)
        if match:
            summaries.append(tuple(map(int, match.groups())))
    if len(summaries) != 1:
        raise ValueError('Expected exactly one final test summary')
    count, failures = summaries[0]
    if len(results) != count or sum(v == 'FAILED' for v in results.values()) != failures:
        raise ValueError('Parsed identities/failures disagree with raw suite totals')
    return [{'module': mod, 'test': name, 'status': status}
            for (mod, name), status in sorted(results.items())]
