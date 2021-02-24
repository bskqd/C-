#include <stdio.h>

double recurs(int b, int n) {
    double res = b;
    for(unsigned i=0;i<n;++i){
        res = b + 1/res;
    }
    return res;
}

int main_152635315(){
    int b, n;
    scanf("%d %d", &n, &b);
    printf("%lf", recurs(b, n));
}
