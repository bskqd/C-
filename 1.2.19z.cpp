// 1.2.19з
#include <stdio.h>

double fact(double x, int k){
    int c = 0, full_power = 2*k + 1, i = 1;
    double result = 1, f = 1, result_full;

    while (c <= k){
        f *= 2*c + 1;
        c++;
    }

    while (i <= full_power){
        result *= x;
        i++;
    }

    result_full = result / f;
    return result_full;
}

int main_7634524125637(){
    double x;
    int k;
    printf("x=");
    scanf("%lf", &x);
    printf("\nk=");
    scanf("%d", &k);

    double result = fact(x, k);

    if (k % 2 == 0){
        printf("%lf", result);
    } else{
        printf("%lf", result * (-1));
    }
}
