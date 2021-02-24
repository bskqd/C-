#include <stdio.h>

#define N 5

int main_fhgsj(){
    int mas[N], max = 0;
    for(int i = 0; i < N; i++){
        printf("mas[%d]=", i);
        scanf("%d", &mas[i]);
        if(max < mas[i]){
            max = mas[i];
        }
    }
    printf("%d", max);
}
