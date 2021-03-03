#include <stdio.h>

#define N 3

double transpon(double mas[N][N], int k, int l, double a){
    for(int i = 0; i < N; i++){
        for(int j = 0; j < N; j++) {
            double temp = mas[i][j];
            mas[i][j] = mas[j][i];
            mas[i][j] = temp;
            if(k == i && l == j){
                mas[i][j] = a;
            }
        }
    }
}

int main(){
    double mas[N][N] = {{1.0, 2, 3},
                        {4, 5, 6},
                        {7, 8, 9}
    };
    int k, l;
    double a;
    scanf("%d, %d, %lf", &k, &l, &a);
    transpon(mas, k, l, a);
    for(int i = 0; i < N; i++){
        for(int j = 0; j < N; j++) {
            printf("%lf, ", mas[i][j]);
        }
        printf("\n");
    }
}
