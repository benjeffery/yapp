import errno
import subprocess
import fnmatch
import os
import yaml
import os.path as path
import yapp


def makeDir(path):
    """
    Make a dir but ignore if it exists.
    """
    try:
        os.mkdir(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def processDir(root_dir):
    yapp_files = [path.join(root, file) for (root, dirs, files) in os.walk(root_dir) for file in files if file[-len(yapp.CONFIG_EXTENSION):] == yapp.CONFIG_EXTENSION]
    for yapp_file in yapp_files:
        process(yapp_file)

def process(yapp_file):
    """
    Process a single yapp file
    """
    with open(yapp_file,'r') as file:
        config = yaml.load(file)

    #Find all the input matching files
    dir = path.dirname(yapp_file)
    files = [path.join(dir,file) for file in os.listdir(dir) if fnmatch.fnmatch(file, config['input_file_pattern'])]

    outdir = yapp_file[:-len(yapp.CONFIG_EXTENSION)]
    #Make the output dir
    makeDir(outdir)

    for file in files:
        outfile = path.join(outdir, path.basename(file))
        tempfile = outfile+'.working'
        errfile = outfile+'.err'
        with open(tempfile, 'w') as tempfile_f, open(errfile, 'w') as errfile_f:
            command = config['command'].format(input_file=file)
            ret_code = subprocess.Popen(command, bufsize=-1, stdout=tempfile_f, stderr=errfile_f, shell=True).wait()
            #Delete the errfile if empty
        if path.getsize(errfile) == 0 and ret_code == 0:
            os.remove(errfile)
        if ret_code == 0:
            os.rename(tempfile, outfile)
