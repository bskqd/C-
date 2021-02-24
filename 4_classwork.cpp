#include <stdio.h>

int main_11(){

    double y,x;
    unsigned n;
    printf("x=");
    scanf("%lf", &x);
    printf("\nn=");
    scanf("%u", &n);

    y = 1;
    int power = 1;

    double y_1=1;
    int power_1 = 1;

    for (int i=0; i<n; i++){
        power *= x*x;
        y += power;
    }

    for (int i=0; i<n; i++){
        power_1 *= x*x*x;
        y_1 += power;
    }

    printf("%lf", y);
    printf("\n%lf", y_1);

}
