""" 
    1) Socket module provides the facility for the network connection : server-client progrmamming.
    2) Here we are utilizing the IPv4 family via AF_INET constant.
"""
import socket
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
"""
    1) statistics is built-in python module for statistical calculations
    2) It is used in this program to derive the mean of set of numbers.
"""
import statistics 
"""
    pandas is python library which provides the various functions for data manupulation and analytics.
"""
import pandas as pd
"""
    1) scipy is python library which provides tools and functions for scientific usage.
    2) we are importing the stats module from the scipy library.
    3) 'skew' is a function to derive the skewness of the dataset.
    4) 'kurtosis' is a function to derive the kurtosis of the dataset.
    5) 'FitError' is a class.
"""
from scipy.stats import skew, kurtosis, FitError 
import scipy.stats as stats 
""" 
    warning modules is part of standard python libarary and allows to filter the warning generated during execution.
"""
import warnings  
warnings.filterwarnings('ignore', category=RuntimeWarning)
""" numpy stands for 'Numerical Python', it is a library for math operations"""
import numpy as np
""" 
    1) tabulate is a python library for the tabular operations.
    2) tabulate function from this libarary is used here to display and format data in tables.
"""
from tabulate import tabulate
"""
    1) prettytable is python libarary used for table creation.
    2) PrettyTable is an object of this library and allows to create table and display them.
"""
from prettytable import PrettyTable
"""
    1) colorama is a python library provides support for style and color. It works on cross-platforms.
    2) Fore and Style are the classes from colorama library
    3) colorama.init() prepares terminal/console for the support for color and style.
"""
import colorama
from colorama import Fore, Style
colorama.init()
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

"""
socket = IP + Port
IP = Server IP address
Port = Port on which server is listening for client connections.
"""
server_ip = config['common']['server_ip'] 
server_port = config['common']['server_port']
recieve_buffer_size = config['server']['receive_buffer_size']

"""
    All below files are created in the same folder as this python server program.
        1) server_data.json - contains the data received from the client.
        2) summmary.json - contains the summary data derived from server_data.json.
        3) statistics.txt - contains the statistical inferences derived from the summary.json.
        4) distribution.txt - contains the probabilistic distribution analysis of the data.
        5) server.log - contains server logs.
"""
received_server_data_json_file = config['server']['received_server_data_json_file'] 
data_summary_json_file = config['server']['data_summary_json_file']
statistical_analysis_file = config['server']['statistical_analysis_file']
probabilistic_distribution_file = config['server']['probabilistic_distribution_file'] 
server_log_file = config['server']['server_log_file']

""" Key for Ceasar Encryption and Decryption, derived from config object """
ceasar_cipher_key = config['common']['encryption_key']  # Number of positions to shift each character for encryption

"""
    1) Logging is build-in python module, provides the facility of logging with different severity levels.
    2) We utilize logging module and logging handler to log the program activity.
    3) logs are saved in .log file.
"""
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.StreamHandler(),
    logging.FileHandler(server_log_file)
])

"""
    probability_distribution_list dictionary contains distribution names as the keys and object as the value.
    For example 'norm' is the key and stats.norm is Normal Probability Distribution object from stats module.
"""
probability_distribution_list = {
    "norm": stats.norm,
    "expon": stats.expon,
    "gamma": stats.gamma,
    "lognorm": stats.lognorm,
    "beta": stats.beta,
    "weibull_min": stats.weibull_min
}

