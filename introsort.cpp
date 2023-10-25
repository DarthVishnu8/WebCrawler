#include <cmath>
#include "partition.cpp"
#include "hsort.cpp"
#include "isort.cpp"
#include <vector>
using namespace std;

static int c =0;
void introsort(vector<int>& v, int l, int r, int thresold) {
int pivot = r;
if(c < thresold){
partition(v, l, r, pivot);
introsort(v,l,pivot-1, pivot);
introsort(v,pivot+1,r,pivot);
}
else{
if(r-l>16){

hsort(v,l,r);
return;
}
else{
isort(v,l,r);
return;
}
}
}

void introsort(vector<int>& v) {
int thresold = 4; // Choose a thresold such the performance is best
introsort(v, 0, v.size() - 1, thresold*std::log2(v.size())); // depth is logarithmic meaning worst case is nlogn

if(v[0] >v[1]){
int t = v[0];
v.erase(v.begin());
for(int i=0;i<v.size();i++){
if(v[i] > t){
int x = t;
t = v[i];
v[i] = x;

}
}
v.push_back(t);
}
}