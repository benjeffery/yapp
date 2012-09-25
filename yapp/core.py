import errno
import subprocess
import fnmatch
import os
import yaml
import os.path as path
import yapp
import logging

def makeDir(path):
    """
    Make a dir but ignore if it exists.
    """
    try:
        os.mkdir(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

class YappProcessor:
    def __init__(self,root_dir, verbosity=logging.ERROR):
        self.root_dir = root_dir
        self.verbosity = verbosity
        self.log = logging.getLogger("Yapp")
        self.log.setLevel(verbosity)
        ch = logging.StreamHandler()
        ch.setLevel(verbosity)
        #formatter = logging.Formatter('%(levelname)s - %(message)s')
        #ch.setFormatter(formatter)
        self.log.addHandler(ch)

    def process(self):
        """
        Process the dir
        """
        yapp_files = [path.join(root, file) for (root, dirs, files) in os.walk(self.root_dir) for file in files if file[-len(yapp.CONFIG_EXTENSION):] == yapp.CONFIG_EXTENSION]
        if len(yapp_files) == 0:
            self.log.warn("No config (*{ext}) files found".format(ext=yapp.CONFIG_EXTENSION))
        for yapp_file in yapp_files:
            if self.verbosity:
                self.log.info("Processing {file}".format(file=yapp_file))
            self.process_config(yapp_file)

    def process_config(self, yapp_file):
        """
        Process a single yapp file
        """
        #noinspection PyBroadException
        try:
            with open(yapp_file,'r') as file:
                config = yaml.load(file)
        except:
            self.log.exception("\tError loading config from {file}".format(file=yapp_file))
            return

        #Find all the input matching files
        dir = path.dirname(yapp_file)
        files = [path.join(dir,file) for file in os.listdir(dir) if fnmatch.fnmatch(file, config['input_file_pattern'])]
        self.log.info("\tFound {num} files".format(num=len(files)))
        outdir = yapp_file[:-len(yapp.CONFIG_EXTENSION)]
        #Make the output dir
        makeDir(outdir)

        for file in files:
            outfile = path.join(outdir, path.basename(file))
            #Check if an old outfile exists and check if it needs to be updated
            if path.exists(outfile) and path.getmtime(outfile) > path.getmtime(file):
                self.log.info("\t\t{file} already has up-to-date output".format(file=file))
                continue
            tempfile = outfile+'.working'
            errfile = outfile+'.err'
            self.log.info("\t\t{file} processing....".format(file=file))
            with open(tempfile, 'w') as tempfile_f, open(errfile, 'w') as errfile_f:
                command = config['command'].format(input_file=file)
                ret_code = subprocess.Popen(command, bufsize=-1, stdout=tempfile_f, stderr=errfile_f, cwd=outdir, shell=True,).wait()
            #Delete the errfile if empty
            if ret_code == 0:
                self.log.info("\t\t{file} success".format(file=file))
                os.rename(tempfile, outfile)
                if path.getsize(errfile) == 0:
                    os.remove(errfile)
            else:
                self.log.warn("\t\t{file} failed with code: {code}".format(file=file, code=ret_code))
