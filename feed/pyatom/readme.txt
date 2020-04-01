PyAtom


PyAtom is a Python library module I wrote to make it very easy to create
an Atom syndication feed.

http://atomenabled.org/developers/syndication/


I have released PyAtom under The Academic Free License 2.1.  I intend to
donate PyAtom to the Python Software Foundation.


Notes on PyAtom:

XML is best represented in a tree structure, and PyAtom is a set of
classes that automatically manage the tree structure for the user.  The
top level of an Atom feed is an XML "Feed" element with a "<feed>" tag;
the Feed element has other elements nested inside it that describe the
feed, and then it has 0 or more Entry elements, each of which has
elements that describe the Entry.

Take a look at RunPyAtomTestCases(), at the end of pyatom.py, for
example code showing how to set up a feed with an entry.

To create an XML document with a feed in it, the user does this:

xmldoc = XMLDoc()
feed = Feed()
xmldoc.root_element = feed

To assign an entry to a feed, the user just does this:

feed.entries.append(entry)

This adds "entry" to the internal list that keeps track of entries.
"entry" is now nested inside "feed", which is nested inside "xmldoc".

Later, when the user wants to save the XML in a file, the user can just
do this:

f = open("file.xml", "w")
s = str(xmldoc)
f.write(s)

To make the string from xmldoc, the XMLDoc class walks through the XML
elements nested inside xmldoc, asking each one to return its string.
Each element that has other elements nested inside does the same thing.
The whole tree is recursively walked, and the tags all return strings
that are indented properly for their level in the tree.

The classes that implement Atom in PyAtom just use the heck out of
inheritance.  There are abstract base classes that implement broadly
useful behavior, and lots of classes that just inherit and use this
behavior; but there are plenty of places where the child classes
overload the inherited behavior and do something different.  The way
Python handles inheritance made this a joy to code up.



If you have any questions about anything here, please contact me using
this email address:

pyatom@langri.com