"""
    Function Name : receiveResourceDataFromClient
    Arguments     : None
    Return        : Generator object    
    Utility       : Listens for the client, accepts the client request and receives the data from client.
    components    : 1) socket.socket() - allocates new socket with IPV4 address family.
                    2) bind() - method in socket, does binding of socket and IP address
                    3) listen() - listens to the incoming client connections.
                    4) accept() - accepts the valid connection from client and returns - client's socket object and client's IP address
                    5) recv() - recieves the chuck of data : max data chunck size is specified by recieve_buffer_size
"""
def receiveResourceDataFromClient():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket_object:
        server_socket_object.bind((server_ip, server_port))
        server_socket_object.listen()
        logging.info('Listning For the Client Connection')

        while True:
            client_socket_object, client_address = server_socket_object.accept()
            
            with client_socket_object:
                logging.info('\n\n\n\033[1m\033[91mConnected by {}\033[0m'.format(client_address))

                chunk = b'' 
                while True:
                    packet = client_socket_object.recv(recieve_buffer_size)
                    if not packet:
                        break
                    chunk += packet
                yield chunk 


"""
    Function Name : serverInit
    Arguments     : None
    Return        : None
    Utility       : Core Function Of this program. All major function calls are made from here.
    Flow          : 1) Recieve data from receiveResourceDataFromClient() using iteratable generator object.
                    2) Decryption of data using ceasar cipher.
                    3) Load the  data into json formatted string.
                    4) append/save data to server_data.json file.
                    5) Summarize the server_data.json.
                    6) Print Summary.
                    7) Save summary.
                    8) Perform Statistical Analysis.
                    9) Perform Probabilistic Distribution Analysis.
    components    : 1) loads() - json method, converts recieved chunk to json formatted string.
                    2) doCaesarDecryption() - decrypt the received data.
                    3) load() - json function, loads the data from file to jason formatted stirng.
                    4) dump() - store the json fomatted data into file from json formatted string.
"""
def serverInit():
    for generator_data in receiveResourceDataFromClient():
        ceasar_decrypted_data = doCaesarDecryption(generator_data.decode(), ceasar_cipher_key)
        json_formatted_data = json.loads(ceasar_decrypted_data) 

        try:
            with open(received_server_data_json_file, 'r') as server_data_file_pointer:
                accumulated_data = json.load(server_data_file_pointer)
        except FileNotFoundError:
            accumulated_data = [] 

        accumulated_data.append(json_formatted_data)
        with open(received_server_data_json_file, 'w') as server_data_file_pointer:
            json.dump(accumulated_data, server_data_file_pointer, indent=4)
            logging.info('Updated/Created server_data.json')

        json_file_summary = summarizeJsonFileData(accumulated_data)
        printJsonFileSummary(json_file_summary)
        saveJsonFileSummary(json_file_summary)
        performVariousStatisticalAnalysis()
        PerformProbabilisticDistribution()

"""
    Function Name : summarizeJsonFileData
    Arguments     : json formatted data received from client
    Return        : dictionary object with summarized data.
    Utility       : Create summary out of entire data to display prime stats, and give user brief idea about the state of system.
    components    : 1) statistics.mean() - function in statistics libarary, derives the mean from set of numbers.
                    2) Note - Use of multiple for loops could be reduced by optimizing the code.
"""
def summarizeJsonFileData(accumulatedData):
    time_stamp = [entry["timestamp"] for entry in accumulatedData]
    cpu_utility_avg = [statistics.mean(entry["cpu_percent"]) for entry in accumulatedData]
    network_connections = [entry["net_connections"] for entry in accumulatedData]
    battery_percent = [entry["battery"]["percent"] for entry in accumulatedData]
    cpu_freq_avg = [statistics.mean([freq["current"] for freq in entry["cpu_freq"]]) for entry in accumulatedData]
    total_virtual_memory = [entry["virtual_memory"]["total"] for entry in accumulatedData]
    total_swap_memory = [entry["swap_memory"]["total"] for entry in accumulatedData]
    total_disk_usage = [entry["disk_usage"]["total"] for entry in accumulatedData]
    total_bytes_sent = [entry["net_io_counters"]["bytes_sent"] for entry in accumulatedData]
    total_bytes_recv = [entry["net_io_counters"]["bytes_recv"] for entry in accumulatedData]

    return {
        "timestamp": time_stamp,
        "average_cpu_usage": cpu_utility_avg,
        "active_network_connections": network_connections,
        "battery_percent": battery_percent,
        "average_cpu_frequency": cpu_freq_avg,
        "total_virtual_memory": total_virtual_memory,
        "total_swap_memory": total_swap_memory,
        "total_disk_usage": total_disk_usage,
        "total_bytes_sent": total_bytes_sent,
        "total_bytes_received": total_bytes_recv
    }

