#include <stdio.h>
#include <math.h>

int main_dsafdfs(){

    double x, eps;
    double a, y;
    int k = 0;

    do{
        printf("x (x!=0) = ");
        scanf("%lf", &x);
    } while (fabs(x)<0.00001);

    do{
        printf("eps (eps!=0) = ");
        scanf("%lf", &eps);
    } while (eps<0.00001);

    a = 1.0;
    y = a;

    while(fabs(a)>eps){
        k++;
        a = a * (-x) * k * k / (k + 1) / (k + 1) ;
        y += a;
    }

    printf("y = %lf", y);

}
