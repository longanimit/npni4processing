
# -*- coding: utf8-*-
# coding: utf-8
__author__	=	"Dominique Dutoit"
__date__ 	=	"$November 1, 2014$"

''' Powerfull to index objects in memory, retreiving by parts.'''

'''
TODO
################## ARCHI #######################################
- fournir maxcountw ; par ex, algo syntaxe avec max = 1000 (1000 depend de la syntaxe)
  ce kwargs eliminine recursivement w et p
-  faire del p ( non recursif, un det est consomme, c le n qui est modfié dans l'objet )
- faire del w (ex : enlever un mot faux)

################## GENERATE DEEP PARTS #########################
# mise à plat de toutes les parties d'un w.

################## RETRIEVAL PART ##########################
#TODO : 
# all  cases :  implement full regex
# case type  : 
#    -- iterator retrieval DEEP W
#		tous les objets qui ont telle partie, same w, ie... en partant des parties d'un w, monter dans les w de ce w.
#    	tous les objets qui ont telles parties (idem mais avec plusieurs bases.)
# crossword and anagrams : add min/max size ; its functionally usefull, else, it could save time
# all cases : stopiteration at EVENT = count of tries in past or event == formal event.'''





from time import clock as npniclock
from collections import OrderedDict, Counter
from OogOrderedSet import OrderedSet
import re
from copy import copy as shallowcopy

class _RevOS_(OrderedSet):
	'''Cls Reversed OrderedSet.'''
	def __iter__(self) : return OrderedSet.__reversed__(self)
	def __reversed__(self) : return OrderedSet.__iter__(self)
	#def __repr__(self) : return self.__class__.__name__
	#def __str__(self) : return self.__class__.__name__
	
class _RevOD_(OrderedDict):
	'''Cls Reversed OrderedDict.'''
	def __iter__(self) : return OrderedDict.__reversed__(self)
	def __reversed__(self) : return OrderedDict.__iter__(self)
class _W2I_(_RevOD_):
	'''Private cls managing _RevOD_[p] = _RevS_([...w...]).'''
	
	def getset(self, w):
		try: return _RevOD_.__getitem__(self, w)
		except : pass
		if isinstance( w, basestring ) : 
			self[w] = _RevOS_( [w] ) #on considere toute basestring  w comme une instance d'elle meme : toute chaine est immutable
		else: self[w] = _RevOS_(  )
		return self[w] #w is added in attestations.