"""
    Function Name : printJsonFileSummary
    Arguments     : json_file_summary
    Return        : None
    Utility       : print the summary created by the summarizeJsonFileData
    components    : 1) items() - built-in method for dictionary object, here used to derive tuple of key and value.
                    2) isinstance() - finds given data type in first argument is of second argument. returns True/False.
                    3) PrettyTable() - function from prettytable, formates table object table_to_print for display purpose.
                    4) add_row() - method from table object table_to_print, to add new row with parameter and value to table.
"""
def printJsonFileSummary(json_file_summary):
    print(f"\n\n{Fore.BLUE}{Style.BRIGHT}{'DATA SUMMARY':^40}{Style.RESET_ALL}")
    
    latest_recieved_data = {}
    for parameter, value in json_file_summary.items():
        if isinstance(value, list) and len(value) > 0:
            latest_recieved_data[parameter] = value[-1]
        else:
            latest_recieved_data[parameter] = value

    table_to_print = PrettyTable(["Parameter", "Latest Value"])
    for parameter, value in latest_recieved_data.items():
        table_to_print.add_row([parameter, f"{value:.2f}" if isinstance(value, float) else value])

    title_for_the_table = Fore.BLUE + Style.BRIGHT + str(table_to_print.title) + Style.RESET_ALL
    print(title_for_the_table)
    print(table_to_print)

"""
    Function Name : saveJsonFileSummary
    Arguments     : json_file_summary
    Return        : None
    Utility       : dump the sammary derive by summarizeJsonFileData to file.
    components    : open the file and dump the data with help of open() function and dump() method.
"""
def saveJsonFileSummary(json_file_summary):
    with open(data_summary_json_file, 'w') as data_summary_json_file_pointer:
        json.dump(json_file_summary, data_summary_json_file_pointer, indent=4)

