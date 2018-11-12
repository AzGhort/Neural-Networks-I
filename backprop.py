#### Libraries
# Standard library
import random
import string
import binascii
import numpy as np

class NeuralNetwork:    

    def __init__(self, sizes):
        self.num_layers = len(sizes)
        self.sizes = sizes
        self.biases = [np.random.randn(y, 1) for y in sizes[1:]]
        self.weights = [np.random.randn(y, x) for x, y in zip(sizes[:-1], sizes[1:])]

    def feedforward(self, a):
        for b, w in zip(self.biases, self.weights):
            a = sigmoid(np.dot(w, a)+b)
        return a

    def SGD(self, training_data, epochs, mini_batch_size, eta):
        n = len(training_data)
        for j in range(epochs):
            random.shuffle(training_data)
            mini_batches = [training_data[k:k+mini_batch_size] for k in range(0, n, mini_batch_size)]
            for mini_batch in mini_batches:
                self.update_mini_batch(mini_batch, eta)
            correctly_classified = self.evaluate(training_data)
            print("Epoch {0}: {1} / {2} points were classified correctly.".format(j, correctly_classified, mini_batch_size))
            if (correctly_classified == mini_batch_size):
                print("All points were classified correctly.")
                break

    def update_mini_batch(self, mini_batch, eta):
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        for x, y in mini_batch:
            delta_nabla_b, delta_nabla_w = self.backprop(x, y)
            nabla_b = [nb+dnb for nb, dnb in zip(nabla_b, delta_nabla_b)]
            nabla_w = [nw+dnw for nw, dnw in zip(nabla_w, delta_nabla_w)]
        self.weights = [w-(eta/len(mini_batch))*nw for w, nw in zip(self.weights, nabla_w)]
        self.biases = [b-(eta/len(mini_batch))*nb for b, nb in zip(self.biases, nabla_b)]

    def backprop(self, x, y):
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        # feedforward
        activation = x
        activations = [x] # list to store all the activations, layer by layer
        zs = [] # list to store all the z vectors, layer by layer
        for b, w in zip(self.biases, self.weights):
            z = np.dot(w, activation)+b
            zs.append(z)
            activation = sigmoid(z)
            activations.append(activation)
        # backward pass
        # (actual out - desired out)*(derivative of potential)
        delta = self.cost_derivative(activations[-1], y) * sigmoid_prime(zs[-1])
        nabla_b[-1] = delta
        nabla_w[-1] = np.dot(delta, activations[-2].transpose())
        for l in range(2, self.num_layers):
            z = zs[-l]
            sp = sigmoid_prime(z)
            delta = np.dot(self.weights[-l+1].transpose(), delta) * sp
            nabla_b[-l] = delta
            nabla_w[-l] = np.dot(delta, activations[-l-1].transpose())
        return (nabla_b, nabla_w)

    def evaluate(self, test_data):
        test_results = [(np.argmax(self.feedforward(x)), np.argmax(y)) for (x, y) in test_data]
        return sum(int(x == y) for (x, y) in test_results)

    def cost_derivative(self, output_activations, y):
        return (output_activations-y)

    def test_vector(self, vector):
        o = self.feedforward(vector)
        out = np.zeros(o.size)
        out[np.argmax(o)] = 1;
        return out
            
class LetterParser:
    def __init__(self, N):
        self.keywords = self.generate_random_words(N)
        self.N = N

    def set_keywords(self, keywords):
        self.keywords = keywords

    def get_train_set(self):
        train_set=[]
        for j in range(len(self.keywords)):
                vector = self.get_input_vector_from_word(self.keywords[j])
                output_vector = [0]*len(self.keywords)
                output_vector[j] = 1
                output_vector = np.array(output_vector)
                output_vector.shape = (self.N, 1)
                train_set.append((vector, output_vector))
        return train_set
       
    def get_input_vector_from_word(self, word):
        binary = bin(int(binascii.hexlify(word.encode()),16))
        bits35 = binary[2:37]
        output = []
        for c in bits35:
            output.append(int(c))
        output = np.array(output)
        output.shape = (35, 1)
        return output

    def generate_random_words(self, count):
        words = []
        for i in range(count):
            words.append(''.join(random.choice(string.ascii_lowercase) for _ in range(7)))
        return words    

    def test_word(self, word, nn):
        vector = self.get_input_vector_from_word(word)
        out = nn.test_vector(vector)
        print("Testing word {0}.".format(word))
        print("Output from neural network: {0}.".format(out))
        return out
        
# auxiliary math functions
def sigmoid(z):
        return 1.0/(1.0+np.exp(-z))

def sigmoid_prime(z):
        return sigmoid(z)*(1-sigmoid(z))


### MAIN
l = LetterParser(10)
train_set = l.get_train_set()
nn = NeuralNetwork([35, 4, 10])
nn.SGD(train_set, 100000, 10, 0.5)
for word in l.keywords:
    l.test_word(word, nn)
