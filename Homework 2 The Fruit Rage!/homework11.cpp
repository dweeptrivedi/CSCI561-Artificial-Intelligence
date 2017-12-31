#include <iostream>
#include <functional>
#include <fstream>
#include <string>
#include <stdlib.h>
#include <sys/types.h>
#include <stdint.h>
#include <stdbool.h>
#include <string>
#include <string.h>
#include <map>
#include <vector>
#include <array>
#include <algorithm>
#include <assert.h>
#include <unistd.h>
#include <cmath>

using namespace std;

uint32_t maxDepth = 3;
uint64_t count1 = 0, prune = 0,  saved = 0, savedIlands = 0, leaves = 0, star = 0;
uint32_t n = 0;
uint32_t p = 0;
double t = 0;

uint32_t bestState[2]={0,0};
uint32_t bestSize=0;
uint32_t min_row,max_row,min_col,max_col;

hash<string> str_hash;
hash<string> score_hash;
map<size_t, vector <array<uint32_t,3>>> m1;
map<size_t, int64_t> m3;

bool goalState(string board) {
    uint32_t data = n*n;
    for (int i=0;i<data;i++){
        if (board[i]!='*')
            return false;
    }
    return true;
}

uint32_t exploreIland2(string &board, uint32_t row, uint32_t col, char fruit){
    uint32_t index = row*n+col;
    if (board[index] != fruit)
        return 0;

    board[index] = '*';
    if (col < n-1){
        max_col = (max_col>col+1)?max_col:col+1;
        exploreIland2(board, row, col+1, fruit);
    }
    if (col > 0){
        min_col = (min_col<col-1)?min_col:col-1;
        exploreIland2(board, row, col-1, fruit);
    }
    if (row < n-1){
        max_row = (max_row>row+1)?max_row:row+1;
        exploreIland2(board, row+1, col, fruit);
    }
    if (row > 0){
        min_row = (min_row<row-1)?min_row:row-1;
        exploreIland2(board, row-1, col, fruit);
    }

    return 0;
}

uint32_t exploreIland3(string &board, uint32_t row, uint32_t col, char fruit, uint32_t islanSize){
    uint32_t index = row*n+col;
    if (board[index] != fruit)
        return 0;

    board[index] = '*';
    uint32_t islandSize = 1;
    if (col < n-1){
        max_col = (max_col>col+1)?max_col:col+1;
        islandSize += exploreIland3(board, row, col+1, fruit, islandSize);
    }
    if (col > 0){
        min_col = (min_col<col-1)?min_col:col-1;
        islandSize += exploreIland3(board, row, col-1, fruit, islandSize);
    }
    if (row < n-1){
        max_row = (max_row>row+1)?max_row:row+1;
        islandSize += exploreIland3(board, row+1, col, fruit, islandSize);
    }
    if (row > 0){
        min_row = (min_row<row-1)?min_row:row-1;
        islandSize += exploreIland3(board, row-1, col, fruit, islandSize);
    }

    return islandSize;
}

void applyGravity(string &board){
    uint32_t Rmax = max_row+1;
    int32_t j, last, lastStar;
    for (int i=min_col;i<=max_col;i++){
        j = min_row;
        while (j<Rmax){
            while(j<Rmax && board[j*n+i]=='*')
                j++;
            while(j<Rmax && board[j*n+i]!='*')
                j++;
            if(j<Rmax){
                last = j-1;
                while(j<Rmax && board[j*n+i]=='*'){
                    lastStar = j;
                    j++;
                }
                while(last>=0){
                    board[lastStar*n+i] = board[last*n+i];
                    lastStar--;
                    last--;
                }
                while(lastStar>=0){
                    board[lastStar*n+i] = '*';
                    lastStar--;
                }
            }
        }
    }
    return;
}

bool sortFunc(array<uint32_t,3>&a, array<uint32_t,3>&b){
    return (a[0]>b[0]);
}

bool sortFunc2(array<double,3>&a, array<double,3>&b){
    return (a[1]>b[1]);
}

