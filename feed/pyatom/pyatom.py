# pyatom.py -- PyAtom library module

"""
PyAtom

Module to make it really easy to create Atom syndication feeds.

This module is Copyright (C) 2006 Steve R. Hastings.
Licensed under the Academic Free License version 2.1

You might want to start with the test cases at the end; see how they
work, and then go back and look at the code in the module.

I hope you find this useful!

Steve R. Hastings

Please send your questions or comments to this email address:

pyatom@langri.com
"""



import re
import sys
import time

s_pyatom_name = "PyAtom"
s_pyatom_ver = "0.3.9"
s_pyatom_name_ver = "%s version %s" % (s_pyatom_name, s_pyatom_ver)

# string constants
# These string values are used in more than one place.

s_version = "version"
s_encoding = "encoding"
s_standalone = "standalone"

s_href = "href"
s_lang = "xml:lang"
s_link = "link"
s_term = "term"
s_type = "type"



def set_s_indent(s):
	"""
	Set up the globals PyAtom uses to indent its output:
	s_indent, and s_indent_big

	s_indent is the string to indent one level; default is \\t.

	s_indent_big is s_indent concatenated many times.  PyAtom uses slice
	copies to get indent strings from s_indent_big.
	"""
	global s_indent
	global s_indent_big
	s_indent = s
	s_indent_big = s*256

set_s_indent("\t")



class TFC(object):
	"""
	class TFC: Tag Format Control.
	Controls how tags are converted to strings.

	Arguments to __init__():
		level	Specifies what indent level to start at for output.  Default 0.
		mode	Specifies how to format the output:
				mode_terse -- minimal output (no indenting)
				mode_normal -- default
				mode_verbose -- normal, plus some XML comments

	Normally, if an XML item has no data, nothing is printed, but with
	mode_verbose you may get a comment like "Collection with 0 entries".

	Methods:
		b_print_all()
			Return True if TFC set for full printing.
		b_print_terse()
			Return True if TFC set for terse printing.
		b_print_verbose()
			Return True if TFC set for verbose printing.

		indent_by(incr)
			Return a TFC instance that indents by incr columns.
		s_indent(extra_indent=0)
			Return an indent string.
	"""
	mode_terse, mode_normal, mode_verbose = range(3)

	def __init__(self, level=0, mode=mode_normal):
		"""
Arguments:
	level	Specifies what indent level to start at for output.  Default 0.
	mode	Specifies how to format the output:
			mode_terse -- minimal output (no indenting)
			mode_normal -- default
			mode_verbose -- normal, plus some XML comments

Normally, if an XML item has no data, nothing is printed, but with
mode_verbose you may get a comment like "Collection with 0 entries".
		"""
		self.level = level
		self.mode = mode

	def b_print_all(self):
		"""
		Return True if TFC set for full printing.

		Some optional things are usually suppressed, but will be printed
		if the current level is 0.  And everything gets printed when
		mode_verbose is set.
		"""
		return self.level == 0 or self.mode == TFC.mode_verbose

	def b_print_terse(self):
		"""
		Return True if TFC set for terse printing.
		"""
		return self.mode == TFC.mode_terse

	def b_print_verbose(self):
		"""
		Return True if TFC set for verbose printing.
		"""
		return self.mode == TFC.mode_verbose

	def indent_by(self, incr):
		"""
		Return a TFC instance that indents by incr columns.

		Pass this to a function that takes a TFC to get a temporary indent.
		"""
		return TFC(self.level + incr, self.mode)
	def s_indent(self, extra_indent=0):
		"""
		Return an indent string.

		Return a string of white space that indents correctly for the 
		current TFC settings.  If specified, extra_indent will be added
		to the current indent level.
		"""
		if self.mode == TFC.mode_terse:
			return ""
		level = self.level + extra_indent
		return s_indent_big[0:level]



pat_nbsp = re.compile(r'&nbsp;')
def s_entities_to_ws(s):
	"""
	Return a copy of s with HTML whitespace entities replaced by a space.

	Currently just gets rid of HTML non-breaking spaces ("&nbsp;").
	"""
	if not s:
		return s

	s = re.sub(pat_nbsp, " ", s)
	return s

def s_normalize_ws(s):
	"""
	Return a copy of string s with each run of whitespace replaced by one space.
	>>> s = "and    now\n\n\nfor \t  something\v   completely\r\n  different"
	>>> print s_normalize_ws(s)
	and now for something completely different
	>>>
	"""
	lst = s.split()
	s = " ".join(lst)
	return s
	

def s_escape_html(s):
	"""
	Return a copy of string s with HTML codes escaped.

	This is useful when you want HTML tags printed literally, rather than
	interpreted.

	>>> print s_escape_html("<head>")
	&lt;head&gt;
	>>> print s_escape_html("&nbsp;")
	&amp;nbsp;
	"""
	s = s.replace("&", "&amp;")
	s = s.replace("<", "&lt;")
	s = s.replace(">", "&gt;")
	return s

def s_create_atom_id(t, domain_name, uri=""):
	"""
	Create ID using Mark Pilgrim's algorithm.

	Algorithm taken from here:
	http://diveintomark.org/archives/2004/05/28/howto-atom-id
	"""

	# ymd (year-month-day) example: 2003-12-13
	ymd = time.strftime("%Y-%m-%d", t)

	if uri == "":
		# mush (all mushed together) example: 20031213083000
		mush = time.strftime("%Y%m%d%H%M%S", t)
		uri = "/weblog/" + mush

	# s = "tag:" + domain_name + "," + ymd + ":" + uri
	s = "tag:%s,%s:%s" % (domain_name, ymd, uri)

	s = s.replace("#", "/")

	return s

