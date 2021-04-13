import hashlib
import file_manager
import time
import messag_controller
import sys


data = file_manager.read_file('simulation_parameters.json')


def normal_peer():
    return 'Normal_Peer'


def probable_leader():
    return 'Probable_Leader'


def leader():
    return 'Leader'


def broadcast_status():
    return 'Broadcast'


def RTT_based_status():
    return 'RTT'


def uni_cast_status():
    return 'Uni-cast'


def pick_suitable():
    return 'pick'


def AnoLE1_title():
    return "AnoLE-1"


def AnoLE2_title():
    return "AnoLE-2"


def AnoLE3_title():
    return "AnoLE-3"


def hashing(entity):
    h = hashlib.sha256()
    h.update(str(entity).encode(encoding='UTF-8'))
    return h.hexdigest()


def turn_node_down(node_path):
    file_manager.update_field_in_file(node_path, 'threaded', False)


def time_valid(timestamp, reference_time):
    return time.time() - timestamp < reference_time


def share_msg_with_neighbors(msg, network, msg_criteria, node_id=None, my_path=None):
    if msg_criteria == broadcast_status():
        registered_neighbors = file_manager.read_field_in_file(my_path, 'registered_neighbors')
        for neighbor in registered_neighbors:
            messag_controller.send_message(neighbor, msg, network)
    if msg_criteria == RTT_based_status():
        registered_neighbors = file_manager.read_field_in_file(my_path, 'registered_neighbors')
        lowest_RTT = sys.maxsize
        selected_neighbor = None
        for neighbor in registered_neighbors:
            neighbor_is_alive = file_manager.read_field_in_file(f'temporary/{neighbor}.json', 'alive')
            if neighbor_is_alive and registered_neighbors[neighbor] < lowest_RTT:
                lowest_RTT = registered_neighbors[neighbor]
                selected_neighbor = neighbor
        messag_controller.send_message(selected_neighbor, msg, network)
    if msg_criteria == uni_cast_status():
        messag_controller.send_message(node_id, msg, network)
    if msg_criteria == pick_suitable():
        my_ons = file_manager.read_field_in_file(my_path, 'ONS')
        if len(my_ons) > 0:
            passed_successfully = False
            for neighbor in my_ons:
                neighbor_is_alive = file_manager.read_field_in_file(f'temporary/{neighbor}.json', 'alive')
                if neighbor_is_alive:
                    messag_controller.send_message(neighbor, msg, network)
                    passed_successfully = True
            if passed_successfully:
                return
        else:
            share_msg_with_neighbors(msg, network, broadcast_status(), None, my_path)


def find_ONS(MST, node_id, neighbors):
    ONS = []
    for key in MST:
        if key == node_id-1:
            for neighbor in MST[key]:
                for registered_neighbor in neighbors:
                    if registered_neighbor == neighbor+1:
                        ONS.append(registered_neighbor)
    return ONS
