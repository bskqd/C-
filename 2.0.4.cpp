#include <stdio.h>

#define N 5

int main(){
    double mas[N], max = 0;
    for(int i = 0; i < N; i++){
        printf("mas[%d]=", i);
        scanf("%lf", &mas[i]);
        if(max < mas[i]){
            max = mas[i];
        }
    }
    printf("%lf", max);
}
