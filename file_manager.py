import json
import os
import shutil
import lock


def read_file(file_path):
    while True:
        try:
            with open(file_path, 'r') as f:
                file = json.load(f)
                break
        except Exception as e:
            print(e)
            print('this error appeared in read_file for file: ' + file_path)
    return file


def write_file(file_path, contents):
    locked = lock.lock()
    if locked:
        while True:
            try:
                with open(file_path, 'w') as f:
                    json.dump(contents, f, indent=4)
                print('success writing')
                break
            except Exception as e:
                print(e)
                print('this error appeared in write_file for file: ' + file_path)
        lock.unlock()


def update_field_in_file(path, field, updated_value):
    locked = lock.lock()
    if locked == 'key':
        while True:
            try:
                with open(path, 'r+') as old_file:
                    readable_file = json.load(old_file)
                    readable_file[field] = updated_value
                    old_file.seek(0)
                    json.dump(readable_file, old_file, indent=4)
                    old_file.truncate()
                break
            except Exception as e:
                print(e)
                print('this error appeared in update_field_in_file for file: ' + path)
        lock.unlock()


def read_field_in_file(path, field):
    locked = lock.lock()
    if locked == 'key':
        while True:
            try:
                with open(path, 'r') as f:
                    file = json.load(f)
                    break
            except Exception as e:
                print(e)
                print('this error appeared in read_field_in_file for file: ' + path)
        lock.unlock()
        return file[field]


def initiate_files(network_data):
    clean_directory('temporary')
    for i in range(len(network_data)):
        node = network_data[i]
        path = 'temporary/' + str(node['id']) + '.json'
        with open(path, 'w') as f:
            json.dump(node, f, indent=4)
    print('[SUCCESS] Corresponding files initiated')


def clean_directory(directory_path):
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
            print('this error appeared in clean_directory')
    while lock.locking_queue.qsize() > 0:
        lock.lock()
    lock.unlock()
