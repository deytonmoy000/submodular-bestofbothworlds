"""
@author: Adam Breuer
"""

import numpy as np
from datetime import datetime
import pandas as pd
from scipy import sparse
import networkx as nx
import random

from mpi4py import MPI

# # Load the Objective function classes 
from objectives import  NetCover,\
                        NetCoverSparse,\
                        TrafficCoverDirWeighted,\
                        RevenueMaxOnNet,\
                        MovieRecommenderMonotoneCover,\
                        InfluenceMax,\
                        GraphGenerators

# Load our optimization algorithms and helper functions
from src import submodular

FAST_src_path = "/home/tonmoy/SubmodularData/submodular/src"
# FAST_src_path = ""

# Load our optimization algorithms and helper functions
from src import submodular_PGB
if (FAST_src_path!=""):
    sys.path.append(FAST_src_path)
    import submodular




def run_adaptive_experiments(objective, k_vals_vec, filepath_string, experiment_string, comm, rank, size, p_root=0, trials=5):
    """ Parallel MPI function to run all benchmark algorithms over all values of k 
    for a given objective function and save CSV files of data and runtimes """

    # Initialize data for saving csv files
    size_groundset = len([ele for ele in objective.groundset])

    comm.barrier()
    algostring = 'EXMAX'

    if rank == 0:
        print('Beginning ', algostring, 'for experiment: ', experiment_string)
    eps = 0.1
    d = 0.05

    m_reducedmean = 95

    val_vec = []
    queries_vec = []
    time_vec = []

    # Save data progressively. 
    for ii, kk in enumerate(k_vals_vec):

        for trial in range(trials):
            comm.barrier()

            # Free memory between trials
            sol = []

            # Run the algorithm
            val, queries, time, sol = submodular.exhaustivemax_parallel( objective, \
                                                                        kk, \
                                                                        eps, \
                                                                        d, \
                                                                        comm, \
                                                                        rank, \
                                                                        size, \
                                                                        p_root=0, \
                                                                        randseed=trial, \
                                                                        m_reducedmean=m_reducedmean)
            if rank == p_root:
                val_vec.append(val)
                queries_vec.append(queries)
                time_vec.append(time)

                ## Save data progressively
                print(len(val_vec), len(np.concatenate([np.repeat(range(trials), ii), range(1, (trial+1))])))
                dataset = pd.DataFrame({'f_of_S':  val_vec, \
                                        'Queries': queries_vec, \
                                        'Time':    time_vec, \
                                        'k':       np.concatenate([np.repeat(k_vals_vec[:ii], trials), [kk]*(trial+1)]), \
                                        'n':       [size_groundset]*(ii*trials+trial+1), \
                                        'nproc':   [size]*(ii*trials+trial+1), \
                                        'trial':   np.concatenate([np.tile(range(1,(trials+1)), ii), range(1, (trial+2))])
                                        })
                dataset.to_csv(path_or_buf = filepath_string + experiment_string +'_'+ algostring +".csv", index=False)


                print('f(S)=', val, 'queries=', queries, 'time=', time, algostring, 'k=', kk)
    print('\n')
    comm.barrier()



    # comm.barrier()
    # algostring = 'BINSEARCHMAX'

    # if rank == 0:
    #     print('Beginning ', algostring, 'for experiment: ', experiment_string)
    # eps = 0.1
    # d = 0.05

    # m_reducedmean = 95

    # val_vec = []
    # queries_vec = []
    # time_vec = []

    # # Save data progressively. 
    # for ii, kk in enumerate(k_vals_vec):

    #     for trial in range(trials):
    #         comm.barrier()

    #         # Free memory between trials
    #         sol = []

    #         # Run the algorithm
    #         val, queries, time, sol = submodular.binsearchmax_parallel( objective, \
    #                                                                         kk, \
    #                                                                         eps, \
    #                                                                         d, \
    #                                                                         comm, \
    #                                                                         rank, \
    #                                                                         size, \
    #                                                                         p_root=0, \
    #                                                                         randseed=trial, \
    #                                                                         m_reducedmean=m_reducedmean)
    #         if rank == p_root:
    #             val_vec.append(val)
    #             queries_vec.append(queries)
    #             time_vec.append(time)

    #             ## Save data progressively
    #             #print(len(val_vec), len(np.concatenate([np.repeat(range(trials), ii), range(1, (trial+1))])))
    #             dataset = pd.DataFrame({'f_of_S':  val_vec, \
    #                                     'Queries': queries_vec, \
    #                                     'Time':    time_vec, \
    #                                     'k':       np.concatenate([np.repeat(k_vals_vec[:ii], trials), [kk]*(trial+1)]), \
    #                                     'n':       [size_groundset]*(ii*trials+trial+1), \
    #                                     'nproc':   [size]*(ii*trials+trial+1), \
    #                                     'trial':   np.concatenate([np.tile(range(1,(trials+1)), ii), range(1, (trial+2))])
    #                                     })
    #             dataset.to_csv(path_or_buf = filepath_string + experiment_string +'_'+ algostring +".csv", index=False)


    #         #print('f(S)=', val, 'queries=', queries, 'time=', time, algostring, 'k=', kk)
    # #print('\n')
    # comm.barrier()


    # ############################################################################################################################
    # ####  Also run each algorithm once given a no guess for OPT (sum of top k singletons) and save evolution over rounds  ####
    # ############################################################################################################################
    allvals = submodular.parallel_margvals_returnvals(objective, [], objective.groundset, comm, rank, size)
    val_sum_topk = np.sum( np.sort(allvals)[-kk:] )
    comm.barrier()

    algostring = 'BINSEARCHMAX'

    eps = 0.1
    d = 0.05
    m_reducedmean = 95
    # Free memory between trials
    sol = []
    sol_r = [] 
    time_r = []
    queries_r = []
    comm.barrier()
    val, queries, time, sol, sol_r, time_r, queries_r = submodular.binsearchmax1OPT_parallel( objective, \
                                                                    kk, \
                                                                    eps, \
                                                                    d, \
                                                                    comm, \
                                                                    rank, \
                                                                    size, \
                                                                    OPT=val_sum_topk, \
                                                                    p_root=0, \
                                                                    randseed=trial, \
                                                                    m_reducedmean=m_reducedmean)

    # Also save data the last trial, highest k value solution as it evolved over rounds:
    val_r = submodular.parallel_val_of_sets(objective, sol_r, comm, rank, size)
    if rank == p_root:
        dataset_rounds = pd.DataFrame({'f_of_S':  val_r, \
                                'Queries': queries_r, \
                                'Time':    time_r, \
                                'k':       [kk]*len(time_r), \
                                'n':       [size_groundset]*len(time_r), \
                                'nproc':   [size]*len(time_r)
                                })
        dataset_rounds.to_csv(path_or_buf = filepath_string + experiment_string +'_'+ algostring +"_ROUNDS.csv", index=False)



    ############################################################################################################################
    ####     Also run PGB algorithm       ####
    ############################################################################################################################
    algostring = 'PGB'
    OPT = None
    if rank == p_root:
        print('Beginning ', algostring, 'for experiment: ', experiment_string)
    eps = 0.1
    val_vec = []
    queries_vec = []
    time_vec = []

    for ii, kk in enumerate(k_vals_vec):

        for trial in range(trials):
            comm.barrier()

            # Free memory between trials
            sol = []
            sol_r = [] 
            time_r = []
            queries_r = []

            # Run the algorithm
            val, queries, time, sol, sol_r, time_r, queries_r = submodular_PGB.ParallelGreedyBoost(objective, kk, eps, comm, rank, size, p_root, seed=trial, stop_if_approx=False );
            time_PGB = time;
            val_PGB = val;
            
            if rank == p_root:
            
                print('f(S)=', val, 'queries=', queries, 'time=', time, algostring, experiment_string, 'with k=', kk)

                val_vec.append(val)
                queries_vec.append(queries)
                time_vec.append(time)

                ## Save data progressively
                dataset = pd.DataFrame({'f_of_S':  val_vec, \
                                        'Queries': queries_vec, \
                                        'Time':    time_vec, \
                                        'k':       np.concatenate([np.repeat(k_vals_vec[:ii], trials), [kk]*(trial+1)]), \
                                        'n':       [size_groundset]*(ii*trials+trial+1), \
                                        'nproc':   [size]*(ii*trials+trial+1), \
                                        'trial':   np.concatenate([np.tile(range(1,(trials+1)), ii), range(1, (trial+2))])
                                        })
                dataset.to_csv(path_or_buf = filepath_string + experiment_string +'_exp1_'+ algostring +".csv", index=False)


                print('f(S)=', val, 'queries=', queries, 'time=', time, algostring, 'k=', kk)
    print('\n')


    if rank == p_root:
        print('\nFINISHED\n')
    comm.barrier()

    return







