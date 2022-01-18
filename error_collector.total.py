# v.1.2. Time of error will be added if number of errors less than limit
# Supports old and new time formats, can detect incorrect time format
# v.1.3 Files open exceptions are added
# total - all errors from directory in one file
import sys
import time
import os

def get_list_of_logs():
    """
    Create list of log files in current folder
    """
    list_of_files = os.listdir()
    list_of_logs = [f for f in list_of_files if f.endswith('.log')]
    return list_of_logs

def split_error_string(s, keyword):
    """
    Split string using keyword as delimiter
    """
    a = s.split(keyword)
    if len(a) > 2: # if keyword present in error description
        a[1] = keyword.join(a[1:])
    return a[0].rstrip(), a[1].lstrip().rstrip()

def collect_errors(loglist, keyword, dictname):
    """
    Create dictionary of unique errors in loglist
    """
    for e in loglist:
        if e.find(keyword) >=0:
            datetime, error_text = split_error_string(e, keyword)
            if dictname.get(error_text):
                dictname[error_text] += 1
            else:
                dictname[error_text] = 1
    #print(e, dictname)
    return dictname

def file_to_list(fname):
    """
    Read text file, create list of strings
    """
    loglist = []
    try:
        with open(fname) as f:
            for e in f:
                loglist.append(e)
    except IOError: 
        print('Log file {} not found'.format(fname))
    except UnicodeError:
        pass
    return loglist

def output(error_dict):
    """
    Make a string for output for one log file
    """
    out_string = 'Total errors in this directory: \n\n'
    if len(error_dict) == 0:
        out_string += 'No errors found\n'
    else:
        sort_keys = sorted(error_dict, key = error_dict.get, reverse = True)
        for k in sort_keys:
            out_string += '{} - {}'.format(errlist[k], k)
            out_string += '\n'
                
    return out_string

if __name__ == '__main__':
    
    KEYWORD = 'Error'

    files = get_list_of_logs()
    errlist = {}
    for logfile in files:
        log_list = file_to_list(logfile)
        collect_errors(log_list, KEYWORD, errlist)
    OUT_FILENAME = time.strftime("total_errors_%Y-%m-%d_%H-%M.txt", time.localtime())
    total_output = output(errlist)
    f = open(OUT_FILENAME, 'w')
    f.write(output(errlist))
    f.close()
    
