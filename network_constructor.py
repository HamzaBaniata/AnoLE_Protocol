import networkx as nx
import random
from itertools import combinations
import file_manager
import shared_functions

data = file_manager.read_file("simulation_parameters.json")
DRFC = data['DRFC']


def construct_network(number_of_nodes, network_model, parameter):
    constructed_network = None
    connected = False
    while not connected:
        if network_model == 1:
            constructed_network = construct_ER_network(number_of_nodes, float(parameter))
        if network_model == 2:
            constructed_network = construct_BA_network(number_of_nodes, int(parameter))
        connected = nx.is_connected(constructed_network)
    print('[SUCCESS] Network is built')
    return constructed_network


def construct_ER_network(number_of_nodes, probability_of_edges):
    network = nx.Graph()
    network.name = 'Erdös – Rényi(ER)'
    for i in range(number_of_nodes):
        network.add_node(i)
        network.nodes[i]['id'] = i+1
        network.nodes[i]['registered_neighbors'] = {}
        network.nodes[i]['ONS'] = []
        network.nodes[i]['DRFC'] = DRFC
        network.nodes[i]['previous_MST'] = []
        network.nodes[i]['alive'] = True
        network.nodes[i]['AnoLE_records'] = {}
        network.nodes[i]['current_MST'] = []
        network.nodes[i]['threaded'] = False
        network.nodes[i]['current_leader'] = None
        network.nodes[i]['status'] = shared_functions.normal_peer()
        network.nodes[i]['path'] = 'temporary/' + str(i+1) + '.json'
        network.nodes[i]['default_round_time'] = data['default_round_time(s)']
    for u, v in combinations(network, 2):
        if random.random() < probability_of_edges:
            if u != v:
                network.add_edge(u, v, weight=random.randint(1, 100))
                network.nodes[u]['registered_neighbors'][v+1] = network.edges[u, v]['weight']
                network.nodes[v]['registered_neighbors'][u+1] = network.edges[u, v]['weight']
    return network


def construct_BA_network(number_of_nodes, parameter):
    network = nx.barabasi_albert_graph(number_of_nodes, parameter)
    network.name = 'Barabási – Albert(BA)'
    for i in range(number_of_nodes):
        j = i+1
        network.nodes[i]['id'] = j
        network.nodes[i]['registered_neighbors'] = {}
        network.nodes[i]['ONS'] = []
        network.nodes[i]['DRFC'] = DRFC
        network.nodes[i]['previous_MST'] = []
        network.nodes[i]['current_MST'] = []
        network.nodes[i]['alive'] = True
        network.nodes[i]['AnoLE_records'] = {}
        network.nodes[i]['threaded'] = False
        network.nodes[i]['current_leader'] = None
        network.nodes[i]['status'] = shared_functions.normal_peer()
        network.nodes[i]['path'] = 'temporary/' + str(i+1) + '.json'
        network.nodes[i]['default_round_time'] = data['default_round_time(s)']
    for u, v in combinations(network, 2):
        if network.has_edge(u, v) and 'weight' not in network.edges[u, v]:
            network.edges[u, v]['weight'] = random.randint(1, 100)
            network.nodes[u]['registered_neighbors'][v+1] = network.edges[u, v]['weight']
            network.nodes[v]['registered_neighbors'][u+1] = network.edges[u, v]['weight']
    return network



