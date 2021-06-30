import optparse
import os
from collections import OrderedDict
from loader import load_train_step_datasets, load_test_step_datasets
import LstmModel
import LstmCrfModel
import torch
import torch.autograd as autograd
import torch.nn as nn
import torch.optim as optim
import numpy as np
from utils import evaluate
import matplotlib.pyplot as plt

#TO DO add Dictionary size

optparser = optparse.OptionParser()
optparser.add_option(
    "-T", "--train", default="/data/likai/project/NLPHomework/Homework2/data/ner_train.dat",
    help="Train set location"
)
optparser.add_option(
    "-D", "--dev", default="/data/likai/project/NLPHomework/Homework2/data/ner_dev.key",
    help="Development dataset"
)
#optparser.add_option(
#    "-t", "--test", default="data/eng.testb",
#    help="Development dataset"
#)
optparser.add_option(
    "-l", "--lower", default="0",
    type='int', help="Lowercase words (this will not affect character inputs)"
)
optparser.add_option(
    "-z", "--zeros", default="0",
    type='int', help="Replace digits with 0"
)
#optparser.add_option(
#    "-p", "--pre_emb", default="",
#    help="Location of pretrained embeddings"
#)
optparser.add_option(
    "-s", "--save_emb", default="/data/likai/word_vector/glove/glove.6B.300d.txt",
    help="Location of pretrained embeddings"
)
optparser.add_option(
    "-v", "--vocab_size", default="8000",
    type='int', help="vocab_size"
)
optparser.add_option(
    "-e", "--embedding_dim", default="300",
    type='int', help="words hidden dimension"
)
optparser.add_option(
    "-d", "--hidden_dim", default="100",
    type='int', help="LSTM hidden dimension"
)
opts = optparser.parse_args()[0]

# Parse parameters
Parse_parameters = OrderedDict()
Parse_parameters['lower'] = opts.lower == 1
Parse_parameters['zeros'] = opts.zeros == 1
#Parse_parameters['pre_emb'] = opts.pre_emb
Parse_parameters['save_emb'] = opts.save_emb
Parse_parameters['train'] = opts.train
Parse_parameters['vocab_size'] = opts.vocab_size

# Check parameters validity
assert os.path.isfile(opts.train)
assert os.path.isfile(opts.dev)
#assert os.path.isfile(opts.test)

# load datasets
train_data, tagset_size, dictionaries = load_train_step_datasets(Parse_parameters)
print('target_size:'+str(tagset_size))
dev_data = load_test_step_datasets(Parse_parameters, opts.dev, dictionaries)

#test_data = load_test_step_datasets(Parse_parameters, opts.test, dictionaries)

#embedding_dim, hidden_dim, vocab_size, tagset_size
# Model parameters
Model_parameters = OrderedDict()
Model_parameters['vocab_size'] = opts.vocab_size
Model_parameters['embedding_dim'] = opts.embedding_dim
Model_parameters['hidden_dim'] = opts.hidden_dim
Model_parameters['tagset_size'] = tagset_size


#model = LstmModel.LSTMTagger(Model_parameters)
model = LstmCrfModel.BiLSTM_CRF(Model_parameters)
optimizer = optim.Adam(model.parameters(), lr=0.01)

n_epochs = 10 # number of epochs over the training set


accuracys = []
precisions = []
recalls = []
FB1s =[]


for epoch in range(n_epochs): # again, normally you would NOT do 300 epochs, it is toy data
		epoch_costs = []

		# evaluate
		eval_result = evaluate(model, dev_data, dictionaries)
		accuracys.append(eval_result['accuracy'])
		precisions.append(eval_result['precision'])
		recalls.append(eval_result['recall'])
		FB1s.append(eval_result['FB1'])

		print("Starting epoch %i..." % (epoch))
		for i, index in enumerate(np.random.permutation(len(train_data))):
				print(str(i))
				# Step 1. Remember that Pytorch accumulates gradients.  We need to clear them out
				# before each instance
				model.zero_grad()
    
				# Step 2. Get our inputs ready for the network, that is, turn them into Variables
				# of word indices.
				sentence_in = autograd.Variable(torch.LongTensor(train_data[index]['words']))
				targets = autograd.Variable(torch.LongTensor(train_data[index]['tags']))

				# Step 3. Run our forward pass.
				#tag_scores = model(sentence_in)

				# Step 4. Compute the loss, gradients, and update the parameters by calling
				# optimizer.step()
				#loss = loss_function(tag_scores, targets)
				loss = model.get_loss(sentence_in, targets)
				epoch_costs.append(loss.data.numpy())
				loss.backward()
				optimizer.step()

				#if i%100 == 0:
				#	print("Interation:"+str(i))
				
		print("Epoch %i, cost average: %f" % (epoch, np.mean(epoch_costs)))

print("Plot final result")
print('accuracys:')
print(accuracys)
print('')
print('precisions:')
print(precisions)
print('recalls:')
print(recalls)
print('')
print('FB1s:')
print(FB1s)
print('')

'''
plt.figure()
plt.plot(accuracys,"g-",label="accuracy")
plt.plot(precisions,"r-.",label="precision")
plt.plot(recalls,"m-.",label="recalls")
plt.plot(FB1s,"k-.",label="FB1s")

plt.xlabel("epoches")
plt.ylabel("%")
plt.title("CONLL2000 dataset")

plt.grid(True)
plt.legend()
plt.show()
'''
