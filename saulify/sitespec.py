""" Reading and representation of Instapaper spec files. """

__all__ = ["load_rules", "load_testcases"]

import re
import collections


def parse_specfile(f):
    """
    Parses Instapaper spec file into its component directives

    Args:
      f (file): Spec file object

    Returns:
      List of (label, content) tuples representing directives
    """

    # This regex parses individual lines in the spec file.
    #
    # These consist of a label and content, which are arbitrary text strings
    # separated by the ':' character and optionally end with a python-style
    # comment, as illustrated below:
    #
    # strip_id_or_class: decoration # Remove decorations
    r = re.compile("(?P<label>[^#:]+):(?P<content>[^#]+)")

    for t in f.read().splitlines():
        m = r.match(t)
        if m:
            label = m.group("label").strip()
            content = m.group("content").strip()
            yield (label, content)


def load_testcases(f):
    """
    Reads test cases from an Instapaper spec file.

    Scans file until it reaches a line labelled "test_url", then creates a
    new test spec dictionary. Subsequent lines populate the test dictionary.
    Multiple test cases in a single file are supported.

    Args:
      f (file): Spec file object

    Returns:
      List of dictionaries specifying each test case.
    """

    cases = []

    for label, content in parse_specfile(f):
        if label == "test_url":
            case = collections.defaultdict(list)
            case[label] = content
            cases.append(case)
        elif label.startswith("test_"):
            if not cases:
                raise Exception("Invalid spec file")
            opencase = cases[-1]
            opencase[label].append(content)

    return cases


def load_rules(f):
    """
    Reads scraping rules from Instapaper spec file.

    The scraping rules are stored in a dictionary. For simple directives
    like `strip`, the rules are stored in a list using the directive name as
    the key. Exceptions to this storage format are detailed below.

    `find_string` / `replace_string` :
        These directives come in pairs; one find regular expression and one
        replace. Stored as a list of 2-tuples under the key `"find_replace"`.

    Boolean properties such as `prune`:
        Stored as `True` or `False` according to the last line specifying
        the value.

    Args:
      f (file): Spec file object

    Returns:
      Dictionary containing scraper rules.
    """

    rules = collections.defaultdict(list)
    find_string = None

    boolean_props = ["prune"]

    for label, content in parse_specfile(f):

        if label.startswith("test_"):
            continue

        if label == "find_string":
            find_string = content

        elif label == "replace_string":
            if not find_string:
                raise Exception("Invalid spec file")
            rules["find_replace"].append((find_string, content))

        elif label in boolean_props:
            if content == "yes":
                rules[label] = True
            elif content == "no":
                rules[label] = False
            else:
                raise Exception("Invalid spec file")

        else:
            rules[label].append(content)

    return rules
