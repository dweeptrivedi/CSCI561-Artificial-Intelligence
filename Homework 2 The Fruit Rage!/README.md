Description:

homework11.cpp: 
implementation of minimax algorithm with alpha-beta pruning and optimizations for minimax algorithm. 

calibrate.cpp: 
This file is used to measure how many node/second can be searched in minimax algorithm given a N x N matrix.

The file takes following 5 samples for each N x N matrix:
1.	N x N matrix with no. of islands = 1
2.	N x N matrix with no. of islands = N/2
3.	N x N matrix with no. of islands = N*N
4.	N x N matrix with no. of islands = random (each location is generated randomly)
5.	N x N matrix with no. of islands = random (maximum value of a location in matrix is generated randomly and each location is generated randomly limited by maximum value)

The file will store corresponding values for each sample in calibration.txt, which will be used by homework11.cpp to construct graph of (no. of islands vs no. of nodes) and estimate maximum depth of search tree for selecting best move for given game board.

If calibration.txt is not present then Agent will pick maximum depth of search tree=3 or 4 depending upon matrix size.
