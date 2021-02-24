#include <stdio.h>

double power(int k){
    int i = 0;
    double result = 1;

    while (i <= k){
        result *= 2;
        i++;
    }
    return result;
}

int main(){
    int n;
    int r = 0;
    printf("Input n: ");
    scanf("%d", &n);

//    while (power(r) <= n){
//        r++;
//    }
    do {
        power(r);
        r++;
    } while (power(r) <= n);

    printf("2^r: %lf", power(r));
}
