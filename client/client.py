""" 
    1) Socket module provides the facility for the network connection : server-client progrmamming.
    2) Here we are utilizing the IPv4 family via AF_INET constant.
"""
import socket 

""" 
    1) 'psutil' is cross-platform library stands for 'process and system utility'.
    2) It provides access to the various system resources data.
    3) Few thing we can monitor using psutil are process managment, CPU, Memory, Network statistics.
"""
import psutil 

"""  Time is a built-in module in python libraries, it provides time-stamp in this project"""
import time  

""" 
    1) 'json' in python is a built-in module stands for 'javascript object notation'.
    2) It provides support to create, read, write, modify the .json files.
    3) This project utilizes the .json file to communicate data from client to server.
"""
import json 

"""
    1) Logging is build-in python module, provides the facility of logging with different severity levels.
    2) We utilize logging module and logging handler to log the program activity.
    3) logs are saved in .log file.
"""
import logging

""" subprocess is a module of python library to create the child process """
import subprocess
"""
    1) config is locally created module to access the directory object config.
    2) 'from config import config' imports the config dictionary object from local config module.
    3) It facilitates the import of various variable configuration created using jinja2 and yaml modules.
    4) Here send_time_interval variable is set to the value fetched from the config dictionary object.
"""
from config import config

""" Here, we are using the subprocess module to execute the render.py as the child process.
    This is done to create the config dictionary object from the config module.
"""
command = ['python3', '/home/hardik/seminar-project/config/render.py']
output = subprocess.check_output(command, universal_newlines=True)

""" Send time interval for resource data update to be sent to server."""
send_time_interval = config['client']['send_time_interval']


""" Key for Ceasar Encryption and Decryption, derived from config object """
Ceasar_cipher_key = config['common']['encryption_key']

"""
socket = IP + Port
IP = Server IP address
Port = Port on which server is listening for client connections.
"""
server_ip = config['common']['server_ip']
server_port = config['common']['server_port']

"""
Various Data points retrived using the psutils to be stored in the .json file.
'json' is Javascript Object Notation used for storing and communicating data over the network.
Here file name is simply 'client_data.json', it could be changed to any name suitable.
"""
client_data_file = config['client']['client_data_file']
client_log_file = config['client']['client_log_file']  

"""
    1) 'logging.basicConfig()' is a function to set the initial parameters of the logs in this program.
    2) It sets the severity level to the 'DEBUD', hence all the severity levels would be captured in.
    3) 'format' is set to give time, severity level, function, and a log message.
    4) Here 2 handlers are set
        a - 'logging.StreamHandler()' flush the logs to stdOut
        b - 'logging.FileHandler()' flush the logs to 'client.log' file 
"""
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s', 
                    handlers=[logging.StreamHandler(), logging.FileHandler(client_log_file)])

"""
    Function Name : getTimestamp
    Arguments     : None
    Return        : Present time in format
    Utility       : It simply Provides the time stamp to be used for logs and .json file
    components    : 1) 'strftime' is a function provided by the time module. It returns the time in string format.
                    2) '%Y:%m:%d:%H:%M:%S' is a placeholder string as an argument to the strftime function, indicating in what
                        format time string sould be formed and returned.     
"""
def getTimestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S")

"""
    Function Name : doCaesarEncryption
    Arguments     : 1) input_text - text to be encrypted.
                    2) key  - key to be used for encryption, derived from config object of config module.
    Return        : encrypted_text
    Utility       : 1) Ceasar cipher provides the encryption of the text for the security. It is one of the simplest encryption method.
                    2) This function replaces the current character by shifting it to key numbered character.
                    3) This function does not encrypt non-alphabetical characters.
    components    :  1) use of for loop to inerate through the input_text.
                     2) isalpha() to differentiate the non-alphabets from alphabets.
                     3) ord() to get the ascii value of alphabetic character
"""
def doCaesarEncryption(input_text, key):
    logging.info('Ceaser Cipher Begin')
    encrypted_text_string = ""
    for character in input_text:
        if character.isalpha():  
            if character.isupper():
                ascii_reference_integer = ord('A')
            else:
                ascii_reference_integer = ord('a')
            encrypted_char = chr((ord(character) - ascii_reference_integer + key) % 26 + ascii_reference_integer) 
            encrypted_text_string += encrypted_char
        else:
            encrypted_text_string += character
    
    logging.info('Ceaser Cipher End')
    return encrypted_text_string

"""
    Function Name : doCaesarDecryption
    Arguments     : 1) input_text - text to be encrypted.
                    2) key  - key to be used for encryption, derived from config object of config module.
    Return        : decrepted text.
    Utility       : To decrypt the encrypted text from the received message.
    components    : doCaesarEncryption with negative key, which would shift the character to original character -'substitute back'.
"""
def doCaesarDecryption(input_text, key):
    return doCaesarEncryption(input_text, -key)  # Reversing the key performs decryption


