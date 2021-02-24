#include <stdio.h>
#include <math.h>

double all_in_one(double x, int k){
    double y = 1;
    double power = x;

    for (int i=1;i<=k;++i){
        y += power;
        power *= x / (i+1);
    }
    return y;
}

int main_235(){
    double x;
    unsigned k;
    printf("Input k: ");
    scanf("%d\n", &k);
    do{
        printf("Input x: ");
        scanf("%lf", &x);
    } while (fabs(x) > 1);
    double result = all_in_one(x, k);
    printf("result: %lf", result);
}
