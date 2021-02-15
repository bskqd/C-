// 1.2.9a
#include <stdio.h>

int main(){
    double x;
    int n;
    printf("x = ");
    scanf("%lf", &x);
    printf("\nn = ");
    scanf("%d", &n);

    int i = 2;
    long double result = 1, loc_result = 1;

    while (i <= n){
        loc_result *= x * i;
        result += loc_result;
        i++;
    }

    printf("result = %Lf", result);
}
