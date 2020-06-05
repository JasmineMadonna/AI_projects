import nltk,sys, os, json
from numpy.random import choice

class ngram:
	#This class has methods and variables to compute the unigrams, bigrams, trigrams and its probabilities
	def __init__(self, stop_words):
		self.tokens = []
		self.stop_words = stop_words
		self.unigrams = {}
		self.unigrams_list = []
		self.bigrams = {}
		self.trigrams = {}
		self.unigram_prob = []
		self.bigram_prob = {}
		self.trigram_prob = {}

	#Reads all files in the auth_dir and tokenzie them. Removes the punctation and converts all tokens to lower case after tokenizing
	def read_and_tokenize(self, auth_dir):
		for filename in os.listdir(auth_dir):
			file_content = open(auth_dir+"/"+filename).read()
			tokens_upper = nltk.word_tokenize(file_content)
			tokens_file = [token.lower() for token in tokens_upper if token.isalpha()]

			self.tokens = self.tokens + tokens_file

			
		self.tokens[:] = [token for token in self.tokens if token not in self.stop_words]

	#Identifies the unigrams, bigrams and trigrams and their respective counts and stores dict datastructure
	def ngram_count(self):
		size = len(self.tokens)
		#print("Total num of tokens = ", size)
		for i in range(size):
			token = self.tokens[i]
			if token in self.unigrams.keys():
				self.unigrams[token] = self.unigrams[token] + 1
			else:
				self.unigrams[token] = 1
				self.unigrams_list.append(token)

			if i < (size-1):
				bigram = self.tokens[i], self.tokens[i+1]
				if bigram in self.bigrams.keys():
					self.bigrams[bigram] = self.bigrams[bigram] + 1
				else:
					self.bigrams[bigram] = 1

			if i < (size-2):
				trigram = self.tokens[i], self.tokens[i+1], self.tokens[i+2]
				if trigram in self.trigrams.keys():
					self.trigrams[trigram] = self.trigrams[trigram] + 1
				else:
					self.trigrams[trigram] = 1
	
	#Computes unigram, bigram and trigram probability and writes to PROB-FILE 
	def compute_prob(self, prob_file):
		size = len(self.tokens)
		prob_file = open(prob_file, 'a')

		prob_file.write("-------------- Unigrams -----------------\n")
		num_unigrams = len(self.unigrams)
		for key in self.unigrams_list:
			prob = self.unigrams[key]/size
			self.unigram_prob.append(prob)
			prob_file.write(str(key)+" \t\t | "+str(prob)+"\n")

		prob_file.write("\n\n-------------- Bigrams -------------- \n")
		for bigram in self.bigrams:
			self.bigram_prob[bigram] = self.bigrams[bigram]/self.unigrams[bigram[0]]
			prob_file.write(str(bigram[0])+" : "+str(bigram[1])+" \t\t | "+str(self.bigram_prob[bigram])+"\n")
		#print(self.bigram_prob)

		prob_file.write("\n\n-------------- Trigrams -------------- \n")
		for trigram in self.trigrams:
			self.trigram_prob[trigram] = self.trigrams[trigram]/self.bigrams[trigram[0], trigram[1]]
			prob_file.write(str(trigram[0])+" "+str(trigram[1])+" : "+str(trigram[2])+" \t\t | "+str(self.trigram_prob[trigram])+"\n")
		#print(self.trigram_prob)

	#Generate a sequence of 20 tokens based on the ngram probability
	def generate_seq(self):
		seq = ""
		words = []
		prob = []
		first_word = choice(self.unigrams_list, 1, p=self.unigram_prob)[0]
		seq = seq+first_word
		words.append(first_word)
		index = self.unigrams_list.index(first_word)
		prob.append(round(self.unigram_prob[index],6))
		#print("first seq = ", seq)

		second_word_list = []
		second_prob_dist = []
		for key in self.bigram_prob:
			if first_word == key[0]:
				second_word_list.append(key[1])
				second_prob_dist.append(self.bigram_prob[key])
			if len(second_word_list) == self.unigrams[first_word]:
				break

		second_word = choice(second_word_list, 1, second_prob_dist)[0]
		seq = first_word+" "+second_word
		words.append(second_word)
		prob.append(round(self.bigram_prob[first_word,second_word], 5))

		for i in range(2,20):
			third_list = []
			third_prob_dist = []
			for key in self.trigram_prob:
				if key[0] == words[i-2] and key[1] == words[i-1]:
					third_list.append(key[2])
					third_prob_dist.append(self.trigram_prob[key])
				if len(third_list) == self.bigrams[words[i-2], words[i-1]]:
					break

			if len(third_list) == 0:
				return seq, prob

			third_word = choice(third_list, 1, third_prob_dist)[0]
			words.append(third_word)
			prob.append(round(self.trigram_prob[words[i-2], words[i-1], third_word],5))
			seq = seq+" "+third_word

		return seq, prob


if __name__ == "__main__":
	args = sys.argv
	if len(args) < 4:
                print("Error: run command : MarkovChain_EC.py AUTH-DIR/ PROB-FILE RESULT-FILE")
                sys.exit()

	input_dir = str(args[1])
	prob_file = str(args[2])
	res_file = open(str(args[3]),'a')
	#res_file = open(str(args[3]), 'a')

			
	stop_words_txt = open("EnglishStopwords.txt").read()
	stop_words = nltk.word_tokenize(stop_words_txt)

	ngram = ngram(stop_words)
	ngram.read_and_tokenize(input_dir)
	ngram.ngram_count()
	ngram.compute_prob(prob_file)

	
	for i in range(10):
		seq, prob = ngram.generate_seq()
		res_file.write("\n\n"+str(i+1)+". "+seq+"\n")
		res_file.write("Probability : ")
		json.dump(prob, res_file)
