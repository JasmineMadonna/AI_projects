# Solves the globe puzzle using different algorithms
from collections import deque
import sys, copy, heapq, math, time
from operator import attrgetter

#Reads the puzzle from file and creates a dictonary with key and current and goal state.
def read_puzzle(filename):
	tile_pos = {}
	with open(filename, 'r') as f:
		data = f.readlines()
		for i in range(1,len(data)):
			ssplit = data[i].split(',')
			if len(ssplit) >= 4:
				key = ssplit[0].strip('Tile(')
				pos1 = []
				pos1.append(int(ssplit[1].strip(' (')))
				pos1.append(int(ssplit[2].strip(')')))
				pos2 = []
				pos2.append(int(ssplit[3].strip(' Exact(')))
				pos2.append(int(ssplit[4].split(')')[0]))
				tile_pos[key] = [pos1,pos2]
	return tile_pos

#Function to test whether current state is same as goal state
def goal_test(cur_state, goal_state):
	for key in goal_state.keys():
		if cur_state[key][0] == goal_state[key][0] and cur_state[key][1] == goal_state[key][1]:
			continue
		else:
			return False
	return True

#Node class
#f h and f are used only for Astar and RBFS
class Node:
	def __init__(self, state, parent, action, path_cost, h, f):
		self.state = state
		self.parent = parent
		self.action = action
		self.path_cost = path_cost #g
		self.h = h #h
		self.f = f

	def __lt__(self, other):
		return self.f < other.f
		
	def __le__(self, other):
		return self.f <= other.f


#returns the next state when an action is applied to the given state
def result(parent, action):
	state = copy.deepcopy(parent)
	if action == 'long0-180_inc':
		for key in state.keys():
			#if key in {"NP", "30-0", "60-0", "90-0", "120-0", "150-0", "SP", "150-180", "120-180", "90-180", "60-180", "30-180"}:
				if state[key][1] == 0:
					state[key][0] = state[key][0] + 30
					if state[key][0] == 180:
						state[key][1] = 180
				elif state[key][1] == 180:
					state[key][0] = state[key][0] - 30
					if state[key][0] == 0:
						state[key][1] = 0
	if action == 'long0-180_dec':
		for key in state.keys():
			#if key in {"NP", "30-0", "60-0", "90-0", "120-0", "150-0", "SP", "150-180", "120-180", "90-180", "60-180", "30-180"}:
				if state[key][1] == 0:
					state[key][0] = state[key][0] - 30
					if state[key][0] == -30:
						state[key][0] = 30
						state[key][1] = 180
				elif state[key][1] == 180:
					state[key][0] = state[key][0] + 30
					if state[key][0] == 210:
						state[key][0] = 150
						state[key][1] = 0
	if action == 'long90-270_inc':
		for key in state.keys():
			#if key in {"NP", "30-90", "60-90", "90-90", "120-90", "150-90", "SP", "150-270", "120-270", "90-270", "60-270", "30-270"}:
				if state[key] == [0,0]:
					state[key] = [30,90]
				elif state[key] == [180, 180]:
					state[key] = [150,270]
				elif state[key][1] == 90:
					state[key][0] = state[key][0] + 30
					if state[key][0] == 180:
						state[key][1] = 180
				elif state[key][1] == 270:
					state[key][0] = state[key][0] - 30
					if state[key][0] == 0:
						state[key][1] = 0
	if action == 'long90-270_dec':
		for key in state.keys():
			#if key in {"NP", "30-90", "60-90", "90-90", "120-90", "150-90", "SP", "150-270", "120-270", "90-270", "60-270", "30-270"}:
				if state[key] == [0,0]:
					state[key] = [30,270]
				elif state[key] == [180, 180]:
					state[key] = [150,90]
				elif state[key][1] == 90:
					state[key][0] = state[key][0] - 30
					if state[key][0] == 0:
						state[key][1] = 0
				elif state[key][1] == 270:
					state[key][0] = state[key][0] + 30
					if state[key][0] == 180:
						state[key][1] = 180
	if action == 'equ_inc':
		for key in state.keys():
			#if key in {"90-0", "90-30", "90-60", "90-90", "90-120", "90-150", "90-180", "90-210", "90-240", "90-270", "90-300", "90-330"}:
			if state[key][0] == 90:
				state[key][1] = state[key][1] + 30
				if state[key][1] == 360:
					state[key][1] = 0
	if action == 'equ_dec':
		for key in state.keys():
			#if key in {"90-0", "90-30", "90-60", "90-90", "90-120", "90-150", "90-180", "90-210", "90-240", "90-270", "90-300", "90-330"}:
			if state[key][0] == 90:
				if state[key][1] == 0:
					state[key][1] = 330
				else:
					state[key][1] = state[key][1] - 30
	return state

