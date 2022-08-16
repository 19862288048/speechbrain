#!/bin/bash

# Script to test seed variability
# Example:
# ./run_experiments_seed_variability.sh hparams/EEGNet_BNCI2014001_seed_variability.yaml /localscratch/eeg_data results/EEGNet_BNCI2014001_seed_variability_moabb 9 2 1986 1 acc valid_metrics.pkl false true --number_of_epochs=2

hparams=$1
data_folder=$2 #MOABB data folder
output_folder=$3 #results folder
nsbj=$4
nsess=$5
nruns=$7
eval_metric=$8 #acc,loss,f1
metric_file=$9 # test_metrics.pkl or valid_metrics.pkl (use valid_metrics for hyperparameter tuning)
do_leave_one_subject_out=${10}
do_leave_one_session_out=${11}

to_download=true

if [ $6 = "random_seed" ]; then
    seed_init=$RANDOM
else
    seed_init=$6
fi

echo "hparams file : $hparams"
echo "Data folder: $data_folder"
echo "Output folder: $output_folder"
echo "No. of subjects: $nsbj"
echo "No. of sessions: $nsess"
echo "No. of runs: $nruns"

# Creating output folder
mkdir -p $output_folder\_seed\_$seed_init
mkdir -p $data_folder


seed=$seed_init

# RUN MULTIPLE EXPERIMENTS (with different seeds)
for i in $(seq 0 1 $(( nruns - 1 ))); do
  echo $seed
  
  # LEAVE-ONE-SUBJECT-OUT
  if [ "$do_leave_one_subject_out" = true ]
  then

      for target_subject_idx in $(seq 0 1 $(( nsbj - 1 ))); do
          echo "Subject $target_subject_idx"
          python train.py $hparams --seed=$seed --data_folder=$data_folder --output_folder=$output_folder\_seed\_$seed_init/$seed\
          --target_subject_idx=$target_subject_idx --target_session_idx=0 \
          --data_iterator_name='leave-one-subject-out' --to_download=$to_download --to_prepare=true "${@:12}"

         # Data already downloaded
         to_download=False 
      done
  fi
  
  # LEAVE-ONE-SESSION-OUT
  if [ "$do_leave_one_session_out" = true ]
  then

      # Loop over sessions
      for j in $(seq 0 1 $(( nsess - 1 ))); do
          for target_subject_idx in $(seq 0 1 $(( nsbj - 1 ))); do
              echo "Subject $target_subject_idx"
              python train.py $hparams --seed=$seed --data_folder=$data_folder --output_folder=$output_folder\_seed\_$seed_init/$seed\
              --target_subject_idx=$target_subject_idx --target_session_idx=$j \
              --data_iterator_name='leave-one-session-out' --to_download=$to_download --to_prepare=true "${@:12}"
      
              # Data already downloaded
              to_download=False
      done

  done
  fi

  # Store results
  python parse_results.py $output_folder\_seed\_$seed_init/$seed $metric_file $eval_metric | tee -a  $output_folder\_seed\_$seed_init/$seed\_results.txt
  
  # Changing random seed
  seed=$((seed+1))
  
done

# Aggregate results + notify them to Orion (if needed for hyperparameter tuning)
echo 'Final Results'
python aggregate_results.py $output_folder\_seed\_$seed_init $eval_metric | tee -a  $output_folder\_seed\_$seed_init/aggregated_performance.txt





