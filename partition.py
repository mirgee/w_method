class Partition(object):

	def __init__(self):
		# (outputs) -> states  // per round
		self.outputs_to_states = dict()
		self.state_to_class = dict()
		self.class_to_states = dict()
		self.state_to_successors_partitions = dict()
		self._states = set()

	def __repr__(self):
		return str(self.class_to_states)

	def __cmp__(self, other):
		for c, states in self.class_to_states:
			for state in states:
				if state not in other.class_to_states[c]:
					return -1
		return 0

	def __len__(self):
		return len(self.class_to_states)

	def equiv_class(self, state):
		for i, v in enumerate(self.outputs_to_states.values()):
			if state in v:
				return i
		return -1

	def add_state(self, state, output):
		output = tuple(output)
		if output not in self.outputs_to_states:
			self.outputs_to_states[output] = set()
		self.outputs_to_states[output].add(state)
		self._states.add(state)

	def successors_partitions(self, successors):
		partitions = []
		for successor in successors:
			partitions.append(self.equiv_class(successor))
		return partitions

	def update(self):
		for state in self._states:
			state_class = self.equiv_class(state)
			# self.state_to_class[state] = state_class
			if state_class not in self.class_to_states:
				self.class_to_states[state_class] = []
			self.class_to_states[state_class].append(state)
