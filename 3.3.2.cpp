#include <stdio.h>
#include <stdlib.h>

#define N 100

int input(double * a, int n){
    int count = 0;
    for(int i = 0; i < n; i++){
        printf("a[%d]=", i);
        scanf("%lf", &a[i]);
        if (a[i] == 0.0 || a[i] == 0){
            break;
        }
        count++;
    }
    return count;
}

double sum_sq(double * a, int n){
    double s = 0;
    for(int i = 0; i < n; i++){
        s += a[i] * a[i];
    }
    return s;
}

double triple_sq(double * a, int n){
    double s = 0;
    for(int i = 0; i < n; i++){
        s += a[i] * a[i] * a[i];
    }
    return s;
}

int main(){
    int n;
    printf("n = ");
    scanf("%d", &n);
    double* a = (double *) malloc(n * sizeof(double));
    input(a, n);
    printf("Double squares: %lf\n Triple squares: %lf", sum_sq(a, n), triple_sq(a, n));
    free(a);
}
