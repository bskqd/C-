#include <stdio.h>

#define N 5

int main(){
    int mas[N], sum_par = 0, sum_nepar = 0;
    for(int i = 0; i < N; i++){
        printf("mas[%d]=", i);
        scanf("%d", &mas[i]);
        if(mas[i] % 2 == 0){
           sum_par += mas[i];
        } else{
            sum_nepar += mas[i];
        }
    }
    printf("Сума парних = %d\n", sum_par);
    printf("Сума непарних = %d", sum_nepar);
}
