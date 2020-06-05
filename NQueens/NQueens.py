import copy, json, sys, time
class QueensGraph:
	def __init__(self, variables, domain, N, constraint):
		self.var = variables  #var is the variable list [0,1,2.. N-1]
		self.domain = copy.deepcopy(domain)  # a dict which holds the domain for each variable
		self.N = N
		self.constraint = constraint
		self.assignment = {}
		self.unassigned_vars = copy.copy(variables) #initially all variables will be unassigned
		self.backtracking_steps = 0
		self.graph = {} # The entire graph represented as an adjacency list
		for i in range(N):
			self.graph[i] = []
			for j in range(N):
				if i != j:
					self.graph[i].append(j)

	#Resets the variables and domain to find the next solution
	def reset(self, variables, domain):
		self.unassigned_vars = copy.copy(variables)
		self.domain = copy.deepcopy(domain)
		self.assignment = {}
		self.backtracking_steps = 0

# Retursn true if the assignment is a solution, false otherwise
def isComplete(nqueens):
	if len(nqueens.unassigned_vars) == 0:
		return True
	else:
		return False

# returns true of the current assignment is consistent with the previous assignments
def isConsistent(assignment, var, value, N):
	for key in assignment:
		# Checking row constraints
		if value == assignment[key]:
			return False
		# Checking diagonal constraints
		diag_right = value + abs(var - key)
		if diag_right == assignment[key]:
			return False
		diag_left = value - abs(var - key)
		if diag_left == assignment[key]:
			return False

	return True

# Inference function for forward checking
def inference_FOR(nqueens, var, value, N):
	inferences = []
	assign_copy = copy.deepcopy(nqueens.assignment)
	for var_u in nqueens.unassigned_vars:
		#Checking row constraints
		if value in nqueens.domain[var_u]:
			nqueens.domain[var_u].remove(value)
		#Checking diagonal constraints
		diag_right = value + abs(var - var_u)
		if diag_right < N and diag_right in nqueens.domain[var_u]:
			nqueens.domain[var_u].remove(diag_right)

		diag_left = value - abs(var - var_u)
		if diag_left >= 0 and diag_left in nqueens.domain[var_u]:
			nqueens.domain[var_u].remove(diag_left)

		if len(nqueens.domain[var_u]) == 0:
			return False, []
		if len(nqueens.domain[var_u]) == 1:
			# Add to inference only if consistent
			if isConsistent(assign_copy, var_u, nqueens.domain[var_u][0], N):
				inferences.append([var_u, nqueens.domain[var_u][0]])
				assign_copy[var_u] = nqueens.domain[var_u][0] 
			else:
				return False, []
			
	return True, inferences

# Inference function using AC-3 algorithm. Algorithm implemented as given in book 
def inference_MAC(nqueens, var, value, N):
	arcs = []
	for var_u in nqueens.unassigned_vars:
		arcs.append([var, var_u])
	#print("arcs : ", arcs)
	while len(arcs) > 0:
		arc = arcs.pop(0)
		if Revise(nqueens, arc):
			if len(nqueens.domain[arc[1]]) == 0:
				return False, []
			for var in nqueens.unassigned_vars:
				if var != arc[0] and var != arc[1]:
					arcs.append([arc[1],var])
	inferences = []
	assign_copy = copy.deepcopy(nqueens.assignment)
	for var_u in nqueens.unassigned_vars:
		if len(nqueens.domain[var_u])==1:
			if isConsistent(assign_copy, var_u, nqueens.domain[var_u][0], N):
				inferences.append([var_u, nqueens.domain[var_u][0]])
				assign_copy[var_u] = nqueens.domain[var_u][0] 
			else:
				return False, []
	return True, inferences

# Revise function for AC-3 implementation. Returns true we revise the domain for arc[1]. Xj is arc[0], Xi is arc[1]
def Revise(nqueens, arc):
	revised = False
	local_domain = nqueens.domain[arc[0]]
	#If the variable is already assigned value, use the assigned value as domain
	if arc[0] in nqueens.assignment.keys():
		local_domain = [nqueens.assignment[arc[0]]]
	for val_i in nqueens.domain[arc[1]]:
		allows = False
		for val_j in local_domain:
			if val_i != val_j:
				#Check for diagonal constraint
				diag_right = val_j + abs(arc[0] - arc[1])
				diag_left = val_j - abs(arc[0] - arc[1])
				if diag_right != val_i and diag_left != val_i:
					allows = True
					break
		if allows == False:
			nqueens.domain[arc[1]].remove(val_i)
			revised = True
	return revised
				
