#include <vector>
using namespace std;

void partition(std::vector<int> &v, int left, int right, int &pivot) {
int temp;
int pi=left;
for(int i=left; i<right; i++){
if(v[i] <= pivot){
temp = v[i];
v[i] = v[pi];
v[pi] = temp;
}
}
temp = v[right];
v[right]=v[pi];
v[pi]=temp;
pivot = pi;
}