void
getChildren(string &board,vector <array<uint32_t,3>> &childIlands,uint32_t *childIlandsSize){
    uint32_t k =0;
    uint32_t index,size;
    size_t boardhash = str_hash(board);

    if(m1.find(boardhash)!=m1.end()){
        savedIlands++;
        childIlands = m1[boardhash];
        return;
    }

    string visited(board);
    for(uint32_t i=0;i<n;i++){
        for(uint32_t j=0;j<n;j++){
            index= i*n+j;
            if (visited[index]!='*'){
                size = exploreIland3(visited, i, j, visited[index], 0);
                array<uint32_t,3> island {size, i, j};
                childIlands.push_back(island);
                k++;
            }
        }
    }

    sort(childIlands.begin(),childIlands.begin()+k, sortFunc);
    //This will create a new copy at global level, change it to pointer reference if taking too much memory
    m1[boardhash] = childIlands;
    *childIlandsSize=k;
}

void
getChild(string &board, string &child, array <uint32_t,3>&childIland){
    uint32_t r = childIland[1];
    uint32_t c = childIland[2];

    min_row = r;
    max_row = r;
    min_col = c;
    max_col = c;
    exploreIland2(child, r, c, child[r*n+c]);
    applyGravity(child);

    return;
}


int64_t
playGame(string &board, bool player, uint64_t maximus, uint64_t minimus, uint32_t depth, int64_t alpha, int64_t beta){
    int64_t va, vb;
    int64_t temp;
    uint32_t childIlandIdx=0;
    int64_t score = maximus-minimus;
    count1++;

    if (goalState(board)){
        return 0;
    }

    if (player){va=-123456;}else{vb=123456;}
    bool gotit = false;
    size_t boardhash = score_hash(board+to_string(maxDepth-depth)+to_string(player)+to_string(alpha)+to_string(beta));
    if (depth < maxDepth && m3.find(boardhash)!=m3.end()){
        saved++;
        temp = m3[boardhash];
        return temp;
    }

    vector <array<uint32_t,3>>childIlands = vector<array<uint32_t,3>>();
    uint32_t childIlandsSize=0;

    getChildren(board,childIlands,&childIlandsSize);
    childIlandsSize = childIlands.size();

    for (int i=0;i<childIlandsSize;i++){
        score = maximus-minimus;
        string child(board);
        getChild(board, child, childIlands[i]);

        uint32_t squaredSize = childIlands[i][0]*childIlands[i][0];
        (player)?maximus+=squaredSize:minimus+=squaredSize;
        if(depth+1<=maxDepth) {
            temp = playGame(child,!player, maximus, minimus, depth+1, alpha, beta);
        } else {
            temp = 0;
            leaves++;
        }

        if (player){
            maximus -= squaredSize;
            score += squaredSize+temp;
            if (va < score){
                va=score;
                if (depth==1){
                    bestSize = childIlands[i][0];
                    bestState[0] = childIlands[i][1];
                    bestState[1] = childIlands[i][2];
                }
            }
            if (va >= beta){
                prune++;
                return va-maximus+minimus;
            }
            alpha = alpha>va?alpha:va;
        } else {
            minimus -= squaredSize;
            score += temp-squaredSize;
            if (vb > score){
                vb = score;
            }
            if (vb <= alpha){
                prune++;
                return vb-maximus+minimus;
            }
            beta = beta<vb?beta:vb;

        }

    }

    if (player) {
        if (depth<maxDepth)
            m3[boardhash] = va-maximus+minimus;
        return va-maximus+minimus;
    } else {
        if (depth<maxDepth)
            m3[boardhash] = vb-maximus+minimus;
        return vb-maximus+minimus;
    }
}

void initGame(string &board){

    if (goalState(board)){
        return;
    }

    uint64_t maximus = 0;
    uint64_t minimus = 0;
    uint64_t score;
    score = playGame(board, true, maximus, minimus, 1, -123456, 123456);
    bool* visited = (bool*)calloc(sizeof(bool)*n*n,false);
    min_row = bestState[0];
    max_row = bestState[0];
    min_col = bestState[1];
    max_col = bestState[1];

    exploreIland2(board, bestState[0], bestState[1], board[bestState[0]*n+bestState[1]]);
    applyGravity(board);

}

long long totalNodes(uint64_t (&arrayTotal)[677] ,uint32_t num, uint32_t depth, uint32_t maxD){
    if (num==2 || num==1 || (depth == maxD)){
        return 1;
    }
    if (arrayTotal[num]!=0){
        return arrayTotal[num];
    }
    arrayTotal[num] = 1+num+(num*(num-1)*totalNodes(arrayTotal, num-2, depth+1,maxD));
    return arrayTotal[num];
}

