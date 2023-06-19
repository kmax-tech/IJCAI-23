#!/bin/bash

# sleep 10 seconds, so user can log out
sleep 10

# activate virtual environment
source home/ANON/BipolarCalc2023/BipolarCalcEnv/bin/activate
python3  home/ANON/BipolarCalc2023/BipolarADFTimeMeasure.py | tee BipolarCalcReport.txt