s_copyright_multiyear = "Copyright %s %d-%d by %s."
s_copyright_oneyear = "Copyright %s %d by %s."
def s_copyright(s_owner, s_csym="(C)", end_year=None, start_year=None):
	"""
	Return a string with a copyright notice.

	s_owner
		string with copyright owner's name.
	s_csym
		string with copyright symbol. (An HTML entity might be good here.)
	end_year
		last year of the copyright.  Default is the current year.
	start_year
		first year of the copyright.

	If only end_year is specified, only print one year; if both end_year and
	start_year are specified, print a range.

	To localize the entire copyright message into another language, change
	the global variables with the copyright template:
		s_copyright_multiyear: for a year range
		s_copyright_oneyear: for a single year
	"""
	if not end_year:
		end_year = time.localtime().tm_year

	if start_year:
		return s_copyright_multiyear % (s_csym, start_year, end_year, s_owner)

	return s_copyright_oneyear % (s_csym, end_year, s_owner)



# Here are all of the possible XML items.
#
# Supported by PyAtom:
# XML Declaration: <?xml ... ?>
# Comments: <!-- ... -->
# Elements: <tag_name>...</tag_name>
#
# Minimal support:
# Markup Declarations: <!KEYWORD ... >
# Processing Instructions (PIs): <?KEYWORD ... ?>
#
# Not currently supported:
# INCLUDE and IGNORE directives: <!KEYWORD[ ... ]]>
# CDATA sections: <![CDATA[ ... ]]>
#

class XMLItem(object):
	"""
	All PyAtom classes inherit from this class.  All it does is provide a
	few default methods, and be a root for the inheritance tree.

	An XMLItem has several methods that return an XML tag representation of
	its contents.  Each XMLItem knows how to make a tag for itself.  An
	XMLItem that contains other XMLItems will ask each one to make a tag;
	so asking the top-level XMLItem for a tag will cause the entire tree
	of XMLItems to recursively make tags, and you get a full XML
	representation with tags appropriately nested and indented.
	"""
	def _s_tag(self, tfc):
		"""
		A stub which must always be overridden by child classes.
		"""
		assert False, "XMLItem instance is too abstract to print."

	def s_tag(self, level):
		"""
		Return the item as a string containing an XML tag declaration.

		The XML tag will be indented.
		Will return an empty string if the item is empty.
		"""
		tfc = TFC(level, TFC.mode_normal)
		return self._s_tag(tfc)

	def s_tag_verbose(self, level):
		"""
		Return the item as a string containing an XML tag declaration.

		The XML tag will be indented.
		May return an XML Comment if the item is empty.
		"""
		tfc = TFC(level, TFC.mode_verbose)
		return self._s_tag(tfc)

	def s_tag_terse(self, level):
		"""
		Return the item as a string containing an XML tag declaration.

		The XML tag will not be indented.
		Will return an empty string if the item is empty.
		"""
		tfc = TFC(level, TFC.mode_terse)
		return self._s_tag(tfc)

	def __str__(self):
		return self.s_tag(0)

	def level(self):
		"""
		Return an integer describing what level this tag is.

		The root tag of an XML document is level 0; document-level comments
		or other document-level declarations are also level 0.  Tags nested
		inside the root tag are level 1, tags nested inside those tags are
		level 2, and so on.

		This is currently only used by the s_tree() functions.  When
		printing tags normally, the code that walks the tree keeps track of
		what level is current.
		"""
		level = 0
		while self._parent != None:
			self = self._parent
			if self.is_element():
				level += 1
		return level

	def s_name(self):
		"""
		Return a name for the current item.

		Used only by the s_tree() functions.
		"""
		if self._name:
			return self._name
		return "unnamed_instance_of_" + type(self).__name__

	def s_tree(self):
		"""
		Return a verbose tree showing the current tag and its children.

		This is for debugging; it's not valid XML syntax.
		"""
		level = self.level()
		return "%2d) %s\t%s" % (level, self.s_name(), str(self))



class DocItem(XMLItem):
	"""
	A document-level XML item (appearing above root element).

	Items that can be document-level inherit from this class.
	"""
	pass



class ElementItem(XMLItem):
	"""
	An item that may be nested inside an element.

	Items that can be nested inside other elements inherit from this class.
	"""
	pass



class Comment(DocItem,ElementItem):
	"""
	An XML comment.

	Attributes:
		text
			set the text of the comment
	"""
	def __init__(self, text=""):
		"""
		text: set the text of the comment
		"""
		self._parent = None
		self._name = ""
		self.tag_name = "comment"
		self.text = text

	def _s_tag(self, tfc):
		if not self:
			if tfc.b_print_all():
				return tfc.s_indent() + "<!-- -->"
			else:
				return ""
		else:
			if self.text.find("\n") >= 0:
				lst = []
				lst.append(tfc.s_indent() + "<!--")
				lst.append(self.text)
				lst.append(tfc.s_indent() + "-->")
				return "\n".join(lst)
			else:
				s = "%s%s%s%s" % (tfc.s_indent(), "<!-- ", self.text, " -->")
				return s

		assert(False, "not possible to reach this line.")

	def __nonzero__(self):
		# Returns True if there is any comment text.
		# Returns False otherwise.
		return not not self.text

	def is_element(self):
		return True



# REVIEW: can a PI be an ElementItem?
class PI(DocItem):
	"""
	XML Processing Instruction (PI).

	Attributes:
		keyword
		text
	"""
	def __init__(self):
		self._parent = None
		self._name = ""
		self.keyword = ""
		self.text = ""

	def _s_tag(self, tfc):
		if not self:
			return ""
		else:
			if self.text.find("\n") >= 0:
				lst = []
				lst.append("%s%s%s" % (tfc.s_indent(), "<?", self.keyword))
				lst.append(self.text)
				lst.append("%s%s" % (tfc.s_indent(), "?>"))
				return "\n".join(lst)
			else:
				s = "%s%s%s %s%s"% \
						(tfc.s_indent(), "<?", self.keyword, self.text, "?>")
				return s

		assert(False, "not possible to reach this line.")

	def __nonzero__(self):
		# Returns True if there is any keyword.
		# Returns False otherwise.
		return not not self.keyword



