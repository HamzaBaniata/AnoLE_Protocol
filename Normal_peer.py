import file_manager
import shared_functions
import sys
import time

last_message_received_at = time.time()


def receive_msg(messages, my_path, network):
    round_time = file_manager.read_field_in_file(my_path, 'default_round_time')
    my_id = file_manager.read_field_in_file(my_path, 'id')
    my_registered_neighbors = file_manager.read_field_in_file(my_path, 'registered_neighbors')
    global last_message_received_at
    for message in messages:
        last_message_received_at = time.time()
        if shared_functions.time_valid(message['timestamp'], round_time):
            if message['type'] == shared_functions.AnoLE3_title():
                if message['leader'] == file_manager.read_field_in_file(my_path, 'current_leader'):
                    file_manager.update_field_in_file(my_path, 'time_MST_received', time.time())
                    my_ONS = shared_functions.find_ONS(message['MST'], str(my_id), my_registered_neighbors)
                    file_manager.update_field_in_file(my_path, 'ONS', my_ONS)
                    print(f'\n****\nNode {my_id} received the MST and computed its ONS')
                    print('This node is ready to optimally share data with the network\n****\n')
                    print(my_ONS)
            else:
                shared_functions.share_msg_with_neighbors(message, network, shared_functions.pick_suitable(), None, my_path)
                # run Algorithm-2
                # print("Algorithm2 started.")
                check_local_records(my_path, message, network)
    if not shared_functions.time_valid(last_message_received_at, round_time/2):
        shared_functions.turn_node_down(my_path)


# Algorithm-2
def check_local_records(my_path, message, network):
    AnoLE_records = file_manager.read_field_in_file(my_path, 'AnoLE_records')
    my_id = file_manager.read_field_in_file(my_path, 'id')
    condition1 = message['failed_node'] in AnoLE_records
    if condition1:
        if message['nominee'] not in AnoLE_records[message['failed_node']]['nominees']:
            AnoLE_records[message['failed_node']]['nominees'].append(message['nominee'])
    else:
        AnoLE_records[message['failed_node']] = {}
        AnoLE_records[message['failed_node']]['nominees'] = [message['nominee']]
        AnoLE_records[message['failed_node']]['voted'] = False
    # run Algorithm-3
    # print('Algorithm3 started')
    M_K, RFC_value = RFC(my_path, message['failed_node'])
    if len(M_K) > 0:
        condition3 = message['nominee'] in M_K
        condition4 = M_K in AnoLE_records['failed_node']['nominees']
    else:
        condition3 = True
        condition4 = True
    condition5 = len(AnoLE_records[message['failed_node']]['nominees']) >= RFC_value
    condition6 = not AnoLE_records[message['failed_node']]['voted']
    if condition3 and condition4 and condition5 and condition6:
        current_leader = AnoLE_records[message['failed_node']]['nominees'][0]
        print(str(my_id) + " has voted to PL: " + message['nominee'])
        # use Algorithm-4 to find LV
        my_AnoLE2_message = construct_AnoLE2_message(message, my_id, current_leader, find_LV(my_path))
        AnoLE_records[message['failed_node']]['voted'] = True
        shared_functions.share_msg_with_neighbors(my_AnoLE2_message, network, shared_functions.pick_suitable(), None, my_path)
        print('AnoLE-2 messages are being exchanged... hold!')
        file_manager.update_field_in_file(my_path, 'current_leader', current_leader)
    file_manager.update_field_in_file(my_path, 'AnoLE_records', AnoLE_records)


# Algorithm-3
def RFC(my_path, failed_node):
    M_K = []
    current_MST = file_manager.read_field_in_file(my_path, 'current_MST')
    if len(current_MST) > 0:
        M_K = find_neighbors(my_path, failed_node)
    RFC_value = len(M_K)
    if RFC_value == 0:
        RFC_value = file_manager.read_field_in_file(my_path, 'DRFC')
    return M_K, RFC_value


def find_neighbors(my_path, failed_node):
    neighbors = []
    current_MST = file_manager.read_field_in_file(my_path, 'current_MST')
    for row in current_MST:
        if row[0] == failed_node:
            for column in row:
                if current_MST[0][column.index] != row[0]:
                    if current_MST[row][column] < sys.maxsize:
                        neighbors.append(current_MST[0][column.index])
    return neighbors


def construct_AnoLE2_message(received_message, self_id, my_leader, my_LV):
    message = {'type': shared_functions.AnoLE2_title(),
               'failed_node': received_message['failed_node'],
               'timestamp': received_message['timestamp'],
               'nominee': received_message['nominee'],
               'voter': shared_functions.hashing(self_id),
               'elected': my_leader,
               'my_lv': my_LV}
    return message


# Algorithm-4
def find_LV(my_path):
    anonymized_LV = []
    hashed_ids = []
    weights = []
    registered_neighbors = file_manager.read_field_in_file(my_path, 'registered_neighbors')
    for neighbor in registered_neighbors:
        hashed_ids.append(shared_functions.hashing(neighbor))
        weights.append(registered_neighbors[neighbor])
    anonymized_LV.append(hashed_ids)
    anonymized_LV.append(weights)
    return anonymized_LV
