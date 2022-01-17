# v.1.2. Time of error will be added if number of errors less than limit
# Supports old and new time formats, can detect incorrect time format
# v.1.3 Files open exceptions are added
# v.1.4 File encoding are added (utf-8)
# v.1.5 Processing of 'log.txt' are added. Some comments are expanded.
# Optional keywords for output
# v.1.6 File list are sorted before return.
# Keywords are added to filename if parameter '-s' is used
import sys
import time
import os
import argparse

version = '1.6'
LIMIT_OF_ERRORS = 10 # will show times of errors if number of errors less than value
#Eltherm_keywords = ['Atomizer', 'Sampler', 'Monochromator', 'Lamps', 'ADC']

def get_list_of_logs():
    """
    Create list of log files in current folder
    """
    list_of_files = os.listdir()
    list_of_logs = [f for f in list_of_files if f.endswith('.log') or f == 'log.txt']
    list_of_logs.sort()
    return list_of_logs

def split_error_string(s, keyword):
    """
    Split string using keyword as delimiter
    """
    a = s.split(keyword)
    if len(a) > 2: # if keyword present in error description
        a[1] = keyword.join(a[1:])
    return a[0].rstrip(), a[1].lstrip().rstrip()

def collect_errors(loglist, keyword, keywords_list):
    """
    Create dictionary of unique errors in loglist
    {'error': [[list of datetimes], number_of_errors]}
    """
    dictname = {}
    for e in loglist:
        if e.find(keyword) >=0:
            datetime, error_text = split_error_string(e, keyword)
            if keywords_list and any([x for x in keywords_list if x.lower() in error_text.lower()]):
                if dictname.get(error_text):
                    dictname[error_text][1] += 1
                    dictname[error_text][0].append(datetime)
                else:
                    dictname[error_text] = [[], 1]
                    dictname[error_text][0].append(datetime)
            if not keywords_list:
                if dictname.get(error_text):
                    dictname[error_text][1] += 1
                    dictname[error_text][0].append(datetime)
                else:
                    dictname[error_text] = [[], 1]
                    dictname[error_text][0].append(datetime)
    return dictname

def file_to_list(fname):
    """
    Read text file, create list of strings
    """
    loglist = []
    try:
        with open(fname, encoding='utf-8') as f:
            for e in f:
                loglist.append(e)
    except IOError: 
        print('Log file {} not found'.format(fname))
    except UnicodeError:
        pass
    return loglist

def output(error_dict, FILENAME, keywords_list):
    """
    Make a string for output for one log file
    """
    out_string = ''    
    if len(error_dict) == 0 and not keywords_list:
        out_string = 'Results for file {}: \n'.format(FILENAME)
        out_string += 'No errors found\n'
    if len(error_dict) > 0:
        out_string = 'Results for file {}: \n'.format(FILENAME)
        for k in error_dict.keys():
            out_string += '{} - {}'.format(errlist[k][1], k)
            if len(error_dict[k][0]) < LIMIT_OF_ERRORS:
                time_list = []
                for e in error_dict[k][0]:
                    try:
                        time_list.append(time.strftime("%H:%M:%S", time.strptime(e[1:-1])))
                    except: 
                        try:
                            time_list.append(time.strftime("%H:%M:%S", time.strptime(e[1:-1], '%m/%d/%y %H:%M:%S')))
                        except:
                            print("Data format error: ", e)

                out_string += ' (' + ', '.join(time_list) + ')\n'
            else:
                out_string += '\n'
                
    return out_string

if __name__ == '__main__':
    # Command line parser block
    parser = argparse.ArgumentParser(description = f"Error collector for MGA-1000 log files, v. {version}")
    parser.add_argument('files', nargs = "*",
                        help = "Log file name(s) or use -a option")
    parser.add_argument('-a', '--all', action = 'store_true', 
                        help = 'Check all log files in current folder')
    parser.add_argument('-s', '--save', action = 'store_true',
                        help = 'Save results to file. File name will be automatically generated')
    parser.add_argument('-k', '--keywords', nargs = '*', action = 'store',
                        help = 'Save results with keywords only. Several keywords can be used')
    #
    KEYWORD = 'Error'
    
    args = parser.parse_args()
    if args.files or args.all:
        if args.files and args.all:
            args.all = False
        if args.all:
            args.files = get_list_of_logs()
        total_output = []
        for logfile in args.files:
            log_list = file_to_list(logfile)
            errlist = collect_errors(log_list, KEYWORD, args.keywords)
            total_output.append(output(errlist, logfile, args.keywords))
        if args.save:
            OUT_FILENAME = time.strftime("errors_%Y-%m-%d_%H-%M.txt", time.localtime())
            if args.keywords:
                keywords = '_'.join(args.keywords)
                OUT_FILENAME = OUT_FILENAME[:-4] + '_' + keywords + '.txt'
            f = open(OUT_FILENAME, 'w')
            for e in total_output:
                if e:
                    f.write(e + '\n')
            f.close()
        else:
            for e in total_output:
                print(e + '\n')
    else:
        parser.print_help()
    
