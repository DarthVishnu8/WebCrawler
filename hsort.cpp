#include <vector>
using namespace std;

void heapify(vector<int>& v, int N, int i, int left){
int largest = i;
int l = 2*i+1;
int r = 2*i+2;
if(l < N && v[l+left] > v[largest+left]) largest=l;
if(r < N && v[r+left] > v[largest+left]) largest=r;
if(largest != i){
int temp = v[i+left];
v[i+left] = v[largest+left];
v[largest+left] = temp;
heapify(v, N, largest, left);
}
}

void hsort(vector<int>& v, int left, int right) {
int N = right-left+1;
for(int i=N/2-1; i>=0;i--){
heapify(v,N,i,left);
}
for(int i=N-1; i>0;i--){
int temp = v[left];
v[left] = v[i+left];
v[i+left] = temp;
heapify(v,i,0,left);
}
}