"""
    Function Name : clientInit
    Arguments     : None
    Return        : None
    Utility       : This is the core function of the client program.
    Flow          : 1) Collection of resource Data using the psutils module into the dictionary 'resourceData'
                    2) Converting 'resourceData' dictionary to the json formatted string 'json_formatted_resource_data'
                    3) Encryption of 'json_formatted_resource_data'
                    4) Create socket object, connect to server, send encrypted data to server.
                    5) Creating and opening of client_data.json file. Loading/Appending latest resource data to file
    components    : 1) cpu_percent() - psutil method, gives average CPU utilization in percentage over 1 second of time for all 
                       the physical/logical processors.
                    2) cpu_times_percent() - psutil method, gives average percentage of time spent by each logical/physical CPU 
                       on user, system, and idle over the span of 1 second.
                    3) time._asdict() - time module method, converts the tupple into the dictionary, which are elements of list via
                        list comprehension.
                    4) cpu_count() - psutil module method, gives the number of physical/logical CPUs present in the system.
                       Physical CPU counts if logical = False, otherwise, total count.
                    5) cpu_freq() - psutil module method, gives what frequency system CPU is using. if percpu=True, then per CPU. 
                       It also provides tha minimum and maximum frequencies supported by the CPUs.
                    6) cpu_stats() - pstuil module method, provides various stats regarding the CPU such context switches, CPU counts,
                       software/hardware interrupts, systemcalls...
                    7) virtual_memory() - psutil module method, gives various types of system's virtual memory such as total virtual
                       memory, avaialble memory, used memory, free memory, ....
                    8) swap_memory() - psutil method, provides the details of extended RAM(swap) memory.
                    9) disk_usage() - psutil method, gives statistics of the disk from root using '/'.
                    10)net_io_counters() - psutil function, provides the counters of network input/output like bytes/packet 
                       received/transmitted through the network interface.
                    11)net_connection() - psutil function, gives active netwrok connection on the system and info regarding them.
                    12)net_if_addr() - psutil function, provides the information related to the each interface such as IP addresses, 
                       Ethernet addresses, netmask, broadcast addres... Dictionary comprehension with .item() method is used to
                       brows through the dictionary object return by the net_if_stats(), key of the dictinary is name of interface.
                    13)net_if_stats() - psutil function, gives the details about the interface statistics like mode of operation, 
                       speed, MTU.. Use of dictionary comprehension and .item() method.
                    14)boot_time() - psutil function, provides simply boot time of the system.
                    15)sensors_tempurature() - psutil function, gives the dictionary containing the keys as the sensor names and
                       vlaue as the sensor tempurature. Again use of Dictionary comprehension is done.
                    16)sensors_fans() - psutil function, provides speed of the fans
                    17)sensors_battery() - psutil function, gives battery information
                    18)json.dumps() - function from json module, converts the dictionary to json formatted string.
                    19)socket.socket() - allocation of new socket object.
                    20)connect() - socket method, to establish the connection to local/remote server using server
                       IP address and open listening server port.
                    21)sendall() - socket method, to send data given in the argument to the server.
                    22)json.dump() - json function, to write the data into json file.
                    23)sleep() - time module function, suspends the program execution for mentioned time duration in argument.
"""
def clientInit():
    while True:
        logging.info('\n\n\nCollecting Resource Discrete Data Points')
        resourceData = {
            "timestamp": getTimestamp(),
            "cpu_percent": psutil.cpu_percent(interval=1, percpu=True),
            "cpu_times": [time._asdict() for time in psutil.cpu_times_percent(interval=1, percpu=True)],
            "cpu_count": psutil.cpu_count(logical=False),
            "cpu_logical_count": psutil.cpu_count(logical=True),
            "cpu_freq": [freq._asdict() for freq in psutil.cpu_freq(percpu=True)],
            "cpu_stats": psutil.cpu_stats()._asdict(),
            "virtual_memory": psutil.virtual_memory()._asdict(),
            "swap_memory": psutil.swap_memory()._asdict(),
            "disk_usage": psutil.disk_usage('/')._asdict(),
            "net_io_counters": psutil.net_io_counters()._asdict(),
            "net_connections": len(psutil.net_connections()),
            "net_if_addrs": {interface: [{'family': addr.family, 'address': addr.address, 'netmask': addr.netmask,
                                        'broadcast': addr.broadcast, 'ptp': addr.ptp} for addr in addresses]
                            for interface, addresses in psutil.net_if_addrs().items()},
            "net_if_stats": {interface: {'isup': stats.isup, 'duplex': stats.duplex, 'speed': stats.speed, 'mtu': stats.mtu}
                            for interface, stats in psutil.net_if_stats().items()},
            "users": [user.__dict__ for user in psutil.users()],
            "boot_time": psutil.boot_time(),
            "sensors_temperatures": {sensor: [reading.__dict__ for reading in readings]
                                    for sensor, readings in psutil.sensors_temperatures().items()},
            "sensors_fans": {sensor: [reading.__dict__ for reading in readings]
                            for sensor, readings in psutil.sensors_fans().items()},
            "battery": {
                'percent': psutil.sensors_battery().percent if psutil.sensors_battery() else None,
                'secsleft': psutil.sensors_battery().secsleft if psutil.sensors_battery() else None,
                'power_plugged': psutil.sensors_battery().power_plugged if psutil.sensors_battery() else None
            },
        }

        json_formatted_resource_data = json.dumps(resourceData)

        ceasar_encrypted_data = doCaesarEncryption(json_formatted_resource_data, Ceasar_cipher_key)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket_object:
            logging.info(f'Initiating Connection to Server{server_ip}:{server_port}')
            client_socket_object.connect((server_ip, server_port))
            logging.info('Text Transfer Begins to Server')
            client_socket_object.sendall(ceasar_encrypted_data.encode())

        logging.info('Text Transfer End')

        try:
            with open(client_data_file, 'r') as client_data_file_pointer:
                accumulated_data = json.load(client_data_file_pointer)
        except FileNotFoundError:
            accumulated_data = []

        accumulated_data.append(resourceData)
        with open(client_data_file, 'w') as client_data_file_pointer:
            json.dump(accumulated_data, client_data_file_pointer, indent=4)

        logging.info('client_data.json updated')

        time.sleep(send_time_interval)

clientInit()