# REVIEW: can a MarkupDecl be an ElementItem?
class MarkupDecl(DocItem):
	"""
	XML Markup Declaration.

	Attributes:
		keyword
		text
	"""
	def __init__(self):
		self._parent = None
		self._name = ""
		self.keyword = ""
		self.text = ""

	def _s_tag(self, tfc):
		if not self:
			return ""
		else:
			if self.text.find("\n") >= 0:
				lst = []
				lst.append("%s%s%s" % (tfc.s_indent(), "<!", self.keyword))
				lst.append(self.text)
				lst.append("%s%s" % (tfc.s_indent(), ">"))
				return "\n".join(lst)
			else:
				s = "%s%s%s %s%s" % \
						(tfc.s_indent(), "<!", self.keyword, self.text, ">")
				return s

		assert(False, "not possible to reach this line.")

	def __nonzero__(self):
		# Returns True if there is any keyword.
		# Returns False otherwise.
		return not not self.keyword



class CoreElement(ElementItem):
	"""
	This is an abstract class.

	All of the XML element classes inherit from this.
	"""
	def __init__(self, tag_name, def_attr, def_attr_value, attr_names = []):
		# dictionary of attributes and their values
		self.lock = False
		self._parent = None
		self._name = ""
		self.tag_name = tag_name
		self.def_attr = def_attr
		self.attrs = {}
		if def_attr and def_attr_value:
			self.attrs[def_attr] = def_attr_value
		self.attr_names = attr_names
		self.lock = True

	def __nonzero__(self):
		# Returns True if any attrs are set or there are any contents.
		# Returns False otherwise.
		return not not self.attrs or self.has_contents()

	def text_check(self):
		"""
		Raise an exception, unless element has text contents.

		Child classes that have text must override this to do nothing.
		"""
		raise TypeError, "element does not have text contents"

	def nest_check(self):
		"""
		Raise an exception, unless element can nest other elements.

		Child classes that can nest must override this to do nothing.
		"""
		raise TypeError, "element cannot nest other elements"

	def __delattr__(self, name):
		# REVIEW: this should be made to work!
		raise TypeError, "cannot delete elements"

	def __getattr__(self, name):
		if name == "lock":
			# If the "lock" hasn't been created yet, we always want it
			# to be False, i.e. we are not locked.
			return False
		else:
			raise AttributeError, name

	def __setattr__(self, name, value):
		# Here's how this works:
		#
		# 0) "self.lock" is a boolean, set to False during __init__()
		# but turned True afterwards.  When it's False, you can add new
		# members to the class instance without any sort of checks; once
		# it's set True, __setattr__() starts checking assignments.
		# By default, when lock is True, you cannot add a new member to
		# the class instance, and any assignment to an old member has to
		# be of matching type.  So if you say "a.text = string", the
		# .text member has to exist and be a string member.
		#
		# This is the default __setattr__() for all element types.  It
		# gets overloaded by the __setattr__() in NestElement, because
		# for nested elments, it makes sense to be able to add new
		# elements nested inside.
		#
		# This is moderately nice.  But later in NestElement there is a
		# version of __setattr__() that is *very* nice; check it out.
		#
		# 1) This checks assignments to _parent, and makes sure they are
		# plausible (either an XMLItem, or None).

		try:
			lock = self.lock
		except AttributeError:
			lock = False

		if not lock:
			self.__dict__[name] = value
			return

		dict = self.__dict__
		if not name in dict:
			# brand-new item
			if lock:
				raise TypeError, "element cannot nest other elements"

		if name == "_parent":
			if not (isinstance(value, XMLItem) or value is None):
				raise TypeError, "only XMLItem or None is permitted"
			self.__dict__[name] = value
			return

		# locked item so do checks
		if not type(self.__dict__[name]) is type(value):
			raise TypeError, "value is not the same type"

		self.__dict__[name] = value
		

	def has_contents(self):
		return False

	def multiline_contents(self):
		return False

	def s_contents(self, tfc):
		assert False, "CoreElement is an abstract class; it has no contents."

	def _s_start_tag_name_attrs(self, tfc):
		"""
		Return a string with the start tag name, and any attributes.

		Wrap this in correct punctuation to get a start tag.
		"""
		def attr_newline(tfc):
			if tfc.b_print_terse():
				return " "
			else:
				return "\n" + tfc.s_indent(2)

		lst = []
		lst.append(self.tag_name)

		if len(self.attrs) == 1:
			# just one attr so do on one line
			attr = self.attrs.keys()[0]
			s_attr = '%s="%s"' % (attr, self.attrs[attr])
			lst.append(" " + s_attr)
		elif len(self.attrs) > 1:
			# more than one attr so do a nice nested tag
			# 0) show all attrs in the order of attr_names
			for attr in self.attr_names:
				if attr in self.attrs.keys():
					s_attr = '%s="%s"' % (attr, self.attrs[attr])
					lst.append(attr_newline(tfc) + s_attr)
			# 1) any attrs not in attr_names?  list them, too
			for attr in self.attrs:
				if not attr in self.attr_names:
					s_attr = '%s="%s"' % (attr, self.attrs[attr])
					lst.append(attr_newline(tfc) + s_attr)

		return "".join(lst)

	def _s_tag(self, tfc):
		if not self:
			if not tfc.b_print_all():
				return ""

		lst = []

		lst.append(tfc.s_indent() + "<" + self._s_start_tag_name_attrs(tfc))

		if not self.has_contents():
			lst.append("/>")
		else:
			lst.append(">")
			if self.multiline_contents():
				s = "\n%s\n" % self.s_contents(tfc.indent_by(1))
				lst.append(s + tfc.s_indent())
			else:
				lst.append(self.s_contents(tfc))
			lst.append("</" + self.tag_name + ">")

		return "".join(lst)

	def s_start_tag(self, tfc):
		return tfc.s_indent() + "<" + self._s_start_tag_name_attrs(tfc) + ">"

	def s_end_tag(self):
		return "</" + self.tag_name + ">"

	def s_compact_tag(self, tfc):
		return tfc.s_indent() + "<" + self._s_start_tag_name_attrs(tfc) + "/>"

	def is_element(self):
		return True