void setDepth(uint32_t numIslands){
    int maxN=0, maxK=0, numSamples=0;
    int i=0;
    bool notFound = false;
    double read[3]={0};
    vector <array<double,3>> v = vector<array<double,3>>();

    if(t-(t/15)<=0.05 && n>=15){
        maxDepth=2;
        return;
    }

    ifstream calibrate;
    calibrate.open("calibration.txt");
    if(!calibrate.is_open()){
        if (numIslands<=n*n/2) {
            if (n<=10)
                maxDepth = 6;
            else if (n<=14)
                maxDepth = 5;
            else if (n<=17)
                maxDepth = 4;
        } else {
            maxDepth = 4;
        }

        if (n>=18){
            if(numIslands<=n*n/4)
                maxDepth = 4;
            else
                maxDepth = 3;
        }
        return;
    }
    calibrate>>maxN>>maxK>>numSamples;
    for (i=0;i<n-1 && i+1<=maxN;i++){
        for (int j=0;j<numSamples;j++){
            for(int k=0;k<maxK;k++){
                calibrate>>read[k];
            }
        }
    }
    if(read[0]+1!=n){
            if (n<=19 || numIslands<=1.125*n*n/3){
                maxDepth = 4;
            }else{
                maxDepth = 3;
            }
            return;
    }
        
    for (int j=0;j<numSamples;j++){
        array<double, 3> arr;
        for(int k=0;k<maxK;k++){
            calibrate>>arr[k];
        }
        v.push_back(arr);
    }
    sort(v.begin(),v.end(),sortFunc2);
    int id=0;
    while(numIslands<v[id][1] && id<numSamples)
        id++;
    int idx1 = id-1;
    int idx2 = id;
    double m = (v[idx2][2]-v[idx1][1])/(v[idx2][1]-v[idx1][1]);
    double c = v[idx2][2]-(m*v[idx2][1]);
    // y = nodes/sec
    double y = ((m*numIslands)+c);
    
    for (int d=3;d<=n*n;d++){
        uint64_t arrayTotal[677]={0};
        //total nodes for depth , for branching factor=b
        totalNodes(arrayTotal, numIslands,1,d);
        uint64_t nodeCount[677]={0};
        uint64_t sum = 0;
        for (int i=0;i<=numIslands;i++){
            if (arrayTotal[i]!=0){
                if((sum >= (1LL<<63))&&(arrayTotal[i] >= (1LL<<63))){
                    maxDepth=max(d-1,3);
                    if((time_t)t<=(time_t)0.5 && n>=20){
                        maxDepth = 2;
                    }
                    return;
                }
                sum +=  arrayTotal[i];
                nodeCount[i] = sum;
            }
        }
        uint64_t totalTnodes = (t-(t/15)) * y;
        //check this equals sign
        maxDepth = d-1;
        if(totalTnodes<=(sqrt(nodeCount[numIslands]))){
            break;
        }
        
    }
    
}

int main(){
    char *x = (char*)malloc(sizeof(char)*26*26);
    ifstream input;
    input.open("input.txt");

    input>>n;
    input>>p;
    input>>t;

    string board;
    for (int i=0;i<n;i++){
        input >> x;
        for (int j=0;j<n;j++){
            board += x[j];
            if (x[j]=='*')
                star++;
        }
    }

    input.close();


    vector <array<uint32_t,3>> childIlands = vector<array<uint32_t,3>>();
    uint32_t childIlandsSize = 0;
    getChildren(board, childIlands,&childIlandsSize);

    setDepth(childIlandsSize);
    initGame(board);

    ofstream output;
    output.open("output.txt");
    ofstream output1;
    output1.open("score.txt");
    output1<<bestSize<<endl;
    output1.close();
    output<<char('A'+bestState[1])<<bestState[0]+1<<endl;
    for (int i=0;i<n;i++){
        for (int j=0;j<n;j++){
            output <<board[i*n+j];
        }
        output<<endl;
    }
    output.close();

    ofstream temp;
    temp.open("temp.txt");
    temp<<n<<endl;
    temp<<childIlandsSize<<endl;
    temp<<maxDepth<<endl;
    temp<<count1<<endl;
    temp<<leaves<<endl;
    temp<<saved<<endl;
    temp<<savedIlands<<endl;
    temp<<prune<<endl;
    temp.close();

    return 0;
}
