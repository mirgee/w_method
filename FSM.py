import csv
import pprint
from itertools import combinations, permutations
from partition import Partition


class FSM(object):

	def __init__(self):
		self.states = set()
		# Key: (state, edge), value: (next_state, output)
		self.transitions = {}
		# (from_state, to_state)
		self.transitions_set = set()
		self.actions = []
		self.default_output = None
		self.final_states = []
		self.init_state = None
		self.input_alphabet = set()
		self.output_alphabet = set()
		self._covered_transitions = set()
		# (state, k) -> partition
		self.partitions = []
		self.char_set = dict()

	def read_from_csv(self, filename):
		"""Read the FSM from a csv file on filename."""
		with open(filename, "r") as f:
			reader = csv.reader(f, delimiter=",", skipinitialspace=True)
			self.init_state = next(reader)[1]
			self.final_states.append(next(reader)[1])
			self.default_output = next(reader)[1]
			next(reader)
			next(reader)
			l = next(reader)
			self.actions.extend([l[1], l[2], l[3]])
			self.input_alphabet.update([l[1], l[2], l[3]])
			for l in reader:
				for i, a in enumerate(self.actions):
					self.states.update([l[0].strip(), l[1+i]])
					self.output_alphabet.add(l[len(self.actions)+2+i])
					self.transitions[(l[0].strip(), a)] = (l[1+i],l[len(self.actions)+2+i])
					self.transitions_set.add((l[0].strip(), l[1+i], a))

	def completify(self):
		"""Returns a complete copy of self."""
		"""Not necessary for the input FSM."""
		pass

	def _next_state(self, curr_state, action):
		"""Returns next state."""
		return self.transitions[(curr_state, action)][0]

	def _next_output(self, curr_state, action):
		"""Returns next action."""
		return self.transitions[(curr_state, action)][1]

	def _successors(self, state):
		"""Returns all successive states of state."""
		successors = []
		for a in self.actions:
			successors.append(self._next_state(state, a))
		return successors

	def _outputs(self, state):
		"""Returns the sequence of outputs from state."""
		outputs = []
		for a in self.actions:
			outputs.append(self._next_output(state, a))
		return outputs

	def transition(self, state, input_word):
		"""Returns end state and output after inputting input_word from state."""
		s = state
		o = []
		for a in input_word:
			o.append(self._next_output(s, a))
			s = self._next_state(state, a)
		return s, o

	def state_covering_paths(self):
		"""Returns state cover of the FSM."""
		# The same, but only if action leads to a STATE we already visited.
		remaining = []
		visited = set()
		previous = dict() # state -> parent, action
		paths = dict() # state -> path to cover

		previous[self.init_state] = (None, None)
		remaining.append(self.init_state)
		while len(remaining) > 0:
			parent = remaining.pop()
			if parent is not self.init_state:
				paths[parent] = self.action_history(parent, previous)
			for a in self.actions:
				child = self._next_state(parent, a)
				if child in visited or child == parent:
					continue
				if child not in remaining:
					remaining.append(child)
					previous[child] = (parent, a)
					self._covered_transitions.add((parent, child, a))
			visited.add(parent)
		return paths

	def action_history(self, parent, previous):
		"""Helper method to reconstruct input sequence."""
		history = []
		state = parent
		while state is not self.init_state:
			history.insert(0, previous[state][1])
			state = previous[state][0]
		return history

	def state_cover(self):
		"""Find state cover of the FSM."""
		paths = self.state_covering_paths().values()
		l = []
		for p in paths:
			if p not in l:
				l.append(p)
		return l

	def edge_cover_wasteful(self):
		"""Returns edge cover of the FSM."""
		# This is the simplest method, far from optimal
		state_cover = self.state_cover()
		edge_cover = self.state_cover()
		for path in state_cover:
			for a in self.actions:
				new_path = path.append(a)
				if new_path not in state_cover:
					edge_cover.append(new_path)
		return edge_cover

	def edge_cover(self):
		"""Find edge cover of FSM."""
		paths = self.state_covering_paths()
		edge_cover = self.state_cover()
		for transition in self.transitions_set - self._covered_transitions:
			if transition[0] != self.init_state:
				path = paths[transition[0]]
			edge_cover.append(path.append(transition[2]))
		return edge_cover


	def equivalence_partitions(self):
		"""Returns list of equivalence partitions?"""
		partition = Partition()
		for state in self.states:
			partition.add_state(state, self._outputs(state))
		partition.update()
		self.partitions.append(partition)
		while True:
			partition = Partition()
			for state in self.states:
				print(state)
				partition.add_state(state, self.partitions[-1].successors_partitions(self._successors(state)))
			partition.update()
			self.partitions.append(partition)
			print
			if len(self.states) == len(partition): # or partition == partitions[-1]:
				break
		return self.partitions

	def _find_r_b(self, q1, q2):
		"""Find the index of the first separate partitions q1 and q2 belong to."""
		for r, partition in enumerate(self.partitions):
			if partition.state_to_class[q1] == partition.state_to_class[q2]:
				continue
			if r > 0:
				s1 = partition.successors_partitions(self._successors(q1))
				s2 = partition.successors_partitions(self._successors(q2))
			else:
				s1 = self._outputs(q1)
				s2 = self._outputs(q2)
			i = 0
			while s1[i] == s2[i]:
				i += 1
			b = self.actions[i]
			return r, b

	def characterization_set(self):
		"""Returns a characterizations set of the FSM found using the W-method."""
		W = dict()
		for q1, q2 in combinations(self.states, r=2):
			z = []
			r, b = self._find_r_b(q1, q2)
			z.insert(0, b)
			for _ in range(r):
				q1, q2 = self._next_state(q1, b), self._next_state(q2, b)
				_, b = self._find_r_b(q1,q2)
				z.insert(0, b)
			W[(q1, q2)] = z
			W[(q2, q1)] = z

		self.char_set = W

		return W

	def apply_char_set(self):
		"""Prints the output of each state after applying sequence from characterization set."""
		char_set = []
		for seq in self.char_set.values():
			if seq not in char_set:
				char_set.append(seq)

		for s in self.states:
			print(s)
			for seq in char_set:
				print(self.transition(s, seq)[1])

	def diff_table(self):
		"""Returns r for each tuple of states."""
		# table = [[-1 for _ in self.states] for _ in self.states]
		table = {}
		for q1, q2 in permutations(self.states, r=2):
			table[(q1, q2)] = self._find_r_b(q1, q2)[0]
			table[(q2, q1)] = table[(q1, q2)]
		return table

	def find_z(self):
		"""Derive the test set."""
		pass

if __name__ == "__main__":
	f = FSM()
	f.read_from_csv("g1A04A.csv")
	pp = pprint.PrettyPrinter()
	pp.pprint(f.equivalence_partitions())
	pp.pprint(f.characterization_set())
	f.apply_char_set()
	pp.pprint(f.diff_table())