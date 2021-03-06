"""
TODO: add comments
"""

# Importing packages
import logger
import executer
import sys
import job
import psutil

if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding('utf8')

pid = psutil.Process().pid
logger_obj = logger.Logger(filename='rdf-bridge.log', instance_id=pid)
executer_obj = executer.Executer()
logger_obj.write_log('Program is started with process id: '+str(pid))

if len(sys.argv) != 8:
    logger_obj.write_log('Program needs path_to_file_temp, go path, path to config, funtion cmd, partition size and name for the generated file. Example: python bootstrap.py "data-store/rdf-sample-1 data-store/rdf-sample-2" /usr/local/go/bin/go config/rdf-sample.conf all 50 rdf-sample')
    exit()

path_to_file_temp  = sys.argv[1]
config_file = sys.argv[3]
partition_size=int(sys.argv[5])
directory_name = 'data-store/'
directory_name_bitmat = 'bitmat-data-store/'
file_name = sys.argv[6]
which = sys.argv[7]
file_prefix = 'full-'
file_prefix_b = 'bitmat-'
path_to_file = directory_name+file_prefix+file_name
path_to_temp_file = directory_name+file_prefix
path_to_bitmat_file = directory_name_bitmat+file_prefix_b+file_name
path_to_bitmat_file_config = path_to_bitmat_file

logger_obj.write_log('Setup directory paths.')

''' Executes commands
'''
def executeCommands(commands, exe):
    for v in commands:
        logger_obj.write_log('Command started: '+v)
        if exe == True:
            output = executer_obj.run(v)
        else:
            continue
        if output[0] != 0:
            logger_obj.write_log('Command failed with code ['+str(output[0])+']: '+v, 2)
        logger_obj.write_log('Command finished: '+v)

''' Cleans old logs
'''
def cleanLogs():
    logger_obj.write_log('Cleaning logs')
    clean = [
        'mkdir bitmat-data-store',
        'rm bitmat-data-store/*',
        'rm log/*',
        'rm database/*'
    ]
    executeCommands(clean, True)
    logger_obj.write_log('Finished cleaning logs')

''' Generates BitMat Database
'''
def generateBitMatDatabase(test, which):
    logger_obj.write_log('Running commands to generate BitMat Database')

    path_to_file_temp_list = path_to_file_temp.split(' ')
    commands_part1 = []
    sub_all = ''
    pre_all = ''
    obj_all = ''

    for index in path_to_file_temp_list:
        file_name_temp = index.split('/')
        file_name_temp = path_to_temp_file+file_name_temp[-1]
        cmd_set = [
            'cat '+index+' > '+file_name_temp,
            'sed -i \'s/://g\' '+file_name_temp,
            'sed -i \'s/ /:/g\' '+file_name_temp,
            'sort -u '+file_name_temp+' | awk -F: \'{print $1}\' > '+file_name_temp+'-sub',
            'sed -i \'s/\/\//:\/\//g\' '+file_name_temp+'-sub',
            'sort -u '+file_name_temp+' | awk -F: \'{print $2}\' > '+file_name_temp+'-pre',
            'sed -i \'s/\/\//:\/\//g\' '+file_name_temp+'-pre',
            'sort -u '+file_name_temp+' | awk -F: \'{print $3}\' > '+file_name_temp+'-obj',
            'sed -i \'s/\/\//:\/\//g\' '+file_name_temp+'-obj',
            'rm '+file_name_temp
            # 'sed -i \'s/:/ /g\' '+file_name_temp,
            # 'sed -i \'s/\/\//:\/\//g\' '+file_name_temp,
        ]
        sub_all = sub_all + file_name_temp+'-sub '
        pre_all = pre_all + file_name_temp+'-pre '
        obj_all = obj_all + file_name_temp+'-obj '
        commands_part1 = commands_part1 + cmd_set

    commands_part2 = [
        'cat '+sub_all+' > '+path_to_file+'-sub',
        'rm '+sub_all,
        'cat '+pre_all+' > '+path_to_file+'-pre',
        'rm '+pre_all,
        'cat '+obj_all+' > '+path_to_file+'-obj',
        'rm '+obj_all,
        'sort '+path_to_file+'-sub -T /home/alamgir/ | uniq > '+path_to_file+'-sub-all',
        'rm '+path_to_file+'-sub',
        'wc -l < '+path_to_file+'-sub-all > '+path_to_file+'-sub-all-count',
        'sort '+path_to_file+'-pre -T /home/alamgir/ | uniq > '+path_to_file+'-pre-all',
        'rm '+path_to_file+'-pre',
        'wc -l < '+path_to_file+'-pre-all > '+path_to_file+'-pre-all-count',
        'sort '+path_to_file+'-obj -T /home/alamgir/ | uniq > '+path_to_file+'-obj-all',
        'rm '+path_to_file+'-obj',
        'wc -l < '+path_to_file+'-obj-all > '+path_to_file+'-obj-all-count',
        'sort '+path_to_file+'-sub-all '+path_to_file+'-obj-all -T /home/alamgir/ | uniq -d > '+path_to_file+'-common',
        'wc -l < '+path_to_file+'-common > '+path_to_file+'-common-count',
        'sort '+path_to_file+'-sub-all '+path_to_file+'-common -T /home/alamgir/ | uniq -u > '+path_to_file+'-sub-left',
        'sort '+path_to_file+'-obj-all '+path_to_file+'-common -T /home/alamgir/ | uniq -u > '+path_to_file+'-obj-left',
        'cat '+path_to_file+'-common '+path_to_file+'-sub-left > '+path_to_file+'-sub-all',
        'cat '+path_to_file+'-common '+path_to_file+'-obj-left > '+path_to_file+'-obj-all',
        'rm '+path_to_file+'-sub-left',
        'rm '+path_to_file+'-obj-left',
        'cat '+path_to_file_temp+' > '+path_to_file,
        'sed -i \'s/://g\' '+path_to_file,
        'sed -i \'s/\/\//:\/\//g\' '+path_to_file,
        'wc -l < '+path_to_file+' > '+path_to_file+'-count',
        'python rdf-bridge/load-rdf.py sub '+path_to_file+' '+str(partition_size)+' '+file_name,
        'python rdf-bridge/load-rdf.py pre '+path_to_file+' '+str(partition_size)+' '+file_name,
        'python rdf-bridge/load-rdf.py obj '+path_to_file+' '+str(partition_size)+' '+file_name
    ]

    if which == '1':
        commands = commands_part1
    elif which == '2':
        commands = commands_part2
    else:
        commands = commands_part1 + commands_part2

    executeCommands(commands, test)
    logger_obj.write_log('Finished commands to generate BitMat Database')