class TextElement(CoreElement):
	"""
	An element that cannot have other elements nested inside it.

	Attributes:
		attr
		text
	"""
	def __init__(self, tag_name, def_attr, def_attr_value, attr_names = []):
		CoreElement.__init__(self, tag_name, def_attr, def_attr_value,
				attr_names)
		self.lock = False
		self.text = ""
		self.lock = True

	def text_check(self):
		pass

	def has_contents(self):
		return not not self.text

	def multiline_contents(self):
		return self.text.find("\n") >= 0

	def s_contents(self, tfc):
		return self.text



class Nest(ElementItem):
	"""
	A data structure that can store Elements, nested inside it.

	Note: this is not, itself, an Element!  Because it is not an XML
	element, it has no tags.  Its string representation is the
	representations of the elements nested inside it.

	NestElement and XMLDoc inherit from this.
	"""
	def __init__(self):
		self.lock = False
		self._parent = None
		self._name = ""
		self.elements = []
		self.lock = True
	def __len__(self):
		return len(self.elements)
	def __getitem__(self, key):
		return self.elements[key]
	def __setitem__(self, key, value):
		self.elements[key] = value
	def __delitem__(self, key):
		del(self.elements[key])

	def _do_setattr(self, name, value):
		if isinstance(value, XMLItem):
			value._parent = self
			value._name = name
			self.elements.append(value)
		self.__dict__[name] = value

	def __setattr__(self, name, value):
		# Lots of magic here!  This is important stuff.  Here's how it works:
		#
		# 0) self.lock is a boolean, set to False initially and then set
		# to True at the end of __init__().  When it's False, you can add new
		# members to the class instance without any sort of checks; once
		# it's set True, __setattr__() starts checking assignments.  By
		# default, when lock is True, any assignment to an old member
		# has to be of matching type.  You can add a new member to the
		# class instance, but __setattr__() checks to ensure that the
		# new member is an XMLItem.
		#
		# 1) Whether self.lock is set or not, if the value is an XMLitem,
		# then this will properly add the XMLItem into the tree
		# structure.  The XMLItem will have _parent set to the parent,
		# will have _name set to its name in the parent, and will be
		# added to the parent's elements list.  This is handled by
		# _do_setattr().
		#
		# 2) As a convenience for the user, if the user is assigning a
		# string, and self is an XMLItem that has a .text value, this
		# will assign the string to the .text value.  This allows usages
		# like "e.title = string", which is very nice.  Before I added
		# this, I frequently wrote that instead of "e.title.text =
		# string" so I wanted it to just work.  Likewise the user can
		# assign a time value directly into Timestamp elements.
		#
		# 3) This checks assignments to _parent, and makes sure they are
		# plausible (either an XMLItem, or None).

		try:
			lock = self.lock
		except AttributeError:
			lock = False

		if not lock:
			self._do_setattr(name, value)
			return

		dict = self.__dict__
		if not name in dict:
			# brand-new item
			if lock:
				self.nest_check()
				if not isinstance(value, XMLItem):
					raise TypeError, "only XMLItem is permitted"
			self._do_setattr(name, value)
			return

		if name == "_parent" or name == "root_element":
			if not (isinstance(value, XMLItem) or value is None):
				raise TypeError, "only XMLItem or None is permitted"
			self.__dict__[name] = value
			return

		if name == "_name" and type(value) == type(""):
			self.__dict__[name] = value
			return

		# for Timestamp elements, allow this:  element = time
		# (where "time" is a float value, since uses float for times)
		# Also allow valid timestamp strings.
		if isinstance(self.__dict__[name], Timestamp):
			if type(value) == type(1.0):
				self.__dict__[name].time = value
				return
			elif type(value) == type(""):
				t = utc_time_from_s_timestamp(value)
				if t:
					self.__dict__[name].time = t
				else:
					raise ValueError, "value must be a valid timestamp string"
				return

		# Allow string assignment to go to the .text attribute, for
		# elements that allow it.  All TextElements allow it;
		# Elements will allow it if they do not nave nested elements.
		# text_check() raises an error if it's not allowed.
		if isinstance(self.__dict__[name], CoreElement) and \
				type(value) == type(""):
			self.__dict__[name].text_check()
			self.__dict__[name].text = value
			return

		# locked item so do checks
		if not type(self.__dict__[name]) is type(value):
			raise TypeError, "value is not the same type"

		self.__dict__[name] = value
		
	def __delattr__(self, name):
		# This won't be used often, if ever, but if anyone tries it, it
		# should work.
		if isinstance(self.name, XMLItem):
			o = self.__dict__[name]
			self.elements.remove(o)
			del(self.__dict__[name])
		else:
			# REVIEW: what error should this raise?
			raise TypeError, "cannot delete that item"

	def nest_check(self):
		pass

	def is_element(self):
		# a Nest is not really an element
		return False

	def has_contents(self):
		for element in self.elements:
			if element:
				return True
		# empty iff all of the elements were empty
		return False

	def __nonzero__(self):
		return self.has_contents()

	def multiline_contents(self):
		# if there are any contents, we want multiline for nested tags
		return self.has_contents()

	def s_contents(self, tfc):
		if len(self.elements) > 0:
			# if any nested elements exist, we show those
			lst = []

			for element in self.elements:
				s = element._s_tag(tfc)
				if s:
					lst.append(s)

			return "\n".join(lst)
		else:
			return ""

		assert(False, "not possible to reach this line.")
		return ""

	def s_tree(self):
		level = self.level()
		tup = (level, self.s_name(), self.__class__.__name__)
		s = "%2d) %s (instance of %s)" % tup
		lst = []
		lst.append(s)
		for element in self.elements:
			s = element.s_tree()
			lst.append(s)
		return "\n".join(lst)

	def _s_tag(self, tfc):
		return self.s_contents(tfc)




