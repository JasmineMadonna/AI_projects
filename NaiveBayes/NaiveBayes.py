import numpy as np
import pandas as pd
import sys, json

class NaiveBayes:
	def __init__(self):
		self.pos_class = 0
		self.neg_class = 0
		self.class_prob = []
		self.cond_prob = {} # Dictionary to store the conditional probabilities of each attribute given the class 0 or 1

	#Computes the number of positive and negative class and calculate its corresponding probabilities and store in class_prob
	def count_y(self, y):
		for val in y:
			if val==1:
				self.pos_class = self.pos_class+1
		self.neg_class = len(y)-self.pos_class

		self.class_prob.append(self.neg_class/len(y))
		self.class_prob.append(self.pos_class/len(y))

	#Computes the conditional probability for the given attribute given the class
	def compute_freq(self, X, feature, y):
		freq = {}
		for i in range(len(X)):
			val = X[i]
			if val in freq.keys():
				if y[i] == 0:
					freq[val][0] = freq[val][0]+1
				else:
					freq[val][1] = freq[val][1]+1
			else:
				freq[val] = [0,0]
				if y[i] == 0:
					freq[val][0] = freq[val][0]+1
				else:
					freq[val][1] = freq[val][1]+1
		return freq

	#Function to train the training data by computing the conditional probabilities of all attribute given each class output
	def train(self, X_train, y_train):
		self.count_y(y_train)

		for col in X_train.columns:
			#print(col)
			freq = self.compute_freq(X_train[col], col, y_train)
			#print(freq)
			prob = {}
			for key in freq:
				prob[key] = [0,0]
				if freq[key][0] == 0:
					freq[key][0] = 2
				if freq[key][1] == 0:
					freq[key][1] = 2
		
				prob[key][0] = freq[key][0]/self.neg_class
				prob[key][1] = freq[key][1]/self.pos_class
			#print(prob)
			self.cond_prob[col] = prob

	#returns predicted class y for the given test data
	def test(self, test_data):
		pred_y = []
		for index, row in test_data.iterrows():
			pos_prob = 1
			neg_prob = 1
			for col in test_data.columns:
				neg_prob = neg_prob*self.cond_prob[col][row[col]][0]
				pos_prob = pos_prob*self.cond_prob[col][row[col]][1]
			if pos_prob > neg_prob:
				pred_y.append(1)
			else:
				pred_y.append(0)
		return pred_y
		
if __name__ == "__main__":	
	args = sys.argv
	train_file = str(args[1])
	test_file = str(args[2])
	MFile_name = str(args[3])
	RFile_name = str(args[4])

	train_data = pd.read_csv(train_file)
	NB = NaiveBayes()
	y = train_data['class']
	#NB.count_y(y)

	X_train = train_data.drop(['class'], axis=1)

	NB.train(X_train, y)

	MFile = open(MFile_name, "a")
	MFile.write("\nClass probabilities\n")
	MFile.write("\nP(Class 0) = "+str(NB.class_prob[0]))
	MFile.write("\nP(Class 1) = "+str(NB.class_prob[1]))

	MFile.write("\n\nConditional probabilities for each attribute")
	for col in X_train.columns:
		MFile.write("\n\nAttribute : "+col)
		MFile.write("\n\t Class 0 \t\t Class 1")
		for key in NB.cond_prob[col]:
			MFile.write("\n"+str(key))
			MFile.write("\t"+str(NB.cond_prob[col][key][0]))
			MFile.write("\t"+str(NB.cond_prob[col][key][1]))
		#df = pd.DataFrame(NB.cond_prob[col])
		#df.to_json(MFile)
		#df.to_csv(MFile)

	test_data  = pd.read_csv(test_file)
	test_y = test_data['class'].values
	test_X = test_data.drop(['class'], axis=1)
	pred_y = NB.test(test_X)

	RFile = open(RFile_name, "a")
	RFile.write("Predicted class\n")
	json.dump(pred_y, RFile)

	#Computing confusion matrix
	TP = 0
	TN = 0
	FP = 0
	FN = 0

	for i in range(len(test_y)):
		if test_y[i] == 1 and pred_y[i] == 1:
			TP = TP + 1	
		if test_y[i] == 0 and pred_y[i] == 0:
			TN = TN + 1	
		if test_y[i] == 0 and pred_y[i] == 1:
			FP = FP + 1	
		if test_y[i] == 1 and pred_y[i] == 0:
			FN = FN + 1	

	RFile.write("\n\nConfusion Matrix: \n")
	RFile.write("\t True \t False \n")
	RFile.write("True \t "+str(TP)+"\t "+str(FP)+"\n")
	RFile.write("False \t "+str(FN)+"\t "+str(TN)+"\n")
