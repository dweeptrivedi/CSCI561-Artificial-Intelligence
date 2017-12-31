#include <iostream>
#include <fstream>
#include <cstdlib>
#include <string>
#include <cstring>
#include <cmath>
#include <sys/time.h>
#include <algorithm>

using namespace std;

int maxK = 3;
int maxN = 26;
int filenum = 0;
float timeRemaining = 300;
struct timeval timeval1;
struct timeval timeval2;
double time1;
double time2;
double timediff;

double matrix1[26][26];
double matrixn[26][26];
double matrixn2[26][26];
double matrixr[26][26];
double matrixr2[26][26];

void playGame(){
    gettimeofday(&timeval1, NULL);
    int abc = system("./homework11");
    gettimeofday(&timeval2, NULL);
    time1 = double(timeval1.tv_sec)*1000000.0 + double(timeval1.tv_usec);
    time2 = double(timeval2.tv_sec)*1000000.0 + double(timeval2.tv_usec);
    //cout<<(time2-time1)/1000000.0<<endl;
    timediff = (time2-time1)/1000000.0;
}

void readTime(double (&matrix)[26][26]) {
    char *x = (char*)malloc(sizeof(char)*26*26);
    int y,n;
    int k=0;
    ifstream temp;
    temp.open("temp.txt");
    temp>>n;
    while(!temp.eof()) {
        temp>>x;
        y = atoll(x);
        matrix[n][k] = y;
        k++;
    }
    matrix[n][k] = timediff;
    maxK =  k;
    free(x);
}

void writeToInput(string &board, int n) {

    ofstream input;
    input.open("input.txt");
    input<<n<<endl;
    input<<n<<endl;
    input<<timeRemaining<<endl;
    for (int i=0;i<n;i++){
        for (int j=0;j<n;j++){
            input<<board[i*n+j];
        }
        input<<endl;
    }
    input.close();
    return;
}

void generate_one_island_board(int n){
    string board(n*n,'0');
    writeToInput(board, n);
}


void generate_nby2_island_board(int n){
    string board(n*n,'0');
    int fruits;

    for (int i=0;i<n;i++){
        fruits = rand()%10;
        for(int j=0;j<n/2;j++){
            board[i*n+j] = '0'+fruits;
        } 
        fruits = rand()%10;
        for(int j=(n/2)+1;j<n;j++){
            board[i*n+j] = '0'+fruits;
        } 
    }
    writeToInput(board, n);
}

void generate_nsquare_island_board(int n){
    string board(n*n,'0');
    int fruits;
    for (int i=0;i<n;i++){
        for(int j=0;j<n;j++){
            fruits = (j+i)%10;
            board[i*n+j] = '0'+fruits;
        }
    }
    writeToInput(board, n);
}

void generate_random_island_board(int n){
    string board(n*n,'0');
    int fruits;
    for (int i=0;i<n;i++){
        for(int j=0;j<n;j++){
            fruits = rand()%10;
            board[i*n+j] = '0'+fruits;
        }
    }
    writeToInput(board, n);
}

void generate_random_island_board2(int n){
    string board(n*n,'0');
    int fruits;
    int maxfruits = (rand()%9)+2;
    for (int i=0;i<n;i++){
        for(int j=0;j<n;j++){
            fruits = rand()%maxfruits;
            board[i*n+j] = '0'+fruits;
        }
    }
    writeToInput(board, n);
}

int main(){

if(!system(NULL)){
    cout<<"No system command processor found!!"<<endl;
    return 0;
}

bool isThere = false;
ifstream input;
input.open("input.txt");
if (input.good()){
input.close();
isThere = true;
int abc = system("cp input.txt abcd.txt");
}
int abcd = system("g++ homework11.cpp -std=gnu++11 -o homework11");

ofstream calibrate;
calibrate.open("calibration.txt");
if (calibrate.is_open()){
    calibrate.close();
    int abcde = system("rm -rf calibration.txt");
} else {
    calibrate.close();
}

for (int i=1;i<=maxN;i++) {

generate_one_island_board(i);
playGame();
readTime(matrix1);

generate_nby2_island_board(i);
playGame();
readTime(matrixn);

generate_nsquare_island_board(i);
playGame();
readTime(matrixn2);

generate_random_island_board(i);
playGame();
readTime(matrixr);

generate_random_island_board2(i);
playGame();
readTime(matrixr2);

}

calibrate.open("calibration.txt");
calibrate<<maxN<<endl;
//maxK
calibrate<<3<<endl;
//numSamples
calibrate<<5<<endl;

//eq = (maxDepth+(nodes/N))/(timediff-overhead)
//why did I do nodes/N?
for (int i=1;i<=maxN;i++){
    double overhead = matrix1[i][maxK];
    calibrate<<i<<endl<<matrix1[i][0]<<endl<<((matrixn[i][2]*matrixn[i][2]+(matrixn[i][3]/matrixn[i][0]))/fabs(matrixn[i][maxK]-overhead))<<endl;
    calibrate<<i<<endl<<matrixn[i][0]<<endl<<((matrixn[i][2]+(matrixn[i][3]/matrixn[i][0]))/fabs(matrixn[i][maxK]-overhead))<<endl;
    calibrate<<i<<endl<<matrixr[i][0]<<endl<<((matrixr[i][2]+(matrixr[i][3]/matrixr[i][0]))/fabs(matrixr[i][maxK]-overhead))<<endl;
    calibrate<<i<<endl<<matrixr2[i][0]<<endl<<((matrixr2[i][2]+(matrixr2[i][3]/matrixr2[i][0]))/fabs(matrixr2[i][maxK]-overhead))<<endl;
    if (i>=20) {
    calibrate<<i<<endl<<matrixn2[i][0]<<endl<<((matrixn2[i][2]*1.25)/fabs(matrixn2[i][maxK]-overhead))<<endl;
    } else {
    calibrate<<i<<endl<<matrixn2[i][0]<<endl<<((matrixn2[i][2]+(matrixn2[i][3]/matrixn2[i][0]))/fabs(matrixn2[i][maxK]-overhead))<<endl;
    }
}
calibrate.close();

if (isThere){
int abcdef = system("mv abcd.txt input.txt");
}

return 0;
}