class NestElement(Nest,CoreElement):
	"""
	An element that can have other elements nested inside it.

	Attributes:
		attr
		elements: a list of other elements nested inside this one.
	"""
	def __init__(self, tag_name, def_attr, def_attr_value, attr_names=[]):
		CoreElement.__init__(self, tag_name, def_attr, def_attr_value,
				attr_names)
		self.lock = False
		self.elements = []
		self.lock = True

	def is_element(self):
		return True

	def __nonzero__(self):
		return CoreElement.__nonzero__(self)

	def _s_tag(self, tfc):
		return CoreElement._s_tag(self, tfc)



class Element(NestElement,TextElement):
	"""
	A class to represent an arbitrary XML tag.  Can either have other XML
	elements nested inside it, or else can have a text string value, but
	never both at the same time.

	This is intended for user-defined XML tags.  The user can just use
	"Element" for all custom tags.

	PyAtom doesn't use this; PyAtom uses TextElement for tags with a text
	string value, and NestElement for tags that nest other elements.  Users
	can do the same, or can just use Element, as they like.

	Attributes:
		attr
		elements:	a list of other elements nested inside, if any
		text:	a text string value, if any

	Note: if text is set, elements will be empty, and vice-versa.  If you
	have elements nested inside and try to set the .text, this will raise
	an exception, and vice-versa.
	"""
	# A Element can have other elements nested inside it, or it can have
	# a single ".text" string value.  But never both at the same time.
	# Once you nest another element, you can no longer use the .text.
	def __init__(self, tag_name, def_attr, def_attr_value, attr_names=[]):
		NestElement.__init__(self, tag_name, def_attr, def_attr_value,
				attr_names)
		self.lock = False
		self.text = ""
		self.lock = True

	def nest_check(self):
		if self.text:
			raise TypeError, "Element has text contents so cannot nest"

	def text_check(self):
		if len(self.elements) > 0:
			raise TypeError, "Element has nested elements so cannot assign text"

	def has_contents(self):
		return NestElement.has_contents(self) or TextElement.has_contents(self)

	def multiline_contents(self):
		return NestElement.has_contents(self) or self.text.find("\n") >= 0

	def s_contents(self, tfc):
		if len(self.elements) > 0:
			return NestElement.s_contents(self, tfc)
		elif self.text:
			return TextElement.s_contents(self, tfc)
		else:
			return ""
		assert(False, "not possible to reach this line.")

	def s_tree(self):
		lst = []
		if len(self.elements) > 0:
			level = self.level()
			tup = (level, self.s_name(), self.__class__.__name__)
			s = "%2d) %s (instance of %s)" % tup
			lst.append(s)
			for element in self.elements:
				s = element.s_tree()
				lst.append(s)
			return "\n".join(lst)
		elif self.text:
			return XMLItem.s_tree(self)
		else:
			level = self.level()
			tfc = TFC(level)
			s = "%2d) %s %s" % (level, self.s_name(), "empty Element...")
			return s
		assert(False, "not possible to reach this line.")



class Collection(XMLItem):
	"""
	A Collection contains 0 or more Elements, but isn't an XML element.
	Use where a run of 0 or more Elements of the same type is legal.

	When you init your Collection, you specify what class of Element it will
	contain.  Attempts to append an Element of a different class will raise
	an exception.  Note, however, that the various Element classes all
	inherit from base classes, and you can specify a class from higher up in
	the inheritance tree.  You could, if you wanted, make a Collection
	containing "XMLItem" and then any item defined in PyAtom would be legal
	in that collection.  (See XMLDoc, which contains two collections of
	DocItem.)

	Attributes:
		contains:	the class of element this Collection will contain
		elements:	a list of other elements nested inside, if any

	Note: The string representation of a Collection is just the string
	representations of the elements inside it.  However, a verbose string
	reprentation may have an XML comment like this:

	<!-- Collection of <class> with <n> elements -->

	where <n> is the number of elements in the Collection and <class> is the
	name of the class in this Collection.
	"""
	def __init__(self, element_class):
		self.lock = False
		self._parent = None
		self._name = ""
		self.elements = []
		self.contains = element_class
		self.lock = True
	def __len__(self):
		return len(self.elements)
	def __getitem__(self, key):
		return self.elements[key]
	def __setitem__(self, key, value):
		if not isinstance(value, self.contains):
			raise TypeError, "object is the wrong type for this collection"
		self.elements[key] = value
	def __delitem__(self, key):
		del(self.elements[key])

	def __nonzero__(self):
		# there are no attrs so if any element is nonzero, collection is too
		for element in self.elements:
			if element:
				return True
		return False

	def is_element(self):
		# A Collection is not really an Element
		return False

	def s_coll(self):
		name = self.contains.__name__
		n = len(self.elements)
		if n == 1:
			el = "element"
		else:
			el = "elements"
		return "collection of %s with %d %s" % (name, n, el)

	def append(self, element):
		if not isinstance(element, self.contains):
			print >> sys.stderr, "Error: attempted to insert", \
					type(element).__name__, \
					"into collection of", self.contains.__name__
			raise TypeError, "object is the wrong type for this collection"
		element._parent = self
		self.elements.append(element)

	def _s_tag(self, tfc):
		# A collection exists only as a place to put real elements.
		# There are no start or end tags...
		# When tfc.b_print_all() is true, we do put an XML comment.

		if not self.elements:
			if not tfc.b_print_all():
				return ""

		lst = []

		if tfc.b_print_verbose():
			s = "%s%s%s%s" % (tfc.s_indent(), "<!-- ", self.s_coll(), " -->")
			lst.append(s)
			tfc = tfc.indent_by(1)

		for element in self.elements:
			s = element._s_tag(tfc)
			if s:
				lst.append(s)

		return "\n".join(lst)

	def s_tree(self):
		level = self.level()
		s = "%2d) %s %s" % (level, self.s_name(), self.s_coll())
		lst = []
		lst.append(s)
		for element in self.elements:
			s = element.s_tree()
			lst.append(s)
		return "\n".join(lst)