"""
    Function Name : performVariousStatisticalAnalysis
    Arguments     : None
    Return        : None
    Utility       : This function is responsible for performing the various statistical analysis on the given json summary data.
    components    : 1) read_json() - method in pandas library, provides the DataFrame object json_summary_panda_dataframe_object from .json file.
                       DataFrambe object is part of panda library, we want data in this DataFrame object to perform various stati-
                       stical analysis.
                    2) to_datetime() - function in pandas, converts the timestamp into pandas datetime data type.
                    3) drop() - method of DataFrame object, removes the timestamp from the DataFrame Object.
                    4) apply() - method of DataFrambe object, to execute function from different library, scipy.stats.
                    5) skew() - function of scipy.stats, calculates skewness values for given colom from DataFrame Object.
                    6) rename() - method of scipy.stats, renames the series of skewness vlaues to 'skewness'/'kurtosis'.
                    7) kurtosis() - function from scipy.stats, derives kurtosis distribution of given set of numbers.
                    8) set_index() - DataFrame object method, rearranges the index, here 'timestamp' becomes new index, and shifts 
                       from colom to index row position. This will help to derive the time series analysis for variables.
                    9) resample() - DataFrame method, sets the duration for resamplaing, here it is set to 'D', means daily.
                       Other options are hourly('H'), weekly('W'), Monthly('M') ....
                    10) meaan() - method to derive the mean of numbers in set created by resampling in specific duration.
                    11) describe() - DataFrame method, to derive descriptive statistics per colom such as mean, SD, min, max.
                    12) iloc - to select the row and colom to be written in file, as table is quite big.
                    13) tabulate() - function from tabulate, to format the table from partial_table or any other DataFrame Object.
                    14) to_frame() - DataFrame method, to convert the DataFrame object into single colom object.
"""
def performVariousStatisticalAnalysis():
    with open(data_summary_json_file, 'r') as data_summary_json_file_pointer:
        json_summary_panda_dataframe_object = pd.read_json(data_summary_json_file_pointer)

    json_summary_panda_dataframe_object['timestamp'] = pd.to_datetime(json_summary_panda_dataframe_object['timestamp'])
    jspdo_without_timestamp = json_summary_panda_dataframe_object.drop(columns=['timestamp'])
    skewness_derivation = jspdo_without_timestamp.apply(skew).rename('skewness')
    kurtosis_derivation = jspdo_without_timestamp.apply(kurtosis).rename('kurtosis')
    json_summary_panda_dataframe_object = json_summary_panda_dataframe_object.dropna(subset=['timestamp'])
    ts_analysis = json_summary_panda_dataframe_object.set_index('timestamp').resample('H').mean()

    with open(statistical_analysis_file, 'w') as saf_pointer:
        saf_pointer.write(f"\n\n{Fore.YELLOW}{Style.BRIGHT}{'STATISTICAL ANALYSIS':^40}\n{Style.RESET_ALL}\n")

        number_of_rows_per_table = 2 
        number_of_tables = (json_summary_panda_dataframe_object.shape[1] - 2) // number_of_rows_per_table  

        for i in range(number_of_tables):
            start_idx = 1 + i * number_of_rows_per_table
            end_idx = start_idx + number_of_rows_per_table
            saf_pointer.write(f"\n{Fore.YELLOW}{Style.BRIGHT}Descriptive Statistics (Part {i+1}):\n{Style.RESET_ALL}")
            partial_table_ds = json_summary_panda_dataframe_object.describe().iloc[:, start_idx:end_idx]
            saf_pointer.write(tabulate(partial_table_ds,
                                        headers='keys',
                                        tablefmt='pretty',
                                        colalign=("center",) * (partial_table_ds.shape[1] + 1)))

        saf_pointer.write(f"\n{Fore.YELLOW}{Style.BRIGHT}Correlation Matrix (Part 1):\n{Style.RESET_ALL}")
        partial_table_correlation_one = json_summary_panda_dataframe_object.iloc[:, 1:6]
        saf_pointer.write(tabulate(partial_table_correlation_one.corr(), headers='keys', 
                                   tablefmt='pretty', 
                                   colalign=("center",) * (partial_table_correlation_one.shape[1] + 1)))
        saf_pointer.write(f"\n{Fore.YELLOW}{Style.BRIGHT}Correlation Matrix (Part 2):\n{Style.RESET_ALL}")
        partial_table_correlatioin_two = json_summary_panda_dataframe_object.iloc[:, 6:11]
        saf_pointer.write(tabulate(partial_table_correlatioin_two.corr(), headers='keys',
                                    tablefmt='pretty', 
                                    colalign=("center",) * (partial_table_correlatioin_two.shape[1] + 1)))
        saf_pointer.write(f"\n{Fore.YELLOW}{Style.BRIGHT}Skewness:\n{Style.RESET_ALL}")
        saf_pointer.write(tabulate(skewness_derivation.to_frame(), headers='keys', tablefmt='pretty'))
        saf_pointer.write(f"\n{Fore.YELLOW}{Style.BRIGHT}Kurtosis:\n{Style.RESET_ALL}")
        saf_pointer.write(tabulate(kurtosis_derivation.to_frame(), headers='keys', tablefmt='pretty'))


        number_of_ts_tables = 2 
        number_of_ts_rows_per_table = ts_analysis.shape[1] // number_of_ts_tables
        for i in range(number_of_ts_tables):
            start_idx = i * number_of_ts_rows_per_table
            end_idx = start_idx + number_of_ts_rows_per_table

            saf_pointer.write(f"\n{Fore.YELLOW}{Style.BRIGHT}Time Series Analysis (Part {i+1}):\n{Style.RESET_ALL}")
            partial_time_series = ts_analysis.iloc[:, start_idx:end_idx]

            saf_pointer.write(tabulate(partial_time_series, headers='keys', tablefmt='pretty', colalign=("center",) * (partial_time_series.shape[1] + 1)))

    with open(statistical_analysis_file, 'r') as saf_pointer:
        print(saf_pointer.read())


