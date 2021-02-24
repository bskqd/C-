#include <stdio.h>

#define N 10

double scal_sum(double mas[], double mas2[], double mas3[], int n){
    for(int i = 0; i < n; i++){
        mas3[i] = (mas[i] + mas2[i]);
    }
    return true;
}

void output(double mas3[], int n){
    printf("Elements of scal_sum:\n");
    for(int i = 0; i < n; i++){
        printf("%lf\n", mas3[i]);
    }
}

double scal_mult(double mas[], double mas2[], int n){
    double mult = 1.0;
    for(int i = 0; i < n; i++){
        mult += (mas[i] * mas2[i]);
    }
    return mult;
}

int main(){
    int sum_par = 0, sum_nepar = 0, n;
    double mas[N], mas2[N], mas3[N];
    printf("Input n: ");
    scanf("%d", &n);
    if(n > 10){
        printf("N must be <= 10");
    }
    for(int i = 0; i < n; i++){
        printf("mas[%d]=", i);
        scanf("%lf", &mas[i]);
    }
    for(int i = 0; i < n; i++){
        printf("mas2[%d]=", i);
        scanf("%lf", &mas2[i]);
    }
    scal_sum(mas, mas2, mas3, n);
    output(mas3, n);
    printf("Scal mult = %lf", scal_mult(mas, mas2, n));
}
