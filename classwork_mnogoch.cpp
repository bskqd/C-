#include <stdio.h>

double power(double x, int k){
    int i = 1;
    double result = 1;

    while (i <= k){
        result *= x;
        i++;
    }
    return result;
}

int fact(int k){
    int c = 1, f = 1;

    while (c <= k){
        f *= c;
        c++;
    }
    return f;
}

int main(){
    double x, result = 1;
    int k, i = 1;
    scanf("%lf %d", x, k);
    while (i <= k){
        result += power(x, i)/ fact(k);
        i++;
    }
    printf("result: %lf", result);
}