"""
    Function Name : PerformProbabilisticDistribution
    Arguments     : None
    Return        : None
    Utility       : Derives Probability Distribution underlying each data set by a variable.
    components    : 1) read_json() - method in pandas library, provides the DataFrame object json_summary_panda_dataframe_object 
                       from .json file. DataFrambe object is part of panda library, we want data in this DataFrame object to 
                       perform various statistical analysis.
                    2) drop() - method of DataFrame object, removes the timestamp from the DataFrame Object.
                    3) PrettyTable() - function from prettytable, formates table object.
                    4) add_row() - method from table object table_to_print, to add new row with parameter and value to table.
"""
def PerformProbabilisticDistribution():

    with open(data_summary_json_file, 'r') as data_summary_json_file_pointer:
        json_summary_panda_dataframe_object = pd.read_json(data_summary_json_file_pointer)

    jspdo_without_timestamp = json_summary_panda_dataframe_object.drop(columns=['timestamp'])

    with open(probabilistic_distribution_file, 'w') as probabilistic_distribution_file_pointer:
        file_title = f"{Fore.GREEN}{Style.BRIGHT}\n\n PROBABILITY DISTRIBUTION ANALYSIS \n\n{Style.RESET_ALL}"
        probabilistic_distribution_file_pointer.write(file_title + "\n")

        for column in jspdo_without_timestamp.columns:
            variable_data_set = jspdo_without_timestamp[column]
            best_fit_name, best_fit_params = deriveNearMatchDistribution(variable_data_set)
            table = PrettyTable([column, best_fit_name])
            table.align = "l"

            for param_name, param_value in best_fit_params.items():
                table.add_row([param_name, param_value])

            probabilistic_distribution_file_pointer.write(str(table) + "\n\n")
    
    with open(probabilistic_distribution_file, 'r') as probabilistic_distribution_file_pointer:
        print(probabilistic_distribution_file_pointer.read())

"""
    Function Name : deriveNearMatchDistribution
    Arguments     : variable_data_set derived in PerformProbabilisticDistribution()
    Return        : 
    Utility       : Derives the near/best probability distribution for the data set given.
    components    : 1) fit() - method of perticular distribution object, determines variable_data_set fits the distribution or not.
                    2) sum() - function from numpy, to sumup the elements of any array.
                    3) log() - function of numpy, finds natural logorithm of array of numbers.
                    4) pdf() - method of distribution_object, calculates the probability density function for variable_data_set
                    """
def deriveNearMatchDistribution(variable_data_set):
    near_match_name = None
    near_match_parameters = None
    negative_float = float('-inf')

    for distribution_name, distribution_object in probability_distribution_list.items():
        try:
            distribution_parameters = distribution_object.fit(variable_data_set)
            logorithmic_pdf_sum = np.sum(np.log(distribution_object.pdf(variable_data_set, *distribution_parameters)))
            if logorithmic_pdf_sum > negative_float:
                near_match_name = distribution_name
                if distribution_object.shapes is not None:
                    near_match_parameters = dict(zip(distribution_object.shapes, distribution_parameters[:-2]))
                else:
                    near_match_parameters = {}
                negative_float = logorithmic_pdf_sum
        except (RuntimeError, ValueError, FitError):
            continue

    return near_match_name, near_match_parameters


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


# Start storing data from the client
serverInit()




