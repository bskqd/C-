// 1.19з
#include <stdio.h>

int fact(int k){
    int c = 0, f = 1;

    while (c <= k){
        f *= 2*c + 1;
        c++;
    }
    return f;
}

double power(double x, int k){
    int full_power = 2*k + 1, i = 1;
    double result = 1;

    while (i <= full_power){
        result *= x;
        i++;
    }
    return result;
}

int main_214112(){
    double x;
    int k;
    printf("x=");
    scanf("%lf", &x);
    printf("\nk=");
    scanf("%d", &k);

    long double result = power(x, k) / fact(k);

    if (k % 2 == 0){
        printf("%Lf", result);
    } else{
        printf("%Lf", result * (-1));
    }
}
