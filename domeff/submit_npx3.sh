#!/bin/sh

# Creating three empty arrays for arguments 
# used in the submission script
declare -a args
declare -a run_args
declare -a opt_args

# Flling the args array with the arguements used
# in the submission script
for val in "$@"; do
    args+=( "$val" )
done

# This breaks the args array into two arrays
# run_args, which has all the arguments necessary
# for the script to run; and opt_args, which 
# contains all the options needed for the job to
# be properly submitted to npx
nswitch=true
for i in "${!args[@]}"; do
    if [ "$nswitch" == true ]; then 
        if [ "${args[i]}" == '--BREAK' ]; then
            nswitch=false
        fi
    else
        i_minus_2=$((i - 2))
        for j in $(seq $i 1 "${#args[@]}"); do
            run_args+=( "${args[j]}" )
        done
        for j in $(seq 0 1 $i_minus_2); do
            opt_args+=( "${args[j]}" )
        done
        break
    fi
done

# This parses through the options in opt_args and
# sets the varaibles assosiated with the options
for i in "${!opt_args[@]}"; do
    Type=null
    if [ $i -lt "${#opt_args[@]}" ]; then
        if [[ "${opt_args[i]}"  =~ ^[+-]?[0-9]+$ ]]; then
            Type='int'
        elif [[ "${opt_args[i]}" =~ ^[+-]?[0-9]+\.$ ]]; then
            Type='str'
            if [[ "${opt_args[i]}" =~ ^- ]]; then
                Type='opt'
            fi
        elif [[ "${opt_args[i]}" =~ ^[+-]?[0-9]+\.?[0-9]*$ ]]; then
            Type='float'
        else
            Type='str'
            if [[ "${opt_args[i]}" =~ ^- ]]; then
                Type='opt'
            fi
        fi
        if [ $Type == 'opt' ]; then
            i_plus_1=$((i + 1))
            if [ "${opt_args[i]}" == '--meta' ]; then
                case "${opt_args[i_plus_1]}" in
                    
                    "old" | "new" | "ice")
                    META="${opt_args[i_plus_1]}" ;;

                    *)
                    echo -e "Error: Submission terminated. Please provide a variable environment option. Valid options are old, new, and ice.\n"
                    kill -HUP $$ ;;

                esac 
            elif [ "${opt_args[i]}" == '--gpu' ]; then
                if [[ "${opt_args[i_plus_1]}"  =~ ^[+-]?[0-9]+$ ]]; then
                    GPU="${opt_args[i_plus_1]}"
                else
                    echo -e "Error: Submission terminated. Make sure your GPU request is given as an integer.\n"
                    kill -HUP $$
                fi
            elif [ "${opt_args[i]}" == '--cpu' ]; then
                if [[ "${opt_args[i_plus_1]}"  =~ ^[+-]?[0-9]+$ ]]; then
                    CPU="${opt_args[i_plus_1]}"
                else
                    echo -e "Error: Submission terminated. Make sure your CPU request is given as an integer.\n"
                    kill -HUP $$
                fi
            elif [ "${opt_args[i]}" == '--mem' ]; then
                req="${opt_args[i_plus_1]}"
                case ${req: -2} in
                    
                    "GB" | "MB")
                        len=$((${#req} - 2))
                        size=${req:0:$len}
                        if [[ $size  =~ ^[+-]?[0-9]+$ ]] || [[ $size =~ ^[+-]?[0-9]+\.?[0-9]*$ ]]; then
                            MEM="${opt_args[i_plus_1]}"
                        else
                            echo -e "Error: Submission terminated. Make sure your memory size is given as a float or integer.\n"
                            kill -HUP $$
                        fi ;;

                    *)
                      echo -e "Error: Submission terminated. Make sure your memory type is either given as MB or GB.\n"
                      kill -HUP $$ ;;

                esac                                   
            fi  
        fi
    fi
done

# Creating output directory for log files
if [[ -f /scratch/dgillcrist ]]; then
    rm /scratch/dgillcrist
elif [[ ! -d "/scratch/dgillcrist/" ]]; then
    mkdir /scratch/dgillcrist/
fi
mkdir -p npx3-execs /scratch/dgillcrist/npx3-logs npx3-out npx3-error

# Creating execution script, do not delete until job has started!
echo "#!/bin/bash" > npx3-execs/npx3-$$.sh
echo "date" >> npx3-execs/npx3-$$.sh
echo "hostname" >> npx3-execs/npx3-$$.sh
echo "cd `pwd`" >> npx3-execs/npx3-$$.sh

#Set up new tools
if [ $META == 'old' ]; then
    echo "eval `/cvmfs/icecube.opensciencegrid.org/py2-v3.1.1/setup.sh`" >> npx3-execs/npx3-$$.sh
elif [ $META == 'new' ]; then
    echo "eval `/cvmfs/icecube.opensciencegrid.org/py3-v4.1.0/setup.sh`" >> npx3-execs/npx3-$$.sh
elif [ $META == 'ice' ]; then
     echo "eval `/cvmfs/icecube.opensciencegrid.org/iceprod/master/setup.sh`" >> npx3-execs/npx3-$$.sh
fi
echo "${run_args[@]}" >> npx3-execs/npx3-$$.sh
echo "date" >> npx3-execs/npx3-$$.sh

chmod +x npx3-execs/npx3-$$.sh

# Creating condor submission script (ClassAd)
echo "Universe  = vanilla" > 2sub.sub
echo "Executable = npx3-execs/npx3-$$.sh" >> 2sub.sub
echo "Log = /scratch/dgillcrist/npx3-logs/npx3-$$.log" >> 2sub.sub
echo "Output = npx3-out/npx3-$$.out" >> 2sub.sub
echo "Error = npx3-error/npx3-$$.error" >> 2sub.sub
if [ -z $MEM ]; then
    echo "No memory was specified. A default allocation of 3 GB was assigned"
    echo "Request_memory = 3 GB" >> 2sub.sub
else
    size=${MEM:0:$len}
    scale=${MEM: -2}
    echo "Request_memory = $size $scale" >> 2sub.sub
fi
if [ -z $GPU ]; then
     echo "No GPU amount was specified. By default zero GPUs will be used for this job"
else
    echo "Request_gpus = $GPU" >> 2sub.sub
fi
if [ -z $CPU ]; then
     echo "No CPU amount was specified. By default 1 CPU will be used for this job"
else
    echo "Request_cpus = $CPU" >> 2sub.sub
fi
echo "Notification = NEVER" >> 2sub.sub 
echo "Queue" >> 2sub.sub
condor_submit 2sub.sub

# A simple sh script for submitting one job to the npx3 cluster.
# Simply log into npx3.icecube.wisc.edu, run any command as you normally 
#  would but prepend "./submit-npx3.sh" and the command will be run on the
#  npx3 cluster.
#
# Eg #1:
# ./submit-npx3.sh root -l -b -q macro.C
# (NB: You must run in batch mode "-b" and quit root when macro is done "-q")
#
# Eg #2:
# ./submit-npx3.sh ./env-shell.sh python icetray_job.py
# (NB: You must execute env shell when submitting icetray jobs)
#
# This script will create directories to store your execution script, log files,
#  errors, and std output, so you need write permission in the local directory.

# This script creates a script to be executed and another script to submit it.
# The execution script must be available *at time of job execution!*, which may
#  not be until much later and so it's stored in a directory 'npx3-execs'.
# You may occasionally want to 'rm -rf npx3-*' directories if they get big.
# The submission script "2sub.sub" can be discarded immediately.

# This method of passing your job into a bash script as arguments may fail
#  if you have quotes or other special characters

#Quickest ever Condor tutorial:
#"condor_q" gives list of jobs running
#"condor_q $USER" gives list of your jobs
#"condor_rm $USER" removes your jobs 
# Creating output directories
