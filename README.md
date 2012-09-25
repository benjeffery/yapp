#YAPP - YAPP Ain't a Pre-Processor

**YAPP** is a small tool for running commands over sets of files

## Usage

    yapp [-h] [--verbose] root_directory

YAPP will find all *.yapp.yaml files under the root_directory and process them in turn.

## Config
Each config({name}.yapp.yaml) currently needs to contain two lines:



    input_file_pattern: '*.jpg'                                   #A file pattern in the usual unix glob style
    command: 'convert {input_file} -resize 50% {input_file}.png'  #A command to be run 

For each {name}.yapp.yaml
YAPP will create an output directory called {name}
It will then run the command for all matching files in the same directory as the config, substituting in the file name where {input_file} occurs, using the output directory as the working directory for the command.

While the command is running stdout is saved to {input\_file}.working and stderr to {input\_file}.err. If the exit code of the command is 0 then {input\_file}.working is moved to {input\_file} and {input_file}.err deleted if empty.

If {input_file} already exists in the output directory with an mtime more recent than the input file then the command is skipped. "Touch"ing the input file will cause the mtime to change.

##FAQ
####Can't you just do this with xargs?
Yes