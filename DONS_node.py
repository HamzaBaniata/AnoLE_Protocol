import file_manager
import shared_functions
import time
import sys
import messag_controller
import Probable_leader
import Normal_peer

data = file_manager.read_file('simulation_parameters.json')
infinity = sys.maxsize


def ping(my_path, network):
    registered_neighbors = file_manager.read_field_in_file(my_path, 'registered_neighbors')
    keys_list = list(registered_neighbors)
    failed_neighbors = []
    for key in keys_list:
        neighbors_path = 'temporary/' + key + '.json'
        neighbor_alive = file_manager.read_field_in_file(neighbors_path, 'alive')
        if not neighbor_alive:
            failed_neighbors.append(key)
            del registered_neighbors[key]
    for failed_neighbor in failed_neighbors:
        hashed_id_of_neighbor = shared_functions.hashing(failed_neighbor)
        Probable_leader.start(time.time(), my_path, registered_neighbors, network, hashed_id_of_neighbor)


# Algorithm-1
def receive_message(my_path, network):
    my_id = file_manager.read_field_in_file(my_path, 'id')
    my_status = file_manager.read_field_in_file(my_path, 'status')
    messages = messag_controller.get_message(my_id, network)
    if my_status == shared_functions.normal_peer():
        Normal_peer.receive_msg(messages, my_path, network)
    if my_status == shared_functions.probable_leader():
        Probable_leader.receive_msg(messages, my_path, network)
    if my_status == shared_functions.leader():
        pass