#returns true if the state is present in explored set, false otherwise
def isExplored(explored, state):
	for item in explored:
		if goal_test(item, state):
			return True
	return False

#Returns true if state is same as any of the node's state in frontier
def isInFrontier(frontier, state):
	for i in range(len(frontier)):
		if goal_test(frontier[i][1].state, state):
			return (True, i, frontier[i][0])
	return (False, None, None)

#Returns the solution as sequence of steps given the node where the goal state is reached. Backtracks by taking the parent and the action applied to it till it reaches the init state	
def solution(child):
	if child.parent == None:
		return "Init state is the goal state. No actions needed"

	actions = []
	node = child	
	while node.parent != None:
		actions.append(node.action)
		node = node.parent
	
	print("Sequence of steps : ")
	actions.reverse()
	print(actions)
	return "Solution found" 

#Solves puzzle using BFS algorithm
def BFS(parent, goal_state):
	actions = ['long0-180_inc', 'long0-180_dec', 'long90-270_inc', 'long90-270_dec', 'equ_inc', 'equ_dec']
	states_expanded = 0
	if goal_test(parent.state, goal_state):
		return "Solution found"

	max_q_len = 0
	frontier = deque([parent])
	explored = []
	while len(frontier) > 0:
		size = len(frontier)
		if size > max_q_len:
			max_q_len = size
		node = frontier.popleft()
		explored.append(node.state)
		states_expanded = states_expanded + 1
		for action in actions:
			#print(action)
			child_state = result(node.state, action)
			child = Node(child_state, node, action, node.path_cost+1, None, None)
			if isExplored(explored, child.state) == False:
				if goal_test(child.state, goal_state):
					print("States expanded = ", states_expanded)
					print("Max queue length = ", max_q_len)
					print("Path length = ", child.path_cost)
					return solution(child) 
				frontier.append(child)
	return "Solution not found"

#Heuristc for AStar and RBFS
def heuristic(state, goal_state):
	cost_equ = 0
	cost0180 = 0
	cost90270 = 0
	for key in state.keys():
		# if the tile is one of equator tile, compute distance like manhattan distance. While computing the distance acroos longitude, if it is more than 6, subtract the distance from 12 since we can reach the same tile rotating in opposite direction with less moves
		if key in {"90-30", "90-60", "90-120", "90-150", "90-210", "90-240", "90-300", "90-330"}:
			long_cost = abs(state[key][1] - goal_state[key][1])/30
			if long_cost > 6:
				long_cost = 12 - long_cost
			lat_cost = abs(state[key][0] - goal_state[key][0])/30	
			cost_equ = max(cost_equ, (long_cost + lat_cost))
		elif key in {"30-0", "60-0", "120-0", "150-0", "150-180", "120-180", "60-180", "30-180", "30-90", "60-90", "120-90", "150-90", "150-270", "120-270", "60-270", "30-270"}:
		#else:
			cost = 0
			if state[key][1] == goal_state[key][1]:
				cost = abs(state[key][0] - goal_state[key][0])/30
			elif state[key][1] in {0, 180, 90, 270}:
				cost = abs(state[key][0] - 0)/30 + abs(goal_state[key][0] - 0)/30
			else:
				cost = abs(state[key][0] - goal_state[key][0])/30 + abs(state[key][1] - goal_state[key][1])/30
			if cost > 6:
				cost = abs(12 - cost)

			if key in {"NP", "30-0", "60-0", "90-0", "120-0", "150-0", "SP", "150-180", "120-180", "90-180", "60-180", "30-180"}:#should we remove 90-0, 90-180
				cost0180 = max(cost, cost0180)
			else:
				cost90270 = max(cost, cost90270)
			
	return cost_equ + cost0180 + cost90270 

