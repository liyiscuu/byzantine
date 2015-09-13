#!/usr/bin/python 

import threading 
import random 
import sys 
import getopt 
import time 
import copy

verbose = False 
generals = [] 
MESSAGE = 50 

MUTEX = threading.Lock() 

def thread_print(g,msg) : 
	if MUTEX.acquire(): 
		print "general:%d %s" % (g.ID,msg) 
		MUTEX.release() 
		
def split_msg(msg) : 
	path,m = msg.split(':') 
	return (path.split('->'),m) 
		
class general(threading.Thread): 

	N = 7 
	M = 2 
	
	STAGE = 1 

	def __init__(self,iscommander,istraitor,id) : 
		threading.Thread.__init__(self) 
		self.isCommander = iscommander 
		self.isTraitor = istraitor 
		self.ID = id 
		self.queue = [] 
		self.messages = [] 
		self.mutex = threading.Lock() 
		self.finish = False 
	
	def run(self) : 
		thread_print(self,'Starting (isCommander:%s, isTraitor:%s)' %(str(self.isCommander),str(self.isTraitor))) 
		time.sleep(0.5) 

		if self.isCommander : 
			self.send_command(":%d" % (MESSAGE)) 
			self.finish = True 
		else : 
			# exchange msgs 
			while general.STAGE == 1: 
				msg = self.recv() 
				if msg is None : break 
				self.messages.append(msg) 
				self.send_command(msg) 
			
			#thread_print(self,str(self.messages)) 
			
			#OM 
			gens = range(0,general.N) 
			for m in self.messages : 
				path,msg = split_msg(m) 
				if len(path) == 1 : 
					gens.remove(int(path[0])) 
					gens.remove(self.ID) 
					result = self.vote(path[0],gens,path,msg,general.M-1) 
					break 
			
			thread_print(self," Vote CMD:" + str(result)) 


	def vote(self,commander,path,gens,msg,m): 
		thread_print(self,'Commander=%d, gens = %s , M=%d' % (commander,str(gens),m))
		
		if m > 0 : 
			v = [msg]  #self
			for g in gens: 
				tmp_gens = gens.remove(g)
				tmp_path = path.append(g)
				tmp_msg = find_msg(self.msg,path)
				result = self.vote(g,tmp_gens,tmp_path,)
				v.append()
		
			
	def send_command(self,msg) : 
		path,cmd = msg.split(":") 
		
		if path=='': 
			path = [self.ID] 
		else: 
			path = map(int,path.split('->')) 
			path.append(self.ID) 
		
		if len(path) == general.M + 2 : return False 

		for g in generals : 
			if g.ID not in path : 
				msg = '->'.join(map(str,path)) 
				cmd = cmd if not self.isTraitor else str(random.randint(0,100)) 
				self.send(g,msg+':'+cmd) 
		return True 
	
	def send(self,dest,msg): 
		if verbose : thread_print(self,'Send: ' + msg) 
		if  dest.mutex.acquire(): 
			dest.queue.append(msg) 
			dest.mutex.release() 
			
	def recv(self) : 
		msg = None 
		while msg is None and general.STAGE == 1 : 
			if self.mutex.acquire(): 
				if(len(self.queue) > 0): 
					msg = self.queue.pop(0) 
				self.mutex.release() 
			if msg is None : 
				time.sleep(0.01) 
		
		if msg and verbose : thread_print(self,'Recv: ' + msg) 
		
		return msg 
			
if __name__ == '__main__': 
	
	try: 
		opts, args = getopt.getopt(sys.argv[1:], "m:n:") 
	except getopt.error, msg: 
		print "Error Parameters!" 
		sys.exit(-1) 
	
	# option processing 
	for option, value in opts: 
		if option == "-n": 
			general.N = int(value) 
		if option == "-m": 
			general.M = int(value) 

	print 'N=%d,M=%d' % (general.N,general.M) 
	
	assert(general.M<general.N) 
	
	
	commander = random.randint(0,general.N-1) 
	m = 0 
	for i in xrange(general.N) : 
		iscommander = True if commander == i else False 
		if m >= general.M : 
			istraitor = False 
		else : 
			istraitor = True if random.randint(0,1) == 0 else False 
			if istraitor : 
				m +=1 
		g = general(iscommander,istraitor,i) 
		generals.append(g) 
		g.start() 
	
	time.sleep(3) 
	general.STAGE = 2 

	for g in generals : 
		g.join() 