''' Execute job to conert string to interger ids in BitMat database
'''
def convertStringToInt():
    logger_obj.write_log('Executing job now')
    job_obj = job.Job(logger_obj, partition_size, path_to_file, path_to_bitmat_file, file_name)
    job_obj.execute()
    logger_obj.write_log('Job finished')

''' Build indexes
'''
def buildIndexes():
    logger_obj.write_log('Running commands to generate Indexes')
    commands = [
        'sort -T /home/alamgir/ -u -n -t: -k2 -k1 -k3 '+path_to_bitmat_file+' > '+path_to_bitmat_file+'_spo',
        'sort -T /home/alamgir/ -u -n -t: -k2 -k3 -k1 '+path_to_bitmat_file+' | awk -F: \'{print $3":"$2":"$1}\' > '+path_to_bitmat_file+'_ops',
        'sort -T /home/alamgir/ -u -n -t: -k1 -k2 -k3 '+path_to_bitmat_file+' | awk -F: \'{print $2":"$1":"$3}\' > '+path_to_bitmat_file+'_pso',
        'sort -T /home/alamgir/ -u -n -t: -k3 -k2 -k1 '+path_to_bitmat_file+' | awk -F: \'{print $2":"$3":"$1}\' > '+path_to_bitmat_file+'_pos',
    ]
    executeCommands(commands, True)
    logger_obj.write_log('Finished commands to generate Indexes')

''' Make config file
'''
def makeConfig():
    logger_obj.write_log('Making config file')
    job_obj = job.Job(logger_obj, partition_size, path_to_file, path_to_bitmat_file, file_name)
    file_content = ''
    file_content = file_content+ 'BITMATDUMPFILE_SPO=database/uniprot_800m_spo_pdump'+ "\n"
    file_content = file_content+ 'BITMATDUMPFILE_OPS=database/uniprot_800m_ops_pdump'+ "\n"
    file_content = file_content+ 'BITMATDUMPFILE_PSO=database/uniprot_800m_pso_sdump'+ "\n"
    file_content = file_content+ 'BITMATDUMPFILE_POS=database/uniprot_800m_pos_odump'+ "\n"
    file_content = file_content+ 'RAWDATAFILE_SPO='+path_to_bitmat_file_config+'_spo'+ "\n"
    file_content = file_content+ 'RAWDATAFILE_OPS='+path_to_bitmat_file_config+'_ops'+ "\n"
    file_content = file_content+ 'RAWDATAFILE_PSO='+path_to_bitmat_file_config+'_pso'+ "\n"
    file_content = file_content+ 'RAWDATAFILE_POS='+path_to_bitmat_file_config+'_pos'+ "\n"
    file_content = file_content+ 'RAWDATAFILE='+path_to_bitmat_file_config+''+ "\n"
    file_content = file_content+ 'NUM_SUBJECTS='+ job_obj.get_count(path_to_file+'-sub-all')+ "\n"
    file_content = file_content+ 'NUM_PREDICATES='+ job_obj.get_count(path_to_file+'-pre-all')+ "\n"
    file_content = file_content+ 'NUM_OBJECTS='+ job_obj.get_count(path_to_file+'-obj-all')+ "\n"
    file_content = file_content+ 'NUM_COMMON_SO='+ job_obj.get_count(path_to_file+'-common')+ "\n"
    file_content = file_content+ 'ROW_SIZE_BYTES=4'+ "\n"
    file_content = file_content+ 'GAP_SIZE_BYTES=4'+ "\n"
    file_content = file_content+ 'TMP_STORAGE=output'+ "\n"
    file_content = file_content+ 'TABLE_COL_BYTES=5'+ "\n"
    file_content = file_content+ 'COMPRESS_FOLDED_ARRAY=0'+ "\n"
    file_obj = open(config_file, 'w')
    file_obj.write(file_content)
    file_obj.close()
    logger_obj.write_log('Finished making config file')

if sys.argv[4] == 'all':
    cleanLogs()
    generateBitMatDatabase(True, which)
    convertStringToInt()
    buildIndexes()
    makeConfig()
elif sys.argv[4] == 'clean':
    cleanLogs()
elif sys.argv[4] == 'generate':
    generateBitMatDatabase(True, which)
elif sys.argv[4] == 'test':
    generateBitMatDatabase(False, which)
elif sys.argv[4] == 'convert':
    convertStringToInt()
elif sys.argv[4] == 'build':
    buildIndexes()
elif sys.argv[4] == 'make':
    makeConfig()

# Terminate log utility
logger_obj.breakup_with_log()