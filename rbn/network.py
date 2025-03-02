from collections.abc import Callable
import itertools
import random

class Network:
    def __init__(
        self,
        num_nodes,
        num_edges,
        edge_algorithm: Callable[[int, int], dict[int, list]],
        edge_transition_probability: float = 0.5,
        initial_state_probability: float = 0.5
    ):
        self.num_nodes = num_nodes
        self.num_edges = num_edges
        self.adjacency_list = Network._cleanup_adjacency(edge_algorithm(num_nodes, num_edges))
        self.node_rules = self._generate_rules(edge_transition_probability)
        self.node_states = [0 for _ in range(num_nodes)]
        self.initialize_state(initial_state_probability)
    
    def _generate_rules(
        self,
        edge_transition_probability: float = 0.5
    ):
        # _generate_rules generates the truth table mapping for each node
        # which accepts an input of all adjacent nodes and outputs the truth
        # value.
        node_rules = []
        for _, adjacent_nodes in self.adjacency_list.items():
            truth_keys = [
                Network._create_truth_key(truth_inputs)
                for truth_inputs in Network._generate_base_truth_inputs(len(adjacent_nodes))
            ]
            node_rule = Network._assign_truth_mapping(truth_keys, edge_transition_probability)
            node_rules.append(node_rule)
        return node_rules
    

    @staticmethod
    def _assign_truth_mapping(
        truth_keys: list[str],
        edge_transition_probability: float
    ):
        return {
            truth_key: random.choices([0, 1], weights=[1 - edge_transition_probability, edge_transition_probability])[0]
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
        new_states = []
        for _ in range(self.num_nodes):
            is_on = random.choices([0, 1], weights=[1 - probability_of_on, probability_of_on])[0]
            new_states.append(is_on)
        self.node_states = new_states
    

    def get_dependent_node_states(self, adjacent_nodes: list[int]):
        return [self.node_states[n] for n in adjacent_nodes]


    def transition_state(self):
        new_node_states = []
        for node_key, adjacent_nodes in self.adjacency_list.items():
            node_rule_map = self.node_rules[node_key]
            truth_key = Network._create_truth_key(self.get_dependent_node_states(adjacent_nodes))
            new_node_states.append(node_rule_map[truth_key])
        self.node_states = new_node_states


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
        node0 = random.randint(0, num_nodes-1)
        node1 = random.randint(0, num_nodes-1)
        # nodes can connect to themselves
        edge = tuple(sorted((node0, node1)))
        if edge not in edges:
            edges.add(edge)
            adjacency_list[node0].append(node1)
            if node0 == node1:
                # don't link to oneself twice
                continue
            adjacency_list[node1].append(node0)
    return adjacency_list
