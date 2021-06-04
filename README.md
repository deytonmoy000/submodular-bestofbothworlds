### submodular-BestOfBothWorlds ###
*submodular-BestOfBothWorlds* is a python library of high-performance MPI-parallelized implementation of state-of-the-art algorithm **LS+PGB** for submodular maximization described in the paper ***"Best of Both Worlds: Practical and Theoretically Optimal Submodular Maximization in Parallel"***. 



### Prerequisites for replicating our Experiments: ###
Please ensure the following steps are completed before running the experiments:

- Install **OpenMPI** using the command *apt install libopenmpi-dev* (for Ubuntu)

- Install **pandas**

- Install **mpi4py** 

- Install **scipy**

- Install **networkx**

- You will need to download the data (matrix) files **"images_10K_mat.csv"** ([download](https://drive.google.com/file/d/1L5EkO2XZc14malxAVJbtX9DaNYfT4ofK/view?usp=sharing)) and **"tweets_keyword_edgelist.txt"** ([download](https://drive.google.com/file/d/1fCLX_lQko87Ym1T_KgBEs5_0KUPHoutI/view?usp=sharing)) and place it in the *"submodular/data"*  directory. 

- If you would like to run the **FAST** *(Breuer, Balkanski, and Singer, ICML 2020)* algorithms using the evaluation scripts you will need to do the following:
    - Request the source code from *https://www.adambreuer.com/code*
    - Update the variable **FAST_src_path** with the **full system path** (not relative path) to the *"SubmodularData/submodular/src"* (FAST source code) directory in **ExpSet1.py** and **ExpSet2.py**. 
  
        For  Eg. **FAST_src_path =  "/home/user/SubmodularData/submodular/src"**

    - **!NOTE!** If you do not have the **FAST** *(Breuer, Balkanski, and Singer, ICML 2020)*  source code, the evaluation scripts will **only** run the algorithm **LS+PGB**.



### Replicating our Experiments: ###

Our experiments can be replicated by running the following scripts:


 **To replicate Experiments set 1:** (Figure 2, 3, 4)
   - bash *./bash_scripts/run_ExpSet1.bash ExpSet1.py "**nThreads**"*
   - **!NOTE!** Replace **nThreads** by the number of threads you would like the experiments to use    

 **To replicate Experiments set 2:** (Figure 5)
   - bash *./bash_scripts/run_ExpSet2.bash ExpSet2.py*
   - **!NOTE!** The script requires upto 64 threads to run. If you would like to change that, please update the line **declare -a nT=(1 2 4 8 16 32 64)** in *bash_scripts/run_ExpSet2.bash*
 
 **To obtain the results illustrated in Table 2**
   - Generate the result for **Experiments set 1**
   - bash *bash_scripts/run_perf.bash*


**!NOTE!** Results data will be automatically saved as CSV files in the **experiment_results_output_data** directory and the plots will be automatically saved as PDF files in the **plots** directory.




### Implemented Procedures: ###

<!-- ### Submodular Maximization Algorithms from "Best of Both Worlds: Practical and Theoretically Optimal Submodular Maximization in Parallel": ### -->

**LS+PGB**.
  - **LinearSeq()** [**LS**] -- runs the algorithm *LINEARSEQ* for SMCC (Algorithm 1). The procedure implements the optimizations described in *Section G*.
  - **parallel_threshold_sample()** [TS] -- runs the algorithm Parallelizable Greedy Algorithm *THRESHOLDSEQ* for Fixed Threshold 'tau' (Algorithm 3)
  - **ParallelGreedyBoost()** [**LS+PGB**] -- runs *PARALLELGREEDYBOOST*  to Boost to the Optimal Ratio (Algorithm 4) using the *alpha* and *gamma* obtained by running *LinearSeq()*

**!NOTE!** All the procedures are implemented in ***src/submodular_PGB.py***


<!-- ### Submodular Maximization Algorithms from "The Fast Algorithm for Submodular Maximization": ### -->

<!-- **FAST** (Breuer, Balkanski, and Singer, ICML 2020).
  - **FAST_knowopt()** -- runs FAST (non-parallel) for a single guess of the optimal solution value (OPT)
  - **FAST_guessopt()** -- runs FAST (non-parallel) when the optimal solution value (OPT) is unknown
  - **FAST_knowopt_parallel()** -- runs FAST in parallel for a single guess of the optimal solution value (OPT)
  - **FAST_guessopt_parallel()** -- runs FAST in parallel when the optimal solution value (OPT) is unknown -->


### Objective functions: ###
We include the following canonical submodular objective functions:
- **Image Summarization;** 
- **Influence Maximization;**
- **Network Max Cover;**
- **Revenue Maximization on YouTube;**
- **Traffic Sensor Placement.**
- **Twitter Feed Summarization**