class NPNI4P(_W2I_):
	'''NPNI4P : single class NPNI for processing.'''
	crossword_star = '*'
	crossword_qmark = '?'
	regexchars = set ( [ '.', '^', '$', '*', '?', '+', '?', '\\', '|' ] ) 
	
	
	def w2p (self, w=None ):
		'''w2p is considered as a list of p, and index its parts, then consider itself as an s.'''
		def iterator4string( wstr):
			for p in wstr: 
				yield p
		if w in self: return
		self.getset(w) #cree self[w]= _RevOS_(  ) ou _RevOS_( [w] ) selon le cas.
		# TODO ??? AJOUTER LES MUTABLES DYNAMIQUES dict or list --> les considerer comme des atomes.
		if hasattr(w, '__iter__') and not len(w) == 0  : P = w.__iter__()
		elif isinstance(w, basestring) : P = iterator4string(w)
		else : return
		for p in P :
			self.getset(p).add(w)
	
	def w(self, w):
		'''w returns itself if exists, else returns None.'''
		if w in self: return w
		else: return None
	
	def iter_w(self, count = 100000000):
		'''iter_w(count) <--> self.iterkeys().
		default count = 100000000, then prefers  self.iterkeys() if everything is good.'''
		iterator = self.iterkeys()
		for i in xrange( count ):
			try: yield iterator.next()
			except StopIteration: break
		
	def iter_s(self, count = 100000000): 
		'''iter_s(count) returns self.iter_w(count).'''
		return self.iter_w( count)
		
	def l_w(self):
		'''l_w <--> self.keys()'''
		return self.keys()
		
	def l_s(self):
		'''l_s <--> self.keys()'''
		return self.keys()
		
	def s(self, s) :
		'''s consider first arg as set, and return itself, then return the containers w of its instances.'''
		yield self.w(s)
		for w in self.s2i( s ):
			yield w
	
	def s2i(self, s) :
		'''s2i returns strict instances containers of s.'''
		if not s in self:
			yield StopIteration
		else:
			for w in self[s]: 
				yield w
				
	def p(self, p):
		'''p considers p as a reference to a set, then returns self.s2i.'''
		return self.s2i(p)
	
	def w2i(self, w) :
		'''w2i considers w as a reference to a set, then returns self.s2i.'''
		return self.s2i(w)
		
	def last_w(self) :
		for w in self.iter_w():
			return w
		
	def get_domain_iterator(self, d_encode):
		if len( d_encode ) == 0: return self.iterkeys()
		l__len_k = []
		for k in d_encode.iterkeys():
			l__len_k.append( (len( self[k] ), k) )
		l__len_k.sort()
		k = l__len_k[0][1]
		return self[k]
		
	def encodew( self, w, d_encode):
		d_encode_local = shallowcopy(d_encode)
		l_res = []
		casestr = isinstance(w, basestring)
		for p in w:
			if p in d_encode_local:
				l_res.append( d_encode_local[p] )
				continue
			if isinstance (p , basestring )  and casestr == True: #sinon produira un join
				d_encode_local[p] = p
				l_res.append( p )
				continue
			else :
				d_encode_local[p] = unichr(len(d_encode_local)+128)
				l_res.append( d_encode_local[p] )
		res = ''.join([ d_encode_local[p] for p in w ])
		return res, d_encode_local

	def apply_regex(self, compiledq , d_encode):
		iterator_domain = self.get_domain_iterator(d_encode)
		for w in iterator_domain: 
			if isinstance(w, basestring):
				res = compiledq.match( w )
			else: 
				encodedw, d_encode_local = self.encodew( w, d_encode )
				#print w
				#print w, '--->', 'encodedw', repr(encodedw), 'encode_local', repr(d_encode_local)
				res = compiledq.match( encodedw )
			if res == None : continue
			#a = res.group(1)
			#print '"', a, '"', [ord(i) for i in a], type(a)
			#pe MIEUX RENVOYER RES AUSSI, comme ca ca fournit les groupes.
			yield w
			
	def add_p2w(self, w, *P):
		try:
			self[w] #verifie que w est une reference valide
		except : raise TypeError( KeyError, 3 )
		for p in P: self.getset(p).add(w)
		
	def __delitem__(self, w):
		pass
	
	
	################## RETRIEVAL PART ##########################
	def p2w_crossword(self, *Q):
		''' p2w_crossword (*arg) --> w ; args could contain jokers '?' and '*' '''
		star = self.__class__.crossword_star
		qmark = self.__class__.crossword_qmark
		try: ''.join(Q) ; 	case = str
		except : case = object
		#print case, Q
		l_encodingcrossword = []
		d_encode = {} #pour str, servira a calculer le domain. pour object, sert en plus à encoder.
		if case == str:
			for q in Q:
				if q == star : 
					l_encodingcrossword.append( '.*' )
					continue
				if q == qmark: 
					l_encodingcrossword.append( '.' )
					continue
				if q == '.': 
					l_encodingcrossword.append( '\.' )
					continue
				if q == '^': 
					l_encodingcrossword.append( '\^' )
					continue
				if q == '$': 
					l_encodingcrossword.append( '\$' )
					continue
				if q in d_encode :
					l_encodingcrossword.append( q )
					continue
				d_encode[q] = q
				l_encodingcrossword.append( q )
		else :
			for q in Q:
				if q == star : 
					l_encodingcrossword.append( '.*' )
					continue
				if q == qmark: 
					l_encodingcrossword.append( '.' )
					continue
				if q == '.': 
					l_encodingcrossword.append( '\.' )
					continue
				if q == '^': 
					l_encodingcrossword.append( '\^' )
					continue
				if q == '$': 
					l_encodingcrossword.append( '\$' )
					continue
				if q in d_encode :
					l_encodingcrossword.append( d_encode[q] )
					continue
				if isinstance(q, basestring): 
					if len(q) == 1:
						d_encode[q] = q
						l_encodingcrossword.append( q )
						continue
				d_encode[q] = unichr(len(d_encode)+128)
				l_encodingcrossword.append( d_encode[q] )
		encodingcrossword = '^'+''.join(l_encodingcrossword)+'$'
		#print d_encode
		#print repr(encodingcrossword)
		compiledq = re.compile(encodingcrossword )
		for i in self.apply_regex( compiledq, d_encode ):
			yield i
	def apply_regex_anagrams(self, compiledq , d_encode, **kwargs):
		minlen = kwargs.get('minlen', 1) ; maxlen = kwargs.get('maxlen', 50000)
		iterator_domain = self.get_domain_iterator(d_encode)
		for w in iterator_domain: 
			if len(w) < minlen : continue
			if len(w) > maxlen : continue
			
			if isinstance(w, basestring):
				res = compiledq.match( w )
			else: 
				encodedw, d_encode_local = self.encodew( w, d_encode )
				res = compiledq.match( encodedw )
			if res == None : continue
			yield w
	def p2w_anagrams(self, *Q):
		''' anagrams (*arg) --> w ; args contain only *p '''
		try: ''.join(Q) ; case = str
		except : case = object
		l_encodinganagrams = []
		d_encode = {} #pour str, servira a calculer le domain. pour object, sert en plus à encoder.
		if case == str:
			for q in Q:
				if q in self.__class__.regexchars :
					codedq = '\q'
				else : codedq = q
				l_encodinganagrams.append( codedq )
				if not q in d_encode: d_encode[q] = codedq
		else :
			for q in Q:
				if q in self.__class__.regexchars :
					codedq = '\q'
					d_encode[q] = codedq
				elif isinstance(q, basestring): 
					codedq = q
					d_encode[q] = codedq
				else :
					if not q in d_encode:
						codedq = unichr(len(d_encode)+128)
						d_encode[q] = codedq
					else : codedq = d_encode[q]
				l_encodinganagrams.append( codedq )
				
		d__code2count = Counter( l_encodinganagrams )
		l_coding_anagrams = []
		for pcoded, count in d__code2count.iteritems():
			mystring = '(?=' + ''.join( [ '.*'+pcoded for i in xrange( d__code2count[pcoded] ) ] ) +')'
			l_coding_anagrams.append( mystring )
		#coding_anagrams = '^'+''.join(l_coding_anagrams)+'(?!'+'.'*(len(l_encodinganagrams)+3) + '*).*$'
		coding_anagrams = ''.join(l_coding_anagrams)+'.*'
		
		#print 'coding_anagrams', coding_anagrams
		#print d_encode
		#print repr(encodinganagram)
		compiledq = re.compile( coding_anagrams )
		for i in self.apply_regex_anagrams( compiledq, d_encode, minlen = len(l_encodinganagrams)-1, maxlen = len(l_encodinganagrams)+1 ):
			yield i

