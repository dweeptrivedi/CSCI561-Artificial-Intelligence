import re
import copy
import sys
import time

q = 0
nkb = 0
que = []
strkb = []
startTime = 0
availTime = 0


def isVariable(variable):
	return isinstance(variable,str) and variable[0].islower()

def isPredicate(pred):
	return isinstance(pred,list) and len(pred)>=3 and pred[1][0].isupper() and (pred[0]=='' or pred[0]=='~')

class reader:
	def __init__(self, sentence):
		self.str = sentence

	def read(self):
		length = len(self.str)
		term = ""
		itr = 0
		c = clause()
		while itr < length:
			
			if self.str[itr] == ')':
				pred = predicate(term+self.str[itr])
				c.add(pred)
				term = ""
			else:
				if self.str[itr] != ' ' and self.str[itr] != '|':
					term += self.str[itr]
			itr += 1
		c.sort()
		return c
		


def parse(sentence):
	r = reader(sentence)
	return r.read()


def predicate(sentence):
	pred = ["" for i in range(3)]
	if sentence == "":
		return pred
	
	p = re.search("\s*([~\w\d]+)\((.*)\)",sentence)
	name = p.group(1)
	if name[0] == '~':
		pred[0] = name[0]
		pred[1] = name[1:]
	else:
		pred[0] = ""
		pred[1] = name
	pred[2:] = p.group(2).split(',')[:]
	return pred 

class clause:
	def __init__(self, listOfPred=None):
		self.predicates = []
		self.isSorted = False
		if listOfPred!=None:
			for pred in listOfPred:
				self.predicates.append(pred)

	def add(self, pred):
		self.predicates.append(pred)

	def standardize(self,idx=1):
		count = {}
		for pred in self.predicates:
			for i in range(2,len(pred)):
				if isVariable(pred[i]):
					if pred[i] in count:
						pred[i] = "v"+count[pred[i]]
					else:
						
						count[pred[i]] = str(idx)
						pred[i] = "v"+str(idx)
						idx+=1
		return idx

	def applySubst(self, subst):

		for i in range(len(self.predicates)):
			for j in range(2,len(self.predicates[i])):
				key = (self.predicates[i])[j]
				if key in subst:
					while (subst[key] in subst):
						key = subst[key]
					(self.predicates[i])[j] = subst[key]
		
		strClause = {}
		temp = []
		for j in range(len(self.predicates)):
			key = (re.sub("\d+","",str(self.predicates[j])))
			if key not in strClause:
				strClause[key]=1
				temp.append(self.predicates[j])
			else:
				pass
		self.predicates = temp
		#THINK ABOUT THIS##################################################################
		
		#assert len(set(strClause)) == len(self.predicates)
	def sort(self):
		self.predicates = sorted(self.predicates,key=lambda x: x[0]+x[1])

	def repr(self):
		return str(self.predicates)

	def hasTautology(self):
		abc = {}
		for pred in self.predicates:
			ghi = copy.deepcopy(pred)
			if ghi[0]=="":
				ghi[0]="~"
			else:
				ghi[0]=""

			if str(ghi) in abc:
				return True
			abc[str(pred)] = 1
			
		return False

class KB:
	def __init__(self):
		self.clauses = []
		self.kBaseSrepr = {}

	def tell(self, sentence):
		c = parse(sentence)
		c.standardize()
		self.clauses.append(c)
		self.kBaseSrepr[hash(c.repr())] = 1

	def ask(self, query):
		resolve(self, query)



def copyClause(clause1):

	c = clause()
	for pred in clause1.predicates:
		c.add(pred[:])

	return c

def canResolve(clause1,clause2):
	for p1 in clause1.predicates:
		for p2 in clause2.predicates:
			if p1[1]==p2[1] and p1[0]!=p2[0]:
				return True
	return False


def standardize_apart(clause1,clause2):
	idx = clause1.standardize(1)
	clause2.standardize(idx+1)


def occurCheck():
	pass

def unifyVar(var, other, subst):
	if var in subst:
		return unify(subst[var], other, subst)
	elif other in subst:
		return unify(var, subst[other], subst)
	elif occurCheck():
		return None
	else:
		subst[var] = other
		return subst

def unify(x, y, subst):
	if subst == None:
		return None
	elif x==y:
		return subst
	elif isVariable(x):
		return unifyVar(x, y, subst)
	elif isVariable(y):
		return unifyVar(y, x, subst)
	elif isPredicate(x) and isPredicate(y):
		return unify(x[2:],y[2:],subst)
	elif isinstance(x,list) and isinstance(y,list) and  len(x)==len(y):
		for i in range(len(x)):
			subst = unify(x[i],y[i],subst)
		return subst
	else:
		return None