class XMLDeclaration(XMLItem):
	# REVIEW: should this print multi-line for multiple attrs?
	def __init__(self):
		self._parent = None
		self._name = ""
		self.attrs = {}
		self.attrs[s_version] = "1.0"
		self.attrs[s_encoding] = "utf-8"
		self.attr_names = [s_version, s_encoding, s_standalone]

	def _s_tag(self, tfc):
		# An XMLDeclaration() instance is never empty, so always prints.

		lst = []
		s = "%s%s" % (tfc.s_indent(), "<?xml")
		lst.append(s)
		# 0) show all attrs in the order of attr_names
		for attr in self.attr_names:
			if attr in self.attrs.keys():
				s_attr = ' %s="%s"' % (attr, self.attrs[attr])
				lst.append(s_attr)
		# 1) any attrs not in attr_names?  list them, too
		for attr in self.attrs:
			if not attr in self.attr_names:
				s_attr = ' %s="%s"' % (attr, self.attrs[attr])
				lst.append(s_attr)
		lst.append("?>")

		return "".join(lst)

	def __nonzero__(self):
		# Returns True because the XML Declaration is never empty.
		return True

	def is_element(self):
		return True



class XMLDoc(Nest):
	"""
	A data structure to represent an XML Document.  It will have the
	following structure:

	the XML Declaration item
	0 or more document-level XML items
	exactly one XML item (the "root tag")
	0 or more document-level XML items

	document level XML items are: Comment, PI, MarkupDecl


	Attributes:
		xml_decl:	the XMLDeclaration item
		docitems_above:	a collection of DocItem (items above root_element)
		root_element:	the XML tag containing your data
		docitems_below:	a collection of DocItem (items below root_element)

	Note: usually the root_element has lots of other XML items nested inside
	it!
	"""
	def __init__(self, root_element=None):
		Nest.__init__(self)

		self._name = "XMLDoc"

		self.xml_decl = XMLDeclaration()
		self.docitems_above = Collection(DocItem)

		if not root_element:
			root_element = Comment("no root element yet")
		self.root_element = root_element

		self.docitems_below = Collection(DocItem)

	def __setattr__(self, name, value):
		# root_element may always be set to any ElementItem
		if name == "root_element":
			if not (isinstance(value, ElementItem)):
				raise TypeError, "only ElementItem is permitted"

			self.lock = False
			# Item checks out, so assign it.  root_element should only
			# ever have one element, and we always put the new element
			# in the same slot in elements[].
			if "i_root_element" in self.__dict__:
				# Assign new root_element over old one in elements[]
				assert self.elements[self.i_root_element] == self.root_element
				self.elements[self.i_root_element] = value
			else:
				# This is the first time root_element was ever set.
				self.i_root_element = len(self.elements)
				self.elements.append(value)

			value._parent = self
			value._name = name
			self.__dict__[name] = value
			self.lock = True
		else:
			# for all other, fall through to inherited behavior
			Nest.__setattr__(self, name, value)

	def Validate(self):
		# XMLDoc never has parent.  Never change this!
		assert self._parent == None
		return True



def local_time_from_utc_time(t):
	return t - time.timezone

def utc_time_from_local_time(t):
	return t + time.timezone

def local_time():
	return time.time() - time.timezone

def utc_time():
	return time.time()


class TimeSeq(object):
	"""
	A class to generate a sequence of timestamps.

	Atom feed validators complain if multiple timestamps have the same
	value, so this provides a convenient way to set a bunch of timestamps
	all at least one second different from each other.
	"""
	def __init__(self, init_time=0):
		if init_time == 0:
			self.time = local_time()
		else:
			self.time = float(init_time)
	def next(self):
		t = self.time
		self.time += 1.0
		return t

format_RFC3339 = "%Y-%m-%dT%H:%M:%S"

def parse_time_offset(s):
	s = s.lstrip().rstrip()

	if (s == '' or s == 'Z' or s == 'z'):
		return 0

	m = pat_time_offset.search(s)
	sign = m.group(1)
	offset_hour = int(m.group(2))
	offset_min = int(m.group(3))
	offset = offset_hour * 3600 + offset_min * 60
	if sign == "-":
		offset *= -1
	return offset

def s_timestamp(utc_time, time_offset="Z"):
	"""
	Format a time and offset into a string.

	utc_time
		a floating-point value, time in the UTC time zone
	s_time_offset
		a string specifying an offset from UTC.  Examples:
			z or Z -- offset is 0 ("Zulu" time, UTC, aka GMT)
			-08:00 -- 8 hours earlier than UTC (Pacific time zone)
			"" -- empty string is technically not legal, but may work

	Notes:
		Returned string complies with RFC3339; uses ISO8601 date format.
		Example: 2003-12-13T18:30:02Z
		Example: 2003-12-13T18:30:02+02:00
	"""

	if not utc_time:
		return ""

	utc_time += parse_time_offset(time_offset)

	try:
		s = time.strftime(format_RFC3339, time.localtime(utc_time))
	except:
		return ""

	return s + time_offset



pat_RFC3339 = re.compile("(\d\d\d\d)-(\d\d)-(\d\d)T(\d\d):(\d\d):(\d\d)(.*)")
pat_time_offset = re.compile("([+-])(\d\d):(\d\d)")