if __name__ == '__main__':

    start_runtime = datetime.now()

    p_root = 0

    filepath_string = "experiment_results_output_data/"

    # Start MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    

    ################################################################
    ################################################################
    #############           REAL DATA            ###################
    ################################################################
    ################################################################



    # # #####################################################################
    # # ##          INFLUENCEMAX  CallTech FB NETWORK Example         #######
    # # #####################################################################
    if rank == p_root:
        print( 'Initializing FB CalTech Objective' )
    experiment_string = 'INFMAXCalTech'

    # Undirected Facebook Network. Format as an adjacency matrix
    filename_net = "data/socfb-Caltech36.csv"
    edgelist = pd.read_csv(filename_net)
    net_nx = nx.from_pandas_edgelist(edgelist, \
                                     source='source', \
                                     target='target', \
                                     edge_attr=None, \
                                     create_using=None)
    net_nx = net_nx.to_undirected()
    try:
        net_nx.remove_edges_from(net_nx.selfloop_edges())
    except:
        net_nx.remove_edges_from(nx.selfloop_edges(net_nx)) #Later version of networkx prefers this syntax


    #A = np.asarray( nx.adjacency_matrix(net_nx).todense() )
    if rank == p_root:
        print( 'Loaded data. Generating sparse adjacency matrix' )
    A = nx.to_scipy_sparse_matrix(net_nx, format='csr')
    A.setdiag(1)

    A = A.toarray().astype(np.bool)

    p = 0.01
    objective = InfluenceMax.InfluenceMax(A, p)
    if rank == p_root:
        print( 'FB CalTech Objective initialized. Beginning tests.' )
    
    k_vals_vec = [25, 50, 100, 150, 200, 250, 300]
    # k_vals_vec = [5]

    comm.barrier()
    run_adaptive_experiments(objective, k_vals_vec, filepath_string, experiment_string, comm, rank, size)
    



    # ##############################################################
    # ## DIRECTED EdgeCover ON CALI ROAD NETWORK EXPERIMENT ########
    # ##############################################################
    experiment_string = 'CAROAD'
    # Weighted Directed highway adjacency matrix
    filename = "data/Pems_Adj_thresh_10mi_522n.csv"

    A = pd.read_csv(filename).values

    # Generate our DIRECTED MaxCut class containing the function
    objective = TrafficCoverDirWeighted.TrafficCoverDirWeighted(A)

    k_vals_vec = [20, 40, 60, 80, 100, 120, 140, 160]
    # k_vals_vec = [5]

    # Print info and start the stopwatch
    if rank == p_root:
        print ('Starting California experiment. Network size = ', str(A.shape[0]), ' nodes.')
    comm.barrier()

    run_adaptive_experiments(objective, k_vals_vec, filepath_string, experiment_string, comm, rank, size)
    



    # ############################################################
    # ## YOUTUBE REVENUE MAXIMIZATION EXAMPLE ####################
    # ############################################################
    comm.barrier()
    if rank == p_root:
        print( 'Initializing Youtube Objective' )
    experiment_string = 'YOUTUBE50'

    edgelist = pd.read_csv('data/youtube_50rand_edgelist.csv', delimiter=',')
    # Edgelist to Adjacency Matrix
    A = edgelist.pivot(index = "source", columns = "target", values = "weight_draw")
    # Cast to Numpy Matrix
    #A = A.as_matrix()
    A = A.values
    # Missing edges are 0
    A[np.isnan(A)] = 0

    A[A>0] = A[A>0] + 1.0

    alpha = 0.9
    # Generate class containing our f(S)
    objective = RevenueMaxOnNet.RevenueMaxOnNet(A, alpha)
    if rank == p_root:
        print( 'YOUTUBE Objective initialized. Adjacency matrix shape is:', A.shape, ' Beginning tests.' )

    k_vals_vec = [20, 40, 60, 80, 100, 120, 140, 160, 180, 200]
    # k_vals_vec = [5]

    comm.barrier()
    run_adaptive_experiments(objective, k_vals_vec, filepath_string, experiment_string, comm, rank, size)




    # ################################################################
    # ###              Movie Recommendation Example                ###
    # ################################################################
    # Load the movie data and generate the image pairwise distance matrix Dist
    comm.barrier()
    experiment_string = 'MOVIECOVERsubset'

    num_random_movies_users = size_of_ground_set #-1 means 'all images'

    # Initialize the movie data
    movie_user_mat_fname = "data/Movie_ratings_mat.csv"
    movies_dat_fname = 'data/movies.dat'

    objective = None

    try:
        Sim = MovieRecommenderMonotoneCover.load_movie_user_matrix(movie_user_mat_fname)
        if rank != p_root:
            Sim = None # Free memory on all but root proc -- we just try to have them load to test whether the movie data exists

        if rank == p_root:
            genres_idx, genres_dict, genres_strings, movie_titles, movie_years = \
                MovieRecommenderMonotoneCover.load_movie_genres(movies_dat_fname)

            movierandstate = np.random.RandomState(1)

            if num_random_movies_users > 0:  
                movie_rows     = movierandstate.choice(Sim.shape[0], num_random_movies_users, replace=False)
                Sim            = Sim[movie_rows,:][:,movie_rows]
                genres_idx     = genres_idx[movie_rows]
                genres_strings = genres_strings[movie_rows]
                movie_titles   = movie_titles[movie_rows]

            print('loaded movie ratings matrix of shape', Sim.shape)

            # Generate our class containing the function
            genre_weight = 0.5 * np.max( np.sum(Sim, 1) )
            year_weight = 0.0# * np.max( np.sum(Sim, 1) ) 
            ratings_weight = 1.0
            cover_weight = 1.0
            good_movie_score = 4.5

            objective = MovieRecommenderMonotoneCover.MovieRecommenderMonotoneCover(Sim, \
                                                                            movie_titles, \
                                                                            genres_idx, \
                                                                            movie_years, \
                                                                            ratings_weight, \
                                                                            cover_weight, \
                                                                            genre_weight, \
                                                                            year_weight, \
                                                                            good_movie_score)

        # Root processor broadcasts the objective function to all processors
        objective = comm.bcast(objective, p_root)

        k_vals_vec = [25, 50, 75, 100, 125, 150, 175, 200]
        # k_vals_vec = [5]

        comm.barrier()

        run_adaptive_experiments(objective, k_vals_vec, filepath_string, experiment_string, comm, rank, size)


    except:
        if rank == 0:
            print('\nThe final experiment (movie recommendation) requires a large movies data file (too large for GitHub).\
                   Add this file to the /data/ folder to run this experiment.\n')


    # ##################################################################
    # ##################################################################
    # ######                 SYNTHETIC GRAPH DATA                 ######
    # ##################################################################
    # ##################################################################
    size_of_ground_set = 500

    # # ################################################################
    # # ## Boolean Undirected VertCover SBM Example ####################
    # # ################################################################
    comm.barrier()
    if rank == p_root:
        print( 'Initializing SBM Objective' )
    experiment_string = 'SBM'

    #Generate the SBM Adj. Matrix
    comm.barrier()
    objective_rootprocessor = None
    np.random.seed(42)

    # Root processor generates the random graph
    if rank == p_root:

        minSize = 25 # min cluster size
        maxSize = 100 # max cluster size
        numberC = int(np.ceil(np.float(size_of_ground_set) / np.mean((minSize, maxSize))))
        p = 0.01  # = prob of edge
        A = GraphGenerators.SBMSparseCSR(numberC, minSize, maxSize, p)
        A.setdiag(1)

        if A.shape[0] <= 1000:
            A = A.toarray()
            A.astype(np.bool)
            # Generate our NetCover class containing the function
            objective_rootprocessor = NetCover.NetCover(A)
        else:
            objective_rootprocessor = NetCoverSparse.NetCoverSparse(A)


    # Send the class to all processors
    if rank != 0:
        objective_rootprocessor = None
    objective = comm.bcast(objective_rootprocessor, root=0)
    print (len(objective.groundset), np.sum(objective.A), rank)
    ## For testing:
    if rank == p_root:
        print( 'SBM Objective initialized. Beginning tests.' )
        print ('size of ground set:', len(objective.groundset))

    comm.barrier()
    k_vals_vec = [10, 15, 20, 25, 30, 35, 40] 
    # k_vals_vec = [5]
    run_adaptive_experiments(objective, k_vals_vec, filepath_string, experiment_string, comm, rank, size)




    # # ################################################################
    # # ## Boolean Undirected VertCover ER Example #####################
    # # ################################################################
    k_vals_vec = [10, 15, 20, 25, 30, 35, 40] 
    # k_vals_vec = [5]

    comm.barrier()
    if rank == p_root:
        print( 'Initializing ER Objective' )
    experiment_string = 'ER'

    # Set the seed before generating random ER matrix 
    np.random.seed(42)

    objective_rootprocessor = None

    if rank == p_root:
        # Set p == prob of an edge in Erdos Renyi
        p = 0.01

        #Generate the ER Adj. Matrix. Use sparse matrix if A is big (matrix operations slower in sparse format)
        if size_of_ground_set <= 1000:
            A = GraphGenerators.ErdosRenyiSymBool(size_of_ground_set, p)
            np.fill_diagonal(A, 1)
            A.astype(np.bool)
            objective_rootprocessor = NetCover.NetCover(A)

        else:
            A = GraphGenerators.ErdosRenyiSymBoolSparseCSR(size_of_ground_set, p)
            A.setdiag(1)
            objective_rootprocessor = NetCoverSparse.NetCoverSparse(A)

    comm.barrier()

    # Send the class to all processors
    objective = comm.bcast(objective_rootprocessor, root=0)
    print ('n:', len(objective.groundset), 'sum(A):', np.sum(objective.A), 'Processor_rank:', rank)

    ## For testing:
    if rank == p_root:
        print( 'ER Objective initialized. Beginning tests.' )

    run_adaptive_experiments(objective, k_vals_vec, filepath_string, experiment_string, comm, rank, size)




    # #################################################################
    # ## Boolean Undirected Watts-Strogatz Example ####################
    # #################################################################
    # k_vals_vec = [20, 40, 60, 80, 100, 120, 140, 160, 180]
    k_vals_vec = [10, 15, 20, 25, 30, 35, 40] 

    # k_vals_vec = [5]

    comm.barrier()
    if rank == p_root:
        print( 'Initializing WS Objective' )
    experiment_string = 'WS'

    if rank == p_root:

        G = nx.watts_strogatz_graph(n=size_of_ground_set, k=2, p=0.1, seed=42)
        try:
            G.remove_edges_from(G.selfloop_edges())
        except:
            G.remove_edges_from(nx.selfloop_edges(G)) #Later version of networkx prefers this syntax

        if size_of_ground_set <= 1000:
            A = np.asarray( nx.to_numpy_matrix(G) )
            np.fill_diagonal(A, 1)
            A.astype(np.bool)
            print( 'size of A', A.shape[0])
            print( 'density of A', np.sum(A)/len(A)**2)
            # Generate our NetCover class containing the function
            objective_rootprocessor = NetCover.NetCover(A)

        else:
            A = nx.to_scipy_sparse_matrix(G, format='csr')
            A.setdiag(1)
            # Generate our NetCover class containing the function
            objective_rootprocessor = NetCoverSparse.NetCoverSparse(A)
        

    # Send class to all processors
    if rank != 0:
        objective_rootprocessor = None
    objective = comm.bcast(objective_rootprocessor, root=0)

    if rank == p_root:
        print( 'Watts-Strogatz Objective initialized. Beginning tests.' )
    comm.barrier()
    run_adaptive_experiments(objective, k_vals_vec, filepath_string, experiment_string, comm, rank, size)



    
    # ###############################################################
    # ## Boolean Undirected VertCover BA Example ####################
    # ###############################################################
    k_vals_vec = [10, 15, 20, 25, 30, 35, 40]
    # k_vals_vec = [5]

    comm.barrier()
    if rank == p_root:
        print( 'Initializing BA Objective' )
    experiment_string = 'BA'

    if rank == p_root:

        G = nx.barabasi_albert_graph(size_of_ground_set, 1, seed=1)
        try:
            G.remove_edges_from(G.selfloop_edges())
        except:
            G.remove_edges_from(nx.selfloop_edges(G)) #Later version of networkx prefers this syntax

        if size_of_ground_set <= 1000:
            A = np.asarray( nx.to_numpy_matrix(G) )
            np.fill_diagonal(A, 1)

            A.astype(np.bool)
            print( 'size of A', A.shape[0])
            print( 'density of A', np.sum(A)/len(A)**2)
            objective_rootprocessor = NetCover.NetCover(A)

        else:
            A = nx.to_scipy_sparse_matrix(G, format='csr')
            A.setdiag(1)
            objective_rootprocessor = NetCoverSparse.NetCoverSparse(A)

    # Send class to all processors
    if rank != 0:
        objective_rootprocessor = None
    objective = comm.bcast(objective_rootprocessor, root=0)

    if rank == p_root:
        print( 'BA Objective initialized. Beginning tests.' )
    comm.barrier()
    run_adaptive_experiments(objective, k_vals_vec, filepath_string, experiment_string, comm, rank, size)



    if rank == p_root:
        print ('\nALL EXPERIMENTS COMPLETE, total minutes elapsed =', \
            (datetime.now()-start_runtime).total_seconds()/60.0, '\n\n')