def resolveTwo(pairs):
	clause1 = pairs[0]
	clause2 = pairs[1]
	listOfClauses = []

	for pred1 in (clause1.predicates):
		for pred2 in (clause2.predicates):
			if pred1[1]== pred2[1] and pred1[0] != pred2[0]:
				assert len(pred1) == len(pred2)
				
				i1 = clause1.predicates.index(pred1)
				i2 = clause2.predicates.index(pred2)
				dclause1 = copyClause(clause1)
				dclause2  = copyClause(clause2)

				standardize_apart(dclause1,dclause2)
				
				subst = {}
				subst = unify(dclause1.predicates[i1], dclause2.predicates[i2], subst)
				if subst != None:

					listOfPred = (((dclause1.predicates[:i1]) + (dclause1.predicates[i1+1:]) + (dclause2.predicates[:i2]) + (dclause2.predicates[i2+1:])))
					
					if listOfPred != []:
						newClause = clause(listOfPred)
						newClause.applySubst(subst)
						newClause.standardize()
						newClause.sort()

						listOfClauses.append(newClause)

					else:
						newClause = None
						listOfClauses.append(newClause)
						return listOfClauses
					
	return listOfClauses

def resolve(kBase, queryClause, depth):
	global availTime,startTime
	time2 = time.time()
	if depth==2500 or time2-startTime>availTime:
		return
	
	clauses = kBase.clauses
	new = []
	newstr = []
	pairs = []

	temp = 1

	for i in range(len(kBase.clauses)):
		if canResolve(kBase.clauses[i],queryClause):
			pairs.append([kBase.clauses[i],queryClause])


	while temp<=1:
		temp+=1
		new = []
		newstr = []
		clauses = kBase.clauses
		len1 = len(clauses)
		size1 = len(kBase.kBaseSrepr)
		len2 = 0
	
		for i in range(len(pairs)):
			resolvents = resolveTwo(pairs[i])

			for c in resolvents:
				if c==None:
					return True
				key = hash(c.repr())

				if  key not in kBase.kBaseSrepr:
					kBase.kBaseSrepr[key] = 1
					retVal = resolve(kBase,c,depth+1)
					if retVal == True:
						return True
				else:
					pass
			
		##############################
		##WARNING!!!!!!!!!!!!!!!!!!!!!!!!!
		##############################
		del pairs
		pairs = []
		
	return None


def countVar(cl):
	d = {}
	varCount = 0
	for pred in cl.predicates:
		for i in range(2,len(pred)):
			if isVariable(pred[i]) and (pred[i] not in d):
				d[pred[i]]=1
				varCount+=1
	return varCount

def sortKB(kBase):
	pairs = []
	for cl in kBase.clauses:
		pairs.append([cl,countVar(cl)])
	pairs = sorted(pairs,key=lambda x:x[1])
	for i in range(len(kBase.clauses)):
		kBase.clauses[i] = pairs[i][0]
	
def main():
	global q, nkb, que, strkb, availTime, startTime
	ObjKB = KB()
	sys.setrecursionlimit(10000)

	input = open("input.txt","r")
	q = int((input.readline()).rstrip())
	usedTime = time.time()
	for i in range(q):
		que.append((input.readline()).rstrip())
	nkb = int((input.readline()).rstrip())
	for i in range(nkb):
		strkb.append((input.readline()).rstrip())
		ObjKB.tell(strkb[i])
	input.close()
	
	output = open("output.txt","w")
	ObjKBi = copy.deepcopy(ObjKB)
	sortKB(ObjKBi)
	l = len(ObjKBi.clauses)

	for i in range(q):
		
		del ObjKBi.clauses[l:]
		ObjKBi.kBaseSrepr=copy.deepcopy(ObjKB.kBaseSrepr)
		
		availTime = (250-time.time()+usedTime)/(q-i)
		
		if que[i][0] == '~':
			que[i] = que[i][1:]
		else:
			que[i] = '~'+que[i]
			
		queryClause = parse(que[i])		
		ObjKBi.tell(que[i])
		startTime = time.time()
		result = resolve(ObjKBi, queryClause, 1)
		if result:
			output.write("TRUE\n")
		else:
			output.write("FALSE\n")
		

if __name__ == "__main__":
	main()