def utc_time_from_s_timestamp(s_date_time_stamp):
	# parse RFC3339-compatible times that use ISO8601 date format
	# date time stamp example: 2003-12-13T18:30:02Z
	# date time stamp example: 2003-12-13T18:30:02+02:00
	# leaving off the suffix is technically not legal, but allowed

	s_date_time_stamp = s_date_time_stamp.lstrip().rstrip()

	try:
		m = pat_RFC3339.search(s_date_time_stamp)
		year = int(m.group(1))
		mon = int(m.group(2))
		mday = int(m.group(3))
		hour = int(m.group(4))
		min = int(m.group(5))
		sec = int(m.group(6))
		tup = (year, mon, mday, hour, min, sec, -1, -1, -1)
		t = time.mktime(tup)

		s = m.group(7)
		t += parse_time_offset(s)

		return t

	except:
		return 0.0

	assert False, "impossible to reach this line"


def s_time_offset():
	"""
	Return a string with local offset from UTC in RFC3339 format.
	"""

	# If t is set to local time in seconds since the epoch, then...
	# ...offset is the value you add to t to get UTC.  This is the
	# reverse of time.timezone.

	offset = -(time.timezone)

	if offset > 0:
		sign = "+"
	else:
		sign = "-"
		offset = abs(offset)

	offset_hour = offset // (60 * 60)
	offset_min = (offset // 60) % 60
	return "%s%02d:%02d" % (sign, offset_hour, offset_min)

s_offset_local = s_time_offset()

s_offset_default = s_offset_local

def set_default_time_offset(s):
	global s_offset_default
	s_offset_default = s


class Timestamp(CoreElement):
	def __init__(self, tag_name, time=0.0):
		CoreElement.__init__(self, tag_name, None, None)
		self.lock = False
		self.time = time
		self.time_offset = s_offset_default
		self.lock = True

	def __delattr__(self, name):
		CoreElement.__delattr_(self, name)

	def __getattr__(self, name):
		if name == "text":
			return s_timestamp(self.time, self.time_offset)
		return CoreElement.__getattr_(self, name)

	def __setattr__(self, name, value):
		if name == "text":
			if type(value) != type(""):
				raise TypeError, "can only assign a string to .text"
			t = utc_time_from_s_timestamp(value)
			if t:
				self.time = utc_time_from_s_timestamp(value)
			else:
				raise ValueError, "value must be a valid timestamp string"
			return
		CoreElement.__setattr__(self, name, value)

	def has_contents(self):
		return self.time != 0

	def multiline_contents(self):
		return False

	def s_contents(self, tfc):
		return s_timestamp(self.time, self.time_offset)

	def update(self):
		self.time = local_time()
		return self




# Below are all the classes to implement Atom using the above tools.



class AtomText(TextElement):
	def __init__(self, tag_name):
		attr_names = [ s_type ]
		# legal values of type: "text", "html", "xhtml"
		TextElement.__init__(self, tag_name, None, None, attr_names)

class Title(AtomText):
	def __init__(self, text=""):
		AtomText.__init__(self, "title")
		self.text = text
		
class Subtitle(AtomText):
	def __init__(self, text=""):
		AtomText.__init__(self, "subtitle")
		self.text = text
		
class Content(AtomText):
	def __init__(self, text=""):
		AtomText.__init__(self, "content")
		self.text = text
		
class Summary(AtomText):
	def __init__(self, text=""):
		AtomText.__init__(self, "summary")
		self.text = text
		
class Rights(AtomText):
	def __init__(self, text=""):
		AtomText.__init__(self, "rights")
		self.text = text
		
class Id(TextElement):
	def __init__(self, text=""):
		TextElement.__init__(self, "id", None, None)
		self.text = text
		
class Generator(TextElement):
	def __init__(self):
		attr_names = [ "uri", "version" ]
		TextElement.__init__(self, "generator", None, None, attr_names)
		
class Category(TextElement):
	def __init__(self, term_val=""):
		attr_names = [s_term, "scheme", "label"]
		TextElement.__init__(self, "category", s_term, term_val, attr_names)

class Link(TextElement):
	def __init__(self, href_val=""):
		attr_names = [
				s_href, "rel", "type", "hreflang", "title", "length", s_lang]
		TextElement.__init__(self, "link", s_href, href_val, attr_names)

class Icon(TextElement):
	def __init__(self):
		TextElement.__init__(self, "icon", None, None)

class Logo(TextElement):
	def __init__(self):
		TextElement.__init__(self, "logo", None, None)

class Name(TextElement):
	def __init__(self, text=""):
		TextElement.__init__(self, "name", None, None)
		self.text = text

class Email(TextElement):
	def __init__(self):
		TextElement.__init__(self, "email", None, None)

class Uri(TextElement):
	def __init__(self):
		TextElement.__init__(self, "uri", None, None)



class BasicAuthor(NestElement):
	def __init__(self, tag_name, name):
		NestElement.__init__(self, tag_name, None, None)
		self.name = Name(name)
		self.email = Email()
		self.uri = Uri()

class Author(BasicAuthor):
	def __init__(self, name=""):
		BasicAuthor.__init__(self, "author", name)

class Contributor(BasicAuthor):
	def __init__(self, name=""):
		BasicAuthor.__init__(self, "contributor", name)



class Updated(Timestamp):
	def __init__(self, time=0.0):
		Timestamp.__init__(self, "updated", time)

class Published(Timestamp):
	def __init__(self, time=0.0):
		Timestamp.__init__(self, "published", time)



class FeedElement(NestElement):
	def __init__(self, tag_name):
		NestElement.__init__(self, tag_name, None, None)

		self.title = Title("")
		self.id = Id("")
		self.updated = Updated()
		self.authors = Collection(Author)
		self.links = Collection(Link)

		self.subtitle = Subtitle("")
		self.categories = Collection(Category)
		self.contributors = Collection(Contributor)
		self.generator = Generator()
		self.icon = Icon()
		self.logo = Logo()
		self.rights = Rights("")

class Feed(FeedElement):
	def __init__(self):
		FeedElement.__init__(self, "feed")
		self.attrs["xmlns"] = "http://www.w3.org/2005/Atom"
		self.title.text = "Title of Feed Goes Here"
		self.id.text = "ID of Feed Goes Here"
		self.entries = Collection(Entry)

class Source(FeedElement):
	def __init__(self):
		FeedElement.__init__(self, "source")



class Entry(NestElement):
	def __init__(self):
		NestElement.__init__(self, "entry", None, None)
		self.title = Title("Title of Entry Goes Here")
		self.id = Id("ID of Entry Goes Here")
		self.updated = Updated()
		self.authors = Collection(Author)
		self.links = Collection(Link)

		self.content = Content("")
		self.summary = Summary("")
		self.categories = Collection(Category)
		self.contributors = Collection(Contributor)
		self.published = Published()
		self.source = Source()
		self.rights = Rights("")



def diff(s0, name0, s1, name1):
	from difflib import ndiff
	lst0 = s0.split("\n")
	lst1 = s1.split("\n")
	report = '\n'.join(ndiff(lst0, lst1))
	return report


def run_test_cases():

	# The default is to make time stamps in local time with appropriate
	# offset; for our tests, we want a default "Z" offset instead.
	set_default_time_offset("Z")

	failed_tests = 0


	# Test: convert current time into a timestamp string and back

	now = local_time()
	# timestamp format does not allow fractional seconds
	now = float(int(now))	# truncate any fractional seconds
	s = s_timestamp(now)
	t = utc_time_from_s_timestamp(s)
	if now != t:
		failed_tests += 1
		print "test case failed:"
		print now, "-- original timestamp"
		print t, "-- converted timestamp does not match"


	# Test: convert a timestamp string to a time value and back

	s_time = "2003-12-13T18:30:02Z"
	t = utc_time_from_s_timestamp(s_time)
	s = s_timestamp(t)
	if s_time != s:
		failed_tests += 1
		print "test case failed:"
		print s_time, "-- original timestamp"
		print s, "-- converted timestamp does not match"


	# Test: generate the "Atom-Powered Robots Run Amok" example
	#
	# Note: the original had some of the XML declarations in
	# a different order than PyAtom puts them.  I swapped around
	# the lines here so they would match the PyAtom order.  Other
	# than that, this is the example from:
	#
	# http://www.atomenabled.org/developers/syndication/#sampleFeed

	s_example = """\
<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
	<title>Example Feed</title>
	<id>urn:uuid:60a76c80-d399-11d9-b93C-0003939e0af6</id>
	<updated>2003-12-13T18:30:02Z</updated>
	<author>
		<name>John Doe</name>
	</author>
	<link href="http://example.org/"/>
	<entry>
		<title>Atom-Powered Robots Run Amok</title>
		<id>urn:uuid:1225c695-cfb8-4ebb-aaaa-80da344efa6a</id>
		<updated>2003-12-13T18:30:02Z</updated>
		<link href="http://example.org/2003/12/13/atom03"/>
		<summary>Some text.</summary>
	</entry>
</feed>"""

	xmldoc = XMLDoc()
	
	feed = Feed()
	xmldoc.root_element = feed

	feed.title = "Example Feed"
	feed.id = "urn:uuid:60a76c80-d399-11d9-b93C-0003939e0af6"
	feed.updated = "2003-12-13T18:30:02Z"

	link = Link("http://example.org/")
	feed.links.append(link)

	author = Author("John Doe")
	feed.authors.append(author)


	entry = Entry()
	feed.entries.append(entry)
	entry.id = "urn:uuid:1225c695-cfb8-4ebb-aaaa-80da344efa6a"
	entry.title = "Atom-Powered Robots Run Amok"
	entry.updated = "2003-12-13T18:30:02Z"
	entry.summary = "Some text."

	link = Link("http://example.org/2003/12/13/atom03")
	entry.links.append(link)


	s = str(xmldoc)
	if s_example != s:
		failed_tests += 1
		print "test case failed:"
		print "The generated XML doesn't match the example.  diff follows:"
		print diff(s_example, "s_example", s, "s")


	# Test: verify that xmldoc.Validate() succeeds

	if not xmldoc.Validate():
		failed_tests += 1
		print "test case failed:"
		print "xmldoc.Validate() failed."


	# Test: does Element work both nested an non-nested?
	s_test = """\
<test>
	<test:agent number="007">James Bond</test:agent>
	<test:pet
			nickname="Mei-Mei"
			type="cat">Matrix</test:pet>
</test>"""

	class TestPet(Element):
		def __init__(self, name=""):
			Element.__init__(self, "test:pet", None, None)
			self.text = name

	class TestAgent(Element):
		def __init__(self, name=""):
			Element.__init__(self, "test:agent", None, None)
			self.text = name

	class Test(Element):
		def __init__(self):
			Element.__init__(self, "test", None, None)
			self.test_agent = TestAgent()
			self.test_pet = TestPet()

	test = Test()
	test.test_agent = "James Bond"
	test.test_agent.attrs["number"] = "007"
	test.test_pet = "Matrix"
	test.test_pet.attrs["type"] = "cat"
	test.test_pet.attrs["nickname"] = "Mei-Mei"

	s = str(test)
	if s_test != s:
		failed_tests += 1
		print "test case failed:"
		print "test output doesn't match.  diff follows:"
		print diff(s_test, "s_test", s, "s")


	if failed_tests > 0:
		print "self-test failed!"
	else:
		print "self-test successful."



if __name__ == "__main__":
	run_test_cases()
