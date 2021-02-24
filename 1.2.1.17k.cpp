#include <stdio.h>
#include <math.h>

int main_DFASDGSA(){
    double x;
    int eps, k = 2;
    do {
        printf("Input x: ");
        scanf("%lf", &x);
    } while (x >= 1);
    do {
        printf("Input eps: ");
        scanf("%d", &eps);
    } while (fabs(eps) > 0.001);

    double y = 1.0, local_y = 1;
    while (y >= eps){
        if (k == 2) {
            local_y *= 3 * x;
        } else {
            local_y *= k * (k + 1) * x / 2;
        }
        if (k % 2 == 0) {
            local_y = -local_y;
        }
        y += local_y;
        k++;
    }
    printf("%lf", y);
}
