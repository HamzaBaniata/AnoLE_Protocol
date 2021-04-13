import network_constructor
import file_manager
import random
import DONS_node
import threading
from multiprocessing import Queue
import time
import shared_functions
import messag_controller


data = file_manager.read_file('simulation_parameters.json')
number_of_nodes = data['number_of_nodes']
network_model = data['network_model(1:ER,2:BA)']
parameter = data['parameter (ER:0<p<=1,BA:1<=m<n)']
threads = []
globals()['simulated_network'] = network_constructor.construct_network(number_of_nodes, network_model, parameter)
global simulated_network
expected_number_of_PLs = 0
total_number_of_exchanged_messages = 0
total_time_till_end_of_phase2 = 0


def get_DRFC():
    if network_model == 1:
        return parameter * number_of_nodes / 2
    if network_model == 2:
        return parameter / 2


def worker(node_id, network):
    # select non-threaded node and work for it
    my_path = 'temporary/' + str(node_id) + '.json'
    checker = True
    while checker:
        checker = file_manager.read_field_in_file(my_path, 'threaded')
        DONS_node.ping(my_path, network)
        DONS_node.receive_message(my_path, network)
    number_of_ex_msgs = len(messag_controller.sent_msg_log)
    file_manager.update_field_in_file(my_path, 'no_sent_msgs', number_of_ex_msgs)
    print(f"************************\nNode {node_id} is done working\n*******************************")
    finalize_phase1(network)


def finalize_phase1(network):
    global expected_number_of_PLs
    global total_number_of_exchanged_messages
    expected_number_of_PLs -= 1
    if expected_number_of_PLs == 0:
        for n in network.nodes:
            path = f'temporary/{n+1}.json'
            shared_functions.turn_node_down(path)


def run_simulation(network):
    nodes = network.nodes.data()
    globals()['failed_node_id'] = fail_node()
    global failed_node_id
    global expected_number_of_PLs
    expected_number_of_PLs = len(list(network.neighbors(failed_node_id-1)))
    globals()['start_time'] = time.time()
    for i in range(len(nodes)):
        if i != failed_node_id - 1:
            file_manager.update_field_in_file(f'temporary/{i + 1}.json', 'DRFC', get_DRFC())
            t = threading.Thread(target=worker, args=(i+1, network,))
            threads.append(t)
            t.start()


def fail_node():
    random_node = random.randint(1, number_of_nodes)
    file_manager.update_field_in_file('temporary/' + str(random_node) + '.json', 'alive', False)
    print('node ' + str(random_node) + ' failed')
    return random_node


def provide_AnoLE_analysis(network):
    nodes = network.nodes.data()
    pilot_votes = {}
    global start_time
    number_of_leaders = 0
    global failed_node_id
    global total_time_till_end_of_phase2
    for t in threads:
        t.join()
    global total_number_of_exchanged_messages
    for i in range(len(nodes)):
        if i != failed_node_id-1:
            my_path = f'temporary/{i+1}.json'
            voted_for = file_manager.read_field_in_file(my_path, 'current_leader')
            my_num_of_sent_msgs = file_manager.read_field_in_file(my_path, 'no_sent_msgs')
            total_number_of_exchanged_messages += my_num_of_sent_msgs
            try:
                message_waiting_time_before_termination = data['default_round_time(s)']/2
                my_elapsed_time = file_manager.read_field_in_file(my_path, 'time_MST_received') - (start_time + message_waiting_time_before_termination)
                if my_elapsed_time > total_time_till_end_of_phase2:
                    total_time_till_end_of_phase2 = my_elapsed_time
            except:
                pass
            if voted_for not in pilot_votes:
                pilot_votes[voted_for] = 1
            else:
                pilot_votes[voted_for] += 1
            leadership = file_manager.read_field_in_file(f'temporary/{i+1}.json', 'status')
            if leadership == shared_functions.leader():
                number_of_leaders += 1
    print("******************[RESULTS]************************"
          "\ntotal votes by network nodes, determined by PLs, are as follows:")
    print(str(pilot_votes) + '\n')
    if number_of_leaders == 1:
        print('\n[SUCCESS]')
    else:
        print('\n[FAIL]')
    print(f'Number of nodes who announced themselves as leaders at the end of simulation is ({number_of_leaders})')
    print(f'Total number of exchanged messages = {total_number_of_exchanged_messages}')
    print(f'Total time from AnoLE trigger appeared till all nodes received the MST = {total_time_till_end_of_phase2}')
    print("******************[END]****************************")


def prepare_nodes():
    for node in simulated_network:
        path = 'temporary/' + str(node+1) + '.json'
        simulated_network.nodes[node]['received_msgs'] = Queue()
        file_manager.update_field_in_file(path, 'threaded', True)
        print('The following node is up:  ' + str(node))


if __name__ == '__main__':
    file_manager.initiate_files(simulated_network.nodes.data())
    prepare_nodes()
    run_simulation(simulated_network)
    provide_AnoLE_analysis(simulated_network)