#Backtrack algorithm for NQeens as given in book	
def Backtrack(assignment, nqueens, N, Algo):
	if isComplete(nqueens):
		return True, assignment
	var = nqueens.unassigned_vars.pop(0) # pops the next unassigned variable 
	for value in nqueens.domain[var]:
		#print("unassigned var = ", var, " value = ",value)
		if isConsistent(assignment, var, value, N):
			assignment[var] = value  #add var=value to assignment
			#print("Consistent assignment : ", assignment)
			domain_copy = copy.deepcopy(nqueens.domain)
			infer_res = False
			inferences = []
			if Algo == "FOR":
				infer_res, inferences = inference_FOR(nqueens, var, value, N)
			else:
				infer_res, inferences = inference_MAC(nqueens, var, value, N)
			#print("infer_res = ", infer_res, " inferences : ", inferences, "domain : ", nqueens.domain, "domain_copy : ", domain_copy)
			if infer_res:
				for i in range(len(inferences)):
					assignment[inferences[i][0]] = inferences[i][1]
					nqueens.unassigned_vars.remove(inferences[i][0])
				nqueens.backtracking_steps = nqueens.backtracking_steps + 1
				result, assign = Backtrack(assignment, nqueens, N, Algo)
				if result:
					return result, assign
				else:
					assignment.pop(var) # If the backtrack results in failure remove the assignment made, inferences addede and reverse the domain
					nqueens.domain = copy.deepcopy(domain_copy)
					#print("********** inferences : ", inferences, " domain = ", nqueens.domain)
					for i in range(len(inferences)):
						assignment.pop(inferences[i][0])
						nqueens.unassigned_vars.append(inferences[i][0])
			else:
				assignment.pop(var) # If the inference results in failure remove the assignment made
				nqueens.domain = copy.deepcopy(domain_copy)
	if var not in assignment.keys():
		nqueens.unassigned_vars.append(var)
	return False, assignment	

if __name__ == "__main__":
	args = sys.argv
	if len(args) < 5:
		print("Error: Run command: NQueens.py ALG N CFile RFile")
		sys.exit()

	algo = str(args[1])
	N = int(args[2])
	CFile_name = str(args[3])
	RFile_name = str(args[4])

	variables = []
	domain_dict = {}

	for i in range(N):
		variables.append(i)
		domain_dict[i] = []
		for j in range(N):
			domain_dict[i].append(j)

	nqueens = QueensGraph(variables, domain_dict, N, [])
	CFile = open(CFile_name, "a")
	CFile.write("VARIABLES: \n")
	var_str = []
	for var in variables:
		var_str.append("Q"+str(var))

	#CFile.write("Q" + str(var))
	json.dump(var_str, CFile)
	CFile.write("\nQ0 is the queen in 0th column, Q1 the queen in the 1st column and so on. The value each variable takes is the row number in which the queen is placed. \n\n")
	
	CFile.write("\nDOMAIN: \n")
	#json.dump(domain_dict, CFile)
	for key in domain_dict:
		key_str = "Q"+str(key)+" : "
		CFile.write(key_str)
		json.dump(domain_dict[key], CFile)
		CFile.write("\n")

	CFile.write("\nCONSTRAINTS: \n")
	CFile.write("1) Alldiff("+str(var_str).strip('[]')+") \n")
	CFile.write("2) Row value any queen not falls in the diagnoal of any other queen \n")
	CFile.write("Elaborated Constraints below\n")
	for i in range(N):
		for j in nqueens.graph[i]:
			offset = abs(i-j)
			cons_str =  "Q"+str(i)+" != "+"Q"+str(j)+" and "+"Q"+str(i)+" != "+"Q"+str(j)+" + "+str(offset)+" and "+"Q"+str(i)+" != "+"Q"+str(j)+" - "+ str(offset)+"\n"
			CFile.write(cons_str)

	#print("Variables : ", nqueens.var)
	#print("domain_dict : ", nqueens.domain)

	#result, assignment = Backtrack(nqueens.assignment, nqueens, N, algo)

	
	#result, assignment = Backtrack(nqueens.assignment, nqueens, N, algo)
	RFile = open(RFile_name, "a")
	#json.dump(assignment, RFile)
	#variables = variables[1:] + variables[:1]
	bt_steps = []
	t0 = time.time()
	for j in range(2*N):
		#print("domain : ",nqueens.domain)
		result, assignment = Backtrack(nqueens.assignment, nqueens, N, algo)
		bt_steps.append(nqueens.backtracking_steps)
		RFile.write("Solution "+str(j)+"\n")	
		RFile.write("Assignment to variables : ")
		json.dump(assignment, RFile)
		RFile.write("\n")
		sol_op = {}
		for i in range(N):
			sol_op[i] = [0]*N
		for key in assignment:
			sol_op[key][assignment[key]] = "Q" 
			json.dump(sol_op[key], RFile)
			RFile.write("\n")
		if j<N:
			domain_dict[0] =  domain_dict[0][1:] +  domain_dict[0][:1]
		if j==N:
			variables = variables[1:] + variables[:1]
		else:
			domain_dict[1] =  domain_dict[1][1:] +  domain_dict[1][:1]
		nqueens.reset(variables, domain_dict)

	RFile.write("\nNo of solutions : "+str(2*N))
	RFile.write("\nTime taken : "+str(time.time()-t0))
	RFile.write("\nBacktracking steps: \n")
	total = 0
	for i in range(2*N):
		RFile.write("\nSolution "+str(i)+" : "+str(bt_steps[i]))
		total = total + bt_steps[i]
	RFile.write("\nTotal backtracking steps for all solutions : "+str(total))
