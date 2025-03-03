from collections.abc import Callable
import itertools
import random

class Network:
    # A Network captures:
    # 1. A list of boolean node states.
    # 2. The directed edges between nodes.
    # 3. For each node, the boolean truth table where inputs are current state of dependency
    #    nodes and outputs are whether the node turns on or off.
    # 1. Is captured with a list of ints like [0, 1, 1, 0, 0]
    # 2. Is captured with dict[int, list[int]] like:
    #    {0: [1], 1: [1], 2: [0, 3], 3: [2, 0]}
    # 3. Is captured with a truth table dictionary where the keys are string-representations of
    #    binary inputs like:
    #    {"000": 0, "001": 0, "010": 1, "011": "0", "100": 1, "101": 1, "110": 1", "111": 0}
    # The ratio of 0 to 1 outputs are dictated by the node_rule_activation_probability.
    def __init__(
        self,
        num_nodes,
        num_edges,
        edge_algorithm: Callable[[int, int], dict[int, list]],
        node_rule_activation_probability: float = 0.5,
        initial_state_probability: float = 0.5
    ):
        self.num_nodes = num_nodes
        self.num_edges = num_edges
        self.node_dependency_lists = Network._cleanup_adjacency(edge_algorithm(num_nodes, num_edges))
        self.node_transition_rules = self._generate_rules(node_rule_activation_probability)
        self.node_states = [0 for _ in range(num_nodes)]
        self.initialize_state(initial_state_probability)
    
    def _generate_rules(
        self,
        node_rule_activation_probability: float = 0.5
    ):
        # _generate_rules generates the truth table mapping for each node
        # which accepts an input of all nodes which it depends on and outputs the truth
        # value.
        node_rules = []
        for _, adjacent_nodes in self.node_dependency_lists.items():
            truth_keys = [
                Network._create_truth_key(truth_inputs)
                for truth_inputs in Network._generate_base_truth_inputs(len(adjacent_nodes))
            ]
            node_rule = Network._assign_truth_mapping(truth_keys, node_rule_activation_probability)
            node_rules.append(node_rule)
        return node_rules
    

    @staticmethod
    def _assign_truth_mapping(
        truth_keys: list[str],
        node_rule_activation_probability: float
    ):
        # _assign_truth_mapping accepts a list of truth_keys which are the string representation of
        # truth table input values and an edge_transition_probability. It returns a mapping of
        # truth table inputs to truth table outputs where the probability of transition to on is dictated by
        # the node_rule_activation_probability. 
        return {
            truth_key: random.choices([0, 1], weights=[1 - node_rule_activation_probability, node_rule_activation_probability])[0]
            for truth_key in truth_keys
        }


    @staticmethod
    def _generate_base_truth_inputs(num_inputs: int) -> list[tuple[int]]:
        # _generate_base_truth_inputs generates the boolean inputs of a truth
        # table for num_inputs. For a 2-input table, the result would be
        # [(0, 0), (0, 1), (1, 0), (1, 1)]
        return list(itertools.product([0, 1], repeat=num_inputs))

    
    @staticmethod
    def _create_truth_key(truth_inputs: list[int]):
        # _create_truth_key creates a string representation of a list of
        # ints. This is intended to be used for truth table map creation.
        # Given an input like [0, 1, 0], returns: "010"
        return ''.join(str(i) for i in truth_inputs)
    

    @staticmethod
    def _cleanup_adjacency(adjacency_list: dict[int, list]):
        # _cleanup_adjacency finds all nodes which are not adjacent to anything and sets
        # them adjacent to themselves.
        new_adjacency_list = {}
        for node, adjacent_nodes in adjacency_list.items():
            if not adjacent_nodes:
                adjacent_nodes = [node]
            new_adjacency_list[node] = adjacent_nodes
        return new_adjacency_list


    def initialize_state(self, probability_of_on: float = 0.5):
        # initialize_state creates the first list of node states randomly based on the probability_of_on.
        new_states = []
        for _ in range(self.num_nodes):
            is_on = random.choices([0, 1], weights=[1 - probability_of_on, probability_of_on])[0]
            new_states.append(is_on)
        self.node_states = new_states
    

    def _get_dependency_node_states(self, dependency_nodes: list[int]):
        # get_dependency_node_states returns the state of the nodes from the dependency_nodes list.
        return [self.node_states[n] for n in dependency_nodes]


    def transition_state(self):
        # transition_state uses the current node_state and the node_transition_rules to change
        # the node_states.
        new_node_states = []
        for node_key, adjacent_nodes in self.node_dependency_lists.items():
            node_rule_map = self.node_transition_rules[node_key]
            truth_key = Network._create_truth_key(self._get_dependency_node_states(adjacent_nodes))
            new_node_states.append(node_rule_map[truth_key])
        self.node_states = new_node_states
    

    def introduce_disturbance(
        self,
        disturbance_probability: float = 0.2
    ):
        # introduce_disturbance conditionally inverts node states. A node state is inverted
        # if the a random disturbance_probability is calculated to be true.
        new_node_states = []
        for node_state in self.node_states:
            value = node_state
            should_invert = random.choices([0, 1], weights=[1 - disturbance_probability, disturbance_probability])[0]
            if should_invert:
                new_node_states.append(0 if value == 1 else 1)
            else:
                new_node_states.append(value)
        self.node_states = new_node_states
    

    def print_stats(self):
        print("Total Number of Edges: ", sum(len(nodes) for nodes in self.node_dependency_lists.values()))
        print("Highest number of Edges: ", max(len(nodes) for nodes in self.node_dependency_lists.values()))


def edge_algorithm_uniform(
    num_nodes: int,
    num_edges: int
) -> dict[int, list]:
    # Given a number of nodes and a desired number of edges,
    # generate edges randomly such that each edge has 0/num_nodes
    # probability of being attached to any node.
    # Note that there is a potential for a node not to be adjacent to anything.
    adjacency_list = {
        i: []
        for i in range(num_nodes)
    }
    edges = set()
    while len(edges) < num_edges:
        # edges are directional with "from" node coming first.
        # node0 -> node1 == (node0, node1)
        # Nodes only need to know about their inputs and not who they are outputting to.
        node0 = random.randint(0, num_nodes-1)
        node1 = random.randint(0, num_nodes-1)
        # nodes can connect to themselves
        edge = tuple((node0, node1))
        if edge not in edges:
            edges.add(edge)
            adjacency_list[node1].append(node0)
    return adjacency_list


# TODO
# def edge_algorithm_affinity(
#     num_nodes: int,
#     num_edges: int,
#     affinity_factor: float
# ) -> dict[int, list]:
#     # Given a number of nodes, desired number of edges, and an affinity factor,
#     # generate edges such that each edge has a higher likelihood of being connected
#     # to a node from which many edges connect to based on the affinity factor.
