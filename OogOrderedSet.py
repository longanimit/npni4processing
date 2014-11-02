
# -*- coding: utf8-*-
# coding: utf-8
__author__	=	"Dominique Dutoit"
__date__ 	=	"$5 march 2014$"

from collections import MutableSet

class OrderedSet(MutableSet):

	def __init__(self, iterable=None):
		self.end = end = [] 
		end += [None, end, end]		 # sentinel node for doubly linked list
		self.map = {}		# key --> [key, prev, next]
		if iterable is not None:
			self |= iterable
	def __len__(self):
		return len(self.map)

	def __contains__(self, key):
		return key in self.map

	def add(self, key):
		if key not in self.map:
			end = self.end
			curr = end[1]
			curr[2] = end[1] = self.map[key] = [key, curr, end]

	def discard(self, key):
		if key in self.map:		
			key, prev, next = self.map.pop(key)
			prev[2] = next
			next[1] = prev

	def __iter__(self):
		end = self.end
		curr = end[2]
		while curr is not end:
			yield curr[0]
			curr = curr[2]
	
	"""def __getslice__(self, x, y):
		'''x>=0 & y>=0...'''
		if x>len(self) or y <= x : return []
		count=-1 ; res = []
		for i in self.__iter__():
			count+=1
			if x > count : continue
			elif y <= count : break
			else: res.append(i)
		return res"""
		
	def __reversed__(self):
		end = self.end
		curr = end[1]
		while curr is not end:
			yield curr[0]
			curr = curr[1]

	def pop(self, last=True):
		if not self:
			raise KeyError('set is empty')
		key = self.end[1][0] if last else self.end[2][0]
		self.discard(key)
		return key

	def __repr__(self):
		if not self:
			return '%s()' % (self.__class__.__name__,)
		return '%s(%r)' % (self.__class__.__name__, list(self))

	def __eq__(self, other):
		if isinstance(other, OrderedSet):
			return len(self) == len(other) and list(self) == list(other)
		return set(self) == set(other)

			


if __name__ == '__main__':
	from time import clock
	s = OrderedSet('abracadaba')
	t = OrderedSet('simsbalabim')
	assert list(s) == ['a', 'b', 'r', 'c', 'd']
	assert list(s.__reversed__()) == ['d', 'c', 'r', 'b', 'a']
	assert len(s) == 5
	print '__iter__ and __ reversed : pass'
	assert s | t == OrderedSet(['a', 'b', 'r', 'c', 'd', 's', 'i', 'm', 'l'])
	assert s & t == OrderedSet(['b', 'a'])
	assert t & s == OrderedSet(['a', 'b']) #
	assert s - t == OrderedSet(['r', 'c', 'd'])
	print 'logical operators : pass'
	
	
	
	mylist = []
	for i in xrange(10000):
		[mylist.append(i) for j in xrange(int(i**0.3))]
	from random import shuffle
	shuffle(mylist)
	assert len(mylist) == 116864

	begin = clock()
	a=set()
	for i in mylist:
		a.add(i)
	assert len(a) == 9999
	setduration = clock()-begin
	print 'duration for ', a.__class__.__name__,  setduration
	
	
	a = OrderedSet()
	begin = clock()
	for i in  mylist:
		a.add(i)
	assert len(a) == 9999
	orderedsetduration = clock()-begin
	print 'duration for ', a.__class__.__name__, orderedsetduration
	
	#count=0
	#for i in a:
	#	print i, 
	#	count+=1
	#	if count>=10:break
	#print 
	#print a[0:10]
	from collections import defaultdict
	begin = clock()
	dico=defaultdict(OrderedSet)
	for i in mylist:
		dico['truc'].add(i)
	assert len(a) == 9999
	defaultdicduration = clock()-begin
	print 'duration for ', dico.__class__.__name__, defaultdicduration
	try:
		assert 2.5*setduration > orderedsetduration #python 2.7
	except: pass #pypy donne *10 parce que le set de base de pypy est beaucoup plus rapide
