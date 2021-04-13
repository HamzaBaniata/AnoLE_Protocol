import time
import file_manager
import random
import shared_functions
import networkx as nx
import L


def start(trigger_time, my_path, registered_neighbors, network, hashed_id_of_neighbor):
    file_manager.update_field_in_file(my_path, 'status', shared_functions.probable_leader())
    file_manager.update_field_in_file(my_path, 'registered_neighbors', registered_neighbors)
    round_time = file_manager.read_field_in_file(my_path, 'default_round_time')
    random_time = random.randint(0, int(round_time/2))
    print(f'one of my neighbors has failed. This node will wait for {random_time} seconds')
    print("Status is changed from NP to PL\n")
    file_manager.update_field_in_file(my_path, 'votes', {})
    file_manager.update_field_in_file(my_path, 'LVs', [])
    time.sleep(random_time)
    react_to_fail(my_path, hashed_id_of_neighbor, trigger_time, network)


def react_to_fail(my_path, failed_node_id, time_of_failure, network):
    my_info = file_manager.read_file(my_path)
    AnoLE1_message = construct_AnoLE1_message(failed_node_id, shared_functions.hashing(my_info['id']), time_of_failure)
    shared_functions.share_msg_with_neighbors(AnoLE1_message, network, shared_functions.pick_suitable(), None, my_path)
    print("AnoLE-1 messages are being exchanged.. hold!")


def construct_AnoLE1_message(hash_of_failed_node_id, hash_of_PL, time_of_failure):
    message = {'type': shared_functions.AnoLE1_title(),
               'failed_node': hash_of_failed_node_id,
               'nominee': hash_of_PL,
               'timestamp': time_of_failure}
    return message


def receive_msg(list_of_messages, my_path, network):
    for message in list_of_messages:
        received_votes = file_manager.read_field_in_file(my_path, 'votes')
        failed_node = message['failed_node']
        msg_timestamp = message['timestamp']
        round_time = file_manager.read_field_in_file(my_path, 'default_round_time')
        time_is_valid = shared_functions.time_valid(msg_timestamp, round_time)
        if time_is_valid:
            shared_functions.share_msg_with_neighbors(message, network, shared_functions.pick_suitable(), None, my_path)
            if message['type'] == shared_functions.AnoLE2_title():
                count_votes(my_path, message)
        else:
            if failed_node in received_votes:
                recognize_leader(my_path, received_votes[failed_node], network)
                break


# Algorithm-5
def count_votes(my_path, AnoLE2):
    failed_node = AnoLE2['failed_node']
    voter = AnoLE2['voter']
    elected_leader = AnoLE2['elected']
    lv = AnoLE2['my_lv']
    votes = file_manager.read_field_in_file(my_path, 'votes')
    LVs = file_manager.read_field_in_file(my_path, 'LVs')
    failure_timestamp = AnoLE2['timestamp']
    if failed_node not in votes:
        votes[failed_node] = {'timestamp': failure_timestamp,
                              'info': {elected_leader: {'voters': [voter],
                                                        'votes': 1}}}
        LVs.append([failed_node, voter, lv])
    if elected_leader not in votes[failed_node]['info']:
        votes[failed_node]['info'][elected_leader] = {'voters': [voter],
                                                      'votes': 1}
        LVs.append([failed_node, voter, lv])
    if voter not in votes[failed_node]['info'][elected_leader]['voters']:
        votes[failed_node]['info'][elected_leader]['voters'].append(voter)
        votes[failed_node]['info'][elected_leader]['votes'] += 1
        LVs.append([failed_node, voter, lv])
    file_manager.update_field_in_file(my_path, 'votes', votes)
    file_manager.update_field_in_file(my_path, 'LVs', LVs)


# Algorithm-6
def recognize_leader(my_path, votes_record, network):
    global_max_votes = 0
    leader = None
    my_id = file_manager.read_field_in_file(my_path, 'id')
    failed_node_info = votes_record['info']
    my_received_LVs = file_manager.read_field_in_file(my_path, 'LVs')
    for probable_leader in failed_node_info:
        probable_leader_votes = failed_node_info[probable_leader]['votes']
        if probable_leader_votes > global_max_votes:
            global_max_votes = probable_leader_votes
            leader = probable_leader
    file_manager.update_field_in_file(my_path, 'current_leader', leader)
    if leader == shared_functions.hashing(my_id):
        file_manager.update_field_in_file(my_path, 'status', shared_functions.leader())
        print('node ' + str(my_id) + " announced itself as leader. it obtained: " + str(global_max_votes) + ' votes')
        print(f'this leader has obtained a total of {len(my_received_LVs)} LVs')
        NT, connected = construct_NT(my_path)
        if connected:
            dict_NT = nx.to_dict_of_dicts(NT)
            MST = L.construct_MST(dict_NT)
            my_registered_neighbors = file_manager.read_field_in_file(my_path, 'registered_neighbors')
            dict_MST = nx.to_dict_of_dicts(MST)
            ONS = shared_functions.find_ONS(dict_MST, str(my_id), my_registered_neighbors)
            AnoLE3_msg = construct_AnoLE3_msg(shared_functions.hashing(my_id), MST)
            file_manager.update_field_in_file(my_path, 'ONS', ONS)
            shared_functions.share_msg_with_neighbors(AnoLE3_msg, network, shared_functions.pick_suitable(), None, my_path)
        else:
            print('constructed network topology is not connected. No MST can be built.')
    else:
        file_manager.update_field_in_file(my_path, 'status', shared_functions.normal_peer())
        print('node ' + str(my_id) + " changed its status from PL to NP")
        print("and announced the leader as to be: " + leader + ' with ' + str(global_max_votes) + ' votes')


# Algorithm-7
def construct_NT(my_path):
    my_received_LVs = file_manager.read_field_in_file(my_path, 'LVs')
    NT = nx.Graph()
    for LV in my_received_LVs:
        if LV[1] not in NT:
            NT.add_node(LV[1])
            for neighbor in LV[2][0]:
                if neighbor not in NT:
                    NT.add_node(neighbor)
        for weight in LV[2][1]:
            neighbor_index = LV[2][1].index(weight)
            NT.add_edge(LV[1], LV[2][0][neighbor_index], weight=weight)
    print('[SUCCESS]: Anonymized Network Topology is built by the leader')
    connected = nx.is_connected(NT)
    if nx.is_connected(NT):
        print('Network is connected:')
    else:
        print('Network is not connected')
    print(f'it has {NT.number_of_nodes()} nodes')
    # as_dict = nx.to_dict_of_dicts(NT)
    # print(as_dict)
    return NT, connected


def construct_AnoLE3_msg(my_id, MST):
    message = {'type': shared_functions.AnoLE3_title(),
               'timestamp': time.time(),
               'leader': my_id,
               'MST': MST}
    return message
