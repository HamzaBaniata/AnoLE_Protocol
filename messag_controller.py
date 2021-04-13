sent_msg_log = []


def get_message(node_id, simulation_network):
    my_title = int(node_id-1)
    received_messages = []
    while simulation_network.nodes[my_title]['received_msgs'].qsize() != 0:
        received_messages.append(simulation_network.nodes[my_title]['received_msgs'].get())
    return received_messages


def send_message(node_id, message, simulation_network):
    true_id = int(node_id)-1
    new_message = [true_id, message]
    if new_message not in sent_msg_log:
        sent_msg_log.append(new_message)
        simulation_network.nodes[true_id]['received_msgs'].put(message)

