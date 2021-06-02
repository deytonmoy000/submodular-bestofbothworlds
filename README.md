### submodular_PGB ###
*submodular_PGB* is a python library of **high-performance MPI-parallelized implementation of state-of-the-art algorithm Parellel Greedy Boost for submodular maximization**. 



### Prerequisites for replicating our Experiments: ###

**!NOTE!** You will need to download the data (matrix) files **"images_10K_mat.csv"** ([download](https://adminmyfsu-my.sharepoint.com/:x:/g/personal/td18d_my_fsu_edu/EevKBMPIU-dCo30rMrxxt_oBWKi9r74ROgjMEwqyzbgS3A?e=QkfUR0)) and **"tweets_keyword_mat.csv"** ([download]((https://adminmyfsu-my.sharepoint.com/:t:/g/personal/td18d_my_fsu_edu/Ebsak2kz8m5IoGPJkoGLYeYBvkkE8Uqf11aYECSl0aEpmw?e=xjeJmR)) and place it in the *"submodular/data"*  directory. 

**!NOTE!** To run the **FAST** *(Breuer, Balkanski, and Singer, ICML 2020)* algorithms using the evaluation scripts you will need to do the following:
  - Download the source code from *https://www.dropbox.com/sh/6alt6sg1f6jf2d0/AABhNpI0AIF0_q8yvGecg95oa?dl=0*
  - Update the variable **FAST_src_path** with the **full system path** (not relative path) to the *"SubmodularData/submodular/src"* (FAST source code) directory in **ExpSet1.py** and **ExpSet2.py**. 
  
      For  Eg. **FAST_src_path =  "/home/tonmoy/SubmodularData/submodular/src"**




### Replicating our Experiments: ###

Our experiments can be replicated by running the following scripts:


 **To replicate Experiments set 1:**
   - bash *bash_scripts/runExp1.bash*    

 **To replicate Experiments set 2:**
   - bash *bash_scripts/runExp2.bash*

 **To obtain the results illustrated in Table 2**
   - Generate the result for **Experiments set 1**
   - bash *bash_scripts/run_perf.bash*




**!NOTE!** Results data will be automatically saved as CSV files in the **experiment_results_output_data** directory and the plots will be automatically saved as PDF files in the **plots** directory.




### State-of-the-art Submodular Maximization Algorithms: ###

<!-- ### Submodular Maximization Algorithms from "Best of Both Worlds: Practical and Theoretically Optimal Submodular Maximization in Parallel": ### -->

**PGB** (NeurIPS 2021 (submitted)).
  - **LinearSeq()** -- runs the preprocessing algorithm *LINEARSEQ* for SMCC (Algorithm 1) 
  - **parallel_threshold_sample()** -- runs the algorithm Parallelizable Greedy Algorithm *THRESHOLDSEQ* for Fixed Threshold 'tau' (Algorithm 3)
  - **ParallelGreedyBoost()** -- runs *PARALLELGREEDYBOOST*  to Boost to the Optimal Ratio (Algorithm 4)

<!-- ### Submodular Maximization Algorithms from "The Fast Algorithm for Submodular Maximization": ### -->

**FAST** (Breuer, Balkanski, and Singer, ICML 2020).
  - **FAST_knowopt()** -- runs FAST (non-parallel) for a single guess of the optimal solution value (OPT)
  - **FAST_guessopt()** -- runs FAST (non-parallel) when the optimal solution value (OPT) is unknown
  - **FAST_knowopt_parallel()** -- runs FAST in parallel for a single guess of the optimal solution value (OPT)
  - **FAST_guessopt_parallel()** -- runs FAST in parallel when the optimal solution value (OPT) is unknown


### Objective functions: ###
We include the following canonical submodular objective functions:
- **Image Summarization;** 
- **Influence Maximization;**
- **Network Max Cover;**
- **Revenue Maximization on YouTube;**
- **Traffic Sensor Placement.**
- **Twitter Feed Summarization**




