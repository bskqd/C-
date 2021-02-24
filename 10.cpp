#include <stdio.h>

double power(unsigned k){
    unsigned i = 0;
    double result = 1;

    while (i <= k){
        result *= 4;
        i++;
    }
    return result;
}

int main_12412132142(){
    int m;
    unsigned k = 0;
    printf("Input m: ");
    scanf("%d", &m);

    while (power(k) <= m){
        k++;
    }

    printf("k: %d", k);
}