if __name__ == '__main__':
	
	def NONPEDAGOGIQUE():
		n4p = NPNI4P()
		addingdata = ['ABCD', 'A', ( ('ABCD', 'EFGH') ) ]
		for w in addingdata: n4p.w2p( w )
		res = repr( n4p )
		n4p = NPNI4P()
		addingdata = ['ABCD', 'A', ( 'ABCD', 'EFGH')  ]
		for w in addingdata: n4p.w2p( w )
		assert list( n4p ) == ['EFGH', ('ABCD', 'EFGH'), 'D', 'C', 'B', 'A', 'ABCD'] # les lettres A,B,C,D sont decouvertes dans ABCD, on decouvre aussi EFGH a cause de ('ABCD', 'EFGH') , 
																					# mais EFGH ne donne pas lui meme ses lettres et ses lettres restent inconnues.
		assert list(n4p.l_w()) == list(n4p.l_s()) == list( n4p ) 
		assert list(n4p.iter_w(2)) == list(n4p.iter_s(2)) == ['EFGH', ('ABCD', 'EFGH')]
		res1 = repr( n4p )
		assert res == res1 #en application de la notion d'atome, declarer un tout ou se contenter d'enumerer ses parties revient au meme.
		assert len(n4p) == 7 # ['EFGH', ('ABCD', 'EFGH'), 'D', 'C', 'B', 'A', 'ABCD'] 
		assert str( n4p ) == "NPNI4P([('EFGH', _RevOS_([('ABCD', 'EFGH'), 'EFGH'])), (('ABCD', 'EFGH'), _RevOS_()), ('D', _RevOS_(['ABCD', 'D'])), ('C', _RevOS_(['ABCD', 'C'])), ('B', _RevOS_(['ABCD', 'B'])), ('A', _RevOS_(['ABCD', 'A'])), ('ABCD', _RevOS_([('ABCD', 'EFGH'), 'ABCD']))])"
		addingdata = ['ABCD', 'ABCD', 'BCDA', 'BBBCDA', 'A', 'hhhh', 'hhhh', 'jhhh', 'hhh', 'CDDDDAAB', 'ACDAB', 'DABC', 'AZB', 'BZA', 'CDAB' ]
		for w in addingdata: n4p.w2p( w )
		assert 'ABCD' in n4p.p2w_crossword ( *'*ABCD' )
		assert 'A' in n4p.p2w_crossword ( *'*A' )
		assert 'A' in n4p.p2w_crossword ( *'A*' )
		assert 'A' in n4p.p2w_crossword ( *'*A*' )
		assert 'ABCD' in n4p.p2w_crossword ( *'ABCD' ) 
		assert list(n4p.p2w_crossword ( *'*A?' )) == ['CDAB', 'ACDAB', 'CDDDDAAB']
		assert list(n4p.p2w_crossword ( *'hhhh' )) == ['hhhh']
		assert list(n4p.p2w_crossword ( *'hhh' )) == ['hhh']
		assert list(n4p.p2w_crossword ( *'????' )) == 	['CDAB', 'DABC', 'jhhh', 'hhhh', 'BCDA', 'EFGH', 'ABCD']
		assert list(n4p.p2w_crossword ( *'????*' )) == 	['CDAB', 'DABC', 'ACDAB', 'CDDDDAAB', 'jhhh', 'hhhh', 'BBBCDA', 'BCDA', 'EFGH', 'ABCD']
		# remarques sur ci-dessous: recherche objet
		# si un objet est considere comme immutable (ci dessous, il s'agit d'une chaine), il retourne aussi lui m comme instance.
		# voir 
		n4p.w2p( *(('ABCD', 'EFGH'),) )
		assert list(n4p.p2w_crossword ( *( 'ABCD', '*' ) ) ) == [('ABCD', 'EFGH'), 'ABCD'] 
		assert list(n4p.p2w_crossword ( *( '*', 'EFGH' ) ) ) == [('ABCD', 'EFGH'), 'EFGH']
		assert list(n4p.p2w_crossword ( *( 'ABCD', 'EFGH' ) ) ) == [('ABCD', 'EFGH')]
		
	def retrieving_from_crossword():
		n4p = NPNI4P()
		omega = ['BZA', 'AZB', 'DABC', 'CDAB', 'BCDA', 'ABCD']
		for w in omega: n4p.w2p( w )	# indexation
		assert len(n4p) == 11 # A, B, C, D, Z, +len(set(omega))
		assert list(n4p.s2i( 'A' )) == ['ABCD', 'BCDA', 'CDAB', 'DABC', 'AZB', 'BZA', 'A']
		#rappel : omega = ['ABCD', 'BCDA', 'CDAB', 'DABC', 'AZB', 'BZA' ]
		assert len( list(n4p.p2w_crossword ( *'?' )) ) == 5 # les 5 lettres
		assert list(n4p.p2w_crossword ( *'??' )) == []
		assert list(n4p.p2w_crossword ( *'????*' )) == ['ABCD', 'BCDA', 'CDAB', 'DABC']
		assert list(n4p.p2w_crossword ( *'A*' )) == ['ABCD', 'AZB', 'A']
		assert list(n4p.p2w_crossword ( *'?A' )) == []
		assert list(n4p.p2w_crossword ( *'?A*' )) == [ 'DABC' ]
		assert list(n4p.p2w_crossword ( *'?AB*' )) == [ 'DABC' ]
		assert list(n4p.p2w_crossword ( *'A' )) == [ 'A' ]
		assert list(n4p.p2w_crossword ( *'?Z?' )) == [ 'AZB', 'BZA' ]
		assert list(n4p.p2w_crossword ( *'*A*' )) == ['ABCD', 'BCDA', 'CDAB', 'DABC', 'AZB', 'BZA', 'A']
		assert list(n4p.p2w_crossword ( *'*A?' )) == ['CDAB']
		assert list(n4p.p2w_crossword ( *'??A?' )) == ['CDAB']
		assert list(n4p.p2w_crossword ( *'*A?' )) == ['CDAB']
		assert list(n4p.p2w_crossword ( *'**A?' )) == ['CDAB']
		assert list(n4p.p2w_crossword ( *'*?A?' )) == ['CDAB']
		assert list(n4p.p2w_crossword ( *'*A?*' )) == ['ABCD', 'CDAB', 'DABC', 'AZB']
		assert list(n4p.p2w_crossword ( *'*A??*' )) == ['ABCD', 'DABC', 'AZB']
		assert list(n4p.p2w_crossword ( *'*A???*' )) == ['ABCD' ]
		assert list(n4p.p2w_crossword ( *'*A????*' )) == []
		#'Small data, one p and jokers : pass' 
		#rappel : omega = ['ABCD', 'BCDA', 'CDAB', 'DABC', 'AZB', 'BZA' ]
		assert list(n4p.p2w_crossword ( *'*AB*' )) == ['ABCD', 'CDAB', 'DABC']
		assert list(n4p.p2w_crossword ( *'*AB' )) == ['CDAB']
		assert list(n4p.p2w_crossword ( *'AB*' )) == ['ABCD']
		assert list(n4p.p2w_crossword ( *'?AB?' )) == ['DABC']
		assert list(n4p.p2w_crossword ( *'?AB*' )) == ['DABC']
		assert list(n4p.p2w_crossword ( *'?AB' )) == []
		assert list(n4p.p2w_crossword ( *'AB?' )) == []
		assert list(n4p.p2w_crossword ( *'*BZA*' )) == ['BZA']
		#rappel : omega == ['ABCD', 'BCDA', 'CDAB', 'DABC', 'AZB', 'BZA' ]
		assert list(n4p.p2w_crossword ( *'A*B*' )) == ['ABCD', 'AZB']
		assert list(n4p.p2w_crossword ( *'A*B*' )) == ['ABCD', 'AZB']
		assert list(n4p.p2w_crossword ( *'A?B*' )) == ['AZB']
		assert list(n4p.p2w_crossword ( *'A?D*' )) == []
		assert list(n4p.p2w_crossword ( *'A??D*' )) == ['ABCD']
		assert list(n4p.p2w_crossword ( *'A??D?' )) == []
		assert list(n4p.p2w_crossword ( *'AB??' )) == ['ABCD']
		assert list(n4p.p2w_crossword ( *'?A?C' )) == ['DABC']
		assert list(n4p.p2w_crossword ( *'?A?C?' )) == []
		assert list(n4p.p2w_crossword ( *'?AB?' )) == ['DABC']
		assert list(n4p.p2w_crossword ( *'AB?' )) == []
		assert list(n4p.p2w_crossword ( *'*A*B*C*' )) == ['ABCD', 'DABC' ]
		assert list(n4p.p2w_crossword ( *'A*B*C*' )) == ['ABCD']
		assert list(n4p.p2w_crossword ( *'AB*CD' )) == ['ABCD']
		n4p = NPNI4P()
		addingdata = ['ABCD', 'BCDA', 'BBBCDA', 'A', 'hhhh', 'hhhh', 'jhhh', 'hhh', 'CDDDDAAB', 'ACDAB', 'DABC', 'AZB', 'BZA', 'CDAB' ]
		for w in addingdata:
			n4p.w2p( w )
		assert list(n4p.p2w_crossword ( *'*A' )) == ['BZA', 'BBBCDA', 'BCDA', 'A']
		assert list(n4p.p2w_crossword ( *'*ABCD' )) == ['ABCD']
		assert list(n4p.p2w_crossword ( *'*A?' )) == ['CDAB', 'ACDAB', 'CDDDDAAB']
		assert list(n4p.p2w_crossword ( *'*hhhh' )) == ['hhhh']
		assert list(n4p.p2w_crossword ( *'*hh' )) == ['hhh', 'jhhh', 'hhhh']
		assert list(n4p.p2w_crossword ( *'hhh' )) == ['hhh']
		print 'retrieving_from_crossword : pass'
	
	def retrieving_from_anagrams():
		n4p = NPNI4P()
		omega = ['BZA', 'AZB', 'DABC', 'CDAB', 'BCDA', 'ABCD']
		for w in omega: 
			n4p.w2p( w )	# indexation
		assert list( n4p.p2w_anagrams ( *'ZAB' ) ) == ['AZB', 'BZA' ]
		assert list( n4p.p2w_anagrams ( *'AZ' ) ) == ['AZB', 'BZA' ] #admission de 1+ caractere
		assert list( n4p.p2w_anagrams ( *'ZA' ) ) == ['AZB', 'BZA' ] #admission de 1+ caractere
		assert list( n4p.p2w_anagrams ( *'A' ) ) == ['A']
		assert list( n4p.p2w_anagrams ( *'ABC' ) ) == ['ABCD', 'BCDA', 'CDAB', 'DABC']
		print 'retrieving_from_anagrams : pass'
		
	def retrieving_objects():
		class Letter(object): 
			d_letter = {}
			@classmethod
			def getset(cls, w):
				if w in cls.d_letter : return cls.d_letter[w]
				cls.d_letter[w] = cls(w)
				return cls.d_letter[w]
			def __init__(self, w): self.w = w
			def __len__(self) : return len(self.w)
			def __iter__(self) : yield self.w
			def __repr__(self) : return ''.join( ['<', self.__class__.__name__, ' instance ', repr(self.w), '>'])
			def __str__(self) : return self.__repr__()
		class Word(Letter):
			def __iter__(self) : 
				for p in self.w: yield Letter.getset(p)
		n4p = NPNI4P()
		omega = [ Word.getset(w) for w in ['ABCD', 'BCDA', 'BBBCDA', 'CDAB', 'CDDDDAAB', 'ACDAB', 'DABC', 'AZB', 'BZ' ]]
		for w in omega:
			n4p.w2p(w)
		#remarque pour ci-dessous : comme les vrais objets sont mutables dans le temps, ils n'ont jamais pour instance eux-meme...
		assert str(n4p.items()[:3]) == "[(<Word instance 'BZ'>, _RevOS_()), (<Letter instance 'Z'>, _RevOS_([<Word instance 'BZ'>, <Word instance 'AZB'>])), (<Word instance 'AZB'>, _RevOS_())]"
		assert len(n4p) == 14
		letterZ = Letter.d_letter['Z']
		assert str(letterZ) == "<Letter instance 'Z'>"
		assert str(list( n4p.p2w_crossword ( *('*' , letterZ, '?') ) ) ) == "[<Word instance 'AZB'>]" #les obj, en principe mutable, n'ont pas pour instance eux meme.
		wordAZB = Word.getset( 'AZB' )
		assert wordAZB in n4p
		assert list( n4p.p2w_crossword ( *('*', wordAZB, '*' ) ) ) == [] #les obj, en principe mutable, n'ont pas pour instance eux meme.
		letterA = Letter.getset('A')
		letterB = Letter.getset('B')
		assert str(list( n4p.p2w_crossword ( *('*' , letterB, '*', letterA ) ) )) == "[<Word instance 'BBBCDA'>, <Word instance 'BCDA'>]"
		class Compound( Word ):
			def __iter__(self) : 
				for p in self.w: yield p
		compoundAZB_BCDA = Compound ( ( Word.getset( 'AZB' ), Word.getset( 'BCDA' ) ) )
		assert repr( compoundAZB_BCDA ) == "<Compound instance (<Word instance 'AZB'>, <Word instance 'BCDA'>)>"
		n4p.w2p( compoundAZB_BCDA )
		assert str(n4p.last_w()) == "<Compound instance (<Word instance 'AZB'>, <Word instance 'BCDA'>)>"
		assert str(list( n4p.p2w_crossword ( *('*' , Word.getset( 'AZB' ), '?') ) ) ) == "[<Compound instance (<Word instance 'AZB'>, <Word instance 'BCDA'>)>]"
		assert str(list( n4p.p2w_crossword ( *( Word.getset( 'AZB' ), ) ) ) ) == "[]" #considere ici comme mutable
		assert  str(list( n4p.p2w_crossword ( *( Word.getset( 'AZB' ), Word.getset( 'BCDA' ) ) ) ) ) == "[<Compound instance (<Word instance 'AZB'>, <Word instance 'BCDA'>)>]"
		compoundAZB_BCDA_BZ = Compound ( ( Word.getset( 'AZB' ), Word.getset( 'BCDA' ), Word.getset( 'BZ' ) ) )
		n4p.w2p( compoundAZB_BCDA_BZ ) 
		assert str(n4p.last_w()) == "<Compound instance (<Word instance 'AZB'>, <Word instance 'BCDA'>, <Word instance 'BZ'>)>"
		#LE RESULAT PREC RETIENT !ment CDAB, CDDDDAAB, ACDAB : normal
		print 'retrieving_objects : pass'
	
	def special_features():
		'''If isinstance(w, type) == True, then w can mutate then, can add or delete parts.
		Formally, you have interest to mutate (add/extend/delete/append etc) this p in w itself...  Here an an example for an IndexableList.'''
		class IndexableList(object):
			def __init__(self, npni, n = [] ): 
				self.n = n ; self.npni = npni
				npni.w2p( self )
			def __len__(self) : return len(self.n)
			def __iter__(self) : return list.__iter__(self.n)
			def append(self, item) : 
				self.n.append(item)
				self.npni.add_p2w( self, *(item,) )
			def extend(self, alist) : 
				list.extend(self.n, alist)
				self.npni.add_p2w( self, *alist)
			
			def __repr__(self) : return ''.join( ['<', self.__class__.__name__, ' instance of len ', repr(len(self)), '>'])
			def __str__(self) : return self.__repr__()
		n4p = NPNI4P()
		n = IndexableList( n4p, [0, 1, 2] )
		assert str(n) == "<IndexableList instance of len 3>"
		n4p.w2p( n )
		assert str(n4p.l_s()) == "[2, 1, 0, <IndexableList instance of len 3>]"
		assert str(list(n4p.p2w_crossword( *('*' , 1, '?') ) )) == "[<IndexableList instance of len 3>]"
		assert str( list( n4p.p2w_anagrams (1, 2) ) ) == "[<IndexableList instance of len 3>]"
		n.append ( 10 )
		assert len( n4p ) == 5
		n.extend ( [ i for i in xrange (1, 1000, 1) ] )
		n3multiple = IndexableList( n4p, [i for i in xrange (0, 100, 2)] )
		assert str(list(n4p.p2w_crossword( *( '*', 4, '*') ) )) == "[<IndexableList instance of len 50>, <IndexableList instance of len 1003>]"
		
		
		
		
		
		
	def createlotofwandindex(size=1000000):
		'''Only useful for quantitative benchmark..... function loading forms in several languages ; resource computed by PVDT....'''
		#import sys
		print 'load data (createlotofwandindex) : wait...'
		from extract_forms import l_lang, iter__lang_w
		n4p = NPNI4P()
		l4test = ['ABCD', 'BCDA', 'CDAB', 'DABC', 'AZB', 'BZA' ]
		for w in l4test: n4p.w2p( w )
		b = npniclock() ; totalduration = 0
		msg='.'*80
		for count, lang_w in enumerate(iter__lang_w(*l_lang)) :
			if len(n4p) >= size : break
			lang, w = lang_w
			n4p.w2p( w )
			if count%100000 == 0 : 
				msg = ''.join( [ 'len n4p=', str(len(n4p)), ' (total reading:', str(count), ')'])
				print msg
				duration = npniclock()-b ; 
				totalduration+=duration
				b = npniclock()
		duration = npniclock()-b ; 
		totalduration+=duration
		totalduration=str(totalduration)[:5]+'s.'
		
		print 'INDEX CREATION OF '+str(len(n4p)), ' W in ', totalduration, ': pass'
		return n4p
	
	def __query2bigspace__(n4p, *query):
		'''Only useful for quantitative benchmark..... '''
		b = npniclock() 
		p2w = n4p.p2w_crossword ( *query )
		lres = list(p2w)
		#print lres
		duration = str(npniclock()-b)[:5]+'s.'
		print 'Q crossword:', ''.join(query), 'returns ', str(len(lres)) , ' results in ', duration
		res = ''.join( ['  ex:  ', str(lres[:2]), ' ... ', str(lres[-2:]) ] )[:80]
		print res,
		if res[-1]==']': print 
		else : print '...'
		return lres
		
	def quatitative_benchmark(n4p):
		'''the benchmark is rather good but could be speed by some add (see TODO in top of the document).'''
		lres = __query2bigspace__( n4p, *'AB*')
		assert 'ABCD' in lres
		lres = __query2bigspace__( n4p, *'?AB*')
		lres = __query2bigspace__( n4p, *'??AB*')
		lres = __query2bigspace__( n4p, *'*A??B*R*')
		lres = __query2bigspace__( n4p, *'*BRASIVE*')
		lres = __query2bigspace__( n4p, *'*BRAS*')
		print 'BIG DATA, p2w crossword : pass'
		qanagram = 'CATHERINE'
		b = npniclock() 
		lres = list( n4p.p2w_anagrams ( *qanagram ) )
		duration = str(npniclock()-b)[:5]+'s.'
		print 'Q anagram: ', qanagram, 'returns ', str(len(lres)) , ' results in ', duration 
		print lres
		
		print 'quatitative_benchmark : pass'

	NONPEDAGOGIQUE()
	retrieving_from_crossword()
	retrieving_from_anagrams() 
	retrieving_objects()
	special_features()
	n4p = createlotofwandindex(1000000)
	quatitative_benchmark(n4p)