#Solves puzzle using AStar algorithm
def AStar(parent, goal_state):
	actions = ['long0-180_inc', 'long0-180_dec', 'long90-270_inc', 'long90-270_dec', 'equ_inc', 'equ_dec']
	states_expanded = 0
	#if goal_test(parent.state, goal_state):
	#	return "Solution found"
	max_q_len = 0
	g=0
	h=heuristic(parent.state, goal_state)
	parent.h = h
	parent.f = g+h
	frontier = []
	heapq.heappush(frontier,(g+h, parent))
	explored = []
	while len(frontier) > 0:
		size = len(frontier)
		if size > max_q_len:
			max_q_len = size
		node = heapq.heappop(frontier)[1]
		if goal_test(node.state, goal_state):
			print("States expanded = ", states_expanded)
			print("Max queue length = ", max_q_len)
			print("Path length = ", child.path_cost)
			return solution(node)

		explored.append(node.state)
		states_expanded = states_expanded + 1
		for action in actions:
			#print(action)
			child_state = result(node.state, action)
			child_path_cost = node.path_cost + 1
			h=heuristic(child_state, goal_state)
			f = child_path_cost + h
			child = Node(child_state, node, action, child_path_cost, h, f)
			inFrontier, index, cost_front = isInFrontier(frontier, child.state)
			if isExplored(explored, child.state) == False and inFrontier == False:
				heapq.heappush(frontier, (f, child))
			elif inFrontier == True and cost_front > f:
				frontier[index]=(f,child)
				heapq.heapify(frontier)
				
	return "Solution not found"

#Solves puzzle using RBFS algorithm
def RBFS(problem, node, f_limit, states_expanded):
	if goal_test(node.state, problem.goal_state):
		print("States expanded = ", states_expanded)
		print("Path length = ", node.path_cost)
		return solution(node), f_limit	
	successors = []
	states_expanded = states_expanded + 1
	for action in problem.actions:
		child_state = result(node.state, action)
		child_path_cost = node.path_cost + 1 #g
		h=heuristic(child_state, goal_state)
		f = child_path_cost + h
		child = Node(child_state, node, action, child_path_cost, h, f)
		successors.append(child)
	if len(successors) == 0:
		return "failed", f_limit
	for s in successors:
		s.f = max(s.path_cost + s.h, node.f)
	while True:
		successors.sort(key=lambda x: x.f)
		best = successors[0]
		if best.f > f_limit:
			return "failed", best.f
		alternative = successors[1]
		res, best.f = RBFS(problem, best, min(f_limit, alternative.f), states_expanded)
		if res != "failed":
			return res, best.f	

#Using this class only for RBFS
class Problem:
	def __init__(self, init_state, goal_state, actions):
		self.init_state = init_state
		self.goal_state = goal_state
		self.actions = actions

if __name__ == "__main__":
	args = sys.argv
	if len(args) < 3:
		print("Error: Run command Search.py <ALG> <FILE>")
		sys.exit()

	puzzle = str(args[2])
	alg = str(args[1])
	tile_pos = read_puzzle(puzzle)

	#splits the tile_pos dict into two dicts - init_state and goal_state
	init_state = {}
	goal_state = {}
	for key in tile_pos.keys():
		init_state[key] = tile_pos[key][0]
		goal_state[key] = tile_pos[key][1]

	parent = Node(init_state, None, None, 0, None, None)
	print("Solving puzzle: ", puzzle, " for algo ", alg)
	t0 = time.time()
	if alg == "BFS":
		print(BFS(parent, goal_state))
	if alg == "AStar":
		print(AStar(parent, goal_state))
	if alg == "RBFS":
		actions = ['long0-180_inc', 'long0-180_dec', 'long90-270_inc', 'long90-270_dec', 'equ_inc', 'equ_dec']
		problem = Problem(init_state, goal_state, actions)
		h = heuristic(init_state, goal_state)
		parent.f = h #since path_cost is zero for first state
		parent.h = h
		print(RBFS(problem, parent, math.inf, 0))
	print("Elapsed time = ", time.time()-t0)
