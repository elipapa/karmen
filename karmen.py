#!/usr/bin/env python3

"""command/hack to lookup LanguaL food items.
Also has utilities to explore the hierarchy

Ideally:

$ karmen 'ALMOND' (equivalent to karmen search 'ALMOND')
B1272

$ karmen search 'B1272'
ALMOND

$ karmen tree 'ALMOND'
B1213, NUT PRODUCING PLANT
`-- B1062, TEMPERATE-ZONE NUT PRODUCING PLANT
    `-- B1272, ALMOND

$ karmen children 'ALMOND'
ALMOND, SWEET
ALMOND, BITTER

"""


import sys
from lxml import etree
import argparse
import re

# Parse tree
langual = etree.parse('LanguaL2013.XML')
"""
the tree structure is not represented as XML hierarchy. each descriptor is at the same leve. The hierarchy is coded using parents IDs:
FTC is the node ID
BT is the parent ID
"""

# TODO should turn all of this in a LanguaL thesaurus class

def get_ftc(xmlelement):
    """returns a string with the langual code
    """
    return xmlelement.getchildren()[0].text


def get_name(xmlelement):
    """returns a string with the langual term
    """
    return xmlelement.getchildren()[1].text


def get_parentcode(xmlelement):
    """returns string with langual code of parent
    """
    return xmlelement.getchildren()[2].text


def find_byname(searchstring, langualtree=langual):
    """returns list of XML DESCRIPTOR elements that have an exact
     match to the provided term

    >>> d = find_byname('ALMOND')[0]
    >>> get_ftc(d)
    'B1272'
    """
    return [t.getparent() for t in langualtree.iter(tag="TERM")
                            if t.text == searchstring.upper()]


def contains_name(searchstring, langualtree=langual):
    """returns all XML DESCRIPTOR elements that contain the term

    >>> descrL = contains_name('ALMOND')
    >>> [get_name(d) for d in descrL]
    ['ALMOND', 'ALMOND, SWEET', 'ALMOND, BITTER', 'JAVA-ALMOND', 'JAVA-ALMOND', 'TROPICAL ALMOND']
    """
    return [t.getparent() for t in langualtree.iter(tag="TERM")
                            if searchstring.upper() in t.text]


def find_byftc(searchftc, langualtree=langual):
    """
    >>> d = find_byftc('B1272')[0]
    >>> get_name(d)
    'ALMOND'
    """
    return [t.getparent() for t in langualtree.iter(tag="FTC")
                            if t.text == searchftc]


def find_parent(xmlelement):
    """return XML element of parents

    >>> descr = find_byname('ALMOND')[0]
>>> parent = find_parent(descr)
>>> get_name(parent)
'TEMPERATE-ZONE NUT PRODUCING PLANT'
    """
    return find_byftc(get_parentcode(xmlelement))[0]


def find_children(xmlelement, langualtree = langual):
    """returns a list of all children,
    meaning all terms who have this element's FTC code listed as their BT code.
    """
    thiscode = get_ftc(xmlelement)
    return [t.getparent() for t in langualtree.iter(tag='BT')
                            if t.text == thiscode]


def find_descendants(xmlelement, langualtree = langual):
    """returns a list of all descendants,going down the children recursively.
    """
    thiscode = get_ftc(xmlelement)
    return [t.getparent() for t in langualtree.iter(tag='BT')
                                if t.text == thiscode]



def find_allparents(xmlelement, langualtree=langual):
    """returns a list of all xml elements from root to the current element
    >>> descr = find_byname('ALMOND')[0]
    >>> [get_name(d) for d in reversed(find_allparents(descr))]
    ['LANGUAL THESAURUS ROOT', 'B.   FOOD SOURCE', 'PLANT USED AS FOOD SOURCE', 'GRAIN OR SEED-PRODUCING PLANT', 'NUT OR EDIBLE SEED PRODUCING PLANT', 'NUT PRODUCING PLANT', 'TEMPERATE-ZONE NUT PRODUCING PLANT', 'ALMOND']
    """
    branch = [xmlelement]
    thisnode = xmlelement

    while True:
        if get_name(thisnode) == 'LANGUAL THESAURUS ROOT':
            break
        else:
            nextup = find_parent(thisnode)
            branch.append(nextup)
            thisnode = nextup

    return branch


def elementlist_tostr(elementlist):
    return [ '        '.join([get_ftc(d),get_name(d)]) for d in elementlist ]


def print_astree(stringlist):
    """assumes root to child order
    """
    for i,e in enumerate(stringlist):
        leading = '+-'
        print('      ' * i + leading + e)

    return


def search(searchterm, withtree = True, langualtree = langual):
    """command line command which recognized if input is code or name and uses the right function to query xml file
    """
    codes = re.compile(r'[A-Z]\d{4}\b')
    if codes.match(searchterm):
        elmt = find_byftc(searchterm)
        if not elmt:
            print("can't find: " + searchterm + "\n")
            return

    else:
        elmt = find_byname(searchterm
        if not elmt:
            print("can't find an exact match for: " + searchterm + "\n")
            elmt = contains_name(searchterm)
            if not elmt:
                print("can't find anything containing: " + searchterm + "\n")
                return

    for e in elmt:
        if withtree:
            elmtL = reversed(find_allparents(e))
            print_astree(elementlist_tostr(elmtL))
            print("\n--------\n")
        else:
            print( '        '.join([get_ftc(e),get_name(e)]) )
            print("\n--------\n")

    return


def ischild(possible_parent, xmlelement, langualtree = langual):
    """returns true if xmlelement is a child of possible_parent

    >>> ischild(find_byname('FISH')[0], find_byftc('B1234'))
    True
    """
    descendants = find_descendants(possible_parent)
    return (xmlelement in descendants)


def expand_nodes(elementlist, langualtree = langual):
    """takes a list of nodes and returns a list of all branches and leaves
    descending from those nodes.
    This can be used to exclude all the foods having LanguaL classification
    below the given nodes and thereby allowing to prescribe a diet in the most
    general terms
    """
    expandedL = elementlist
    for elemt in elementlist:
        L.extend( find_allchildren(elemt) )
    return expandedL


# TODO include children into print out of hierarchy


def main():
    parser = argparse.ArgumentParser(description='browse LanguaL thesaurus on the command line')
    parser.add_argument('searchstring', help = 'search term')


# # TODO argparse to use subcommands https://docs.python.org/3/library/argparse.html#sub-commands
#
#
#     subparsers = parser.add_subparsers()
#     parser_search = subparsers.add_parser('search', help="searches by code or name")
#     parser_search.add_argument('withtree', help="do not display hierarchy")


    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)
    else:
        args = parser.parse_args()
        search(searchstring)



if __name__ == '__main__':
    main()
