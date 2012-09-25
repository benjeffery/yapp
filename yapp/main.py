import argparse
import logging
from yapp.core import YappProcessor


def commandLineInvocation():
    parser = argparse.ArgumentParser(description='Process files in a given directory')
    parser.add_argument('root_directory', action='store', help='directory to walk to find files to process')
    parser.add_argument('--verbose', '-v', default=False, action='store_true', help='Print details of files being processed')
    #parser.add_argument('--watch', '-w', default=False, action='store_true', help='Continuously watch the directory for new and changed files and process as needed')
    args = parser.parse_args()
    yp = YappProcessor(args.root_directory, verbosity=logging.INFO if args.verbose else logging.ERROR)
    yp.process()
