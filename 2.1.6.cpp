#include <stdio.h>

#define N 3

int main(){
    int k, f = 0;
    int mas[N][N] = {   {1, 2, 3},
                        {4, 5, 6},
                        {7, 8, 9}
    };
    scanf("%d", &k);
    for(int i = 0; i < N; i++){
        for(int j = 0; j < N; j++) {
            if(i - j == k){
                f += mas[i][j];
            }
        }
    }
    printf("%d", f);
}
