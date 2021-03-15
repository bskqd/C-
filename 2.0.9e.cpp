// 2.0.9е
#include <stdio.h>
#include <math.h>

#define N 5

bool is_prime(int k){
    double m = sqrt(k);
    if(k == 1 || k == 2){
        return false;
    }
    for(int i = 2; i <= m; i++){
        if(k % i == 0){
            return false;
        }
    }
    return true;
}

int main_dsfdsgfhdg(){
    int mas[N], prime_numbers = 0;
    for(int i = 0; i < N; i++){
        printf("mas[%d]=", i);
        scanf("%d", &mas[i]);
        if(is_prime(mas[i])){
            printf("%d\n", mas[i]);
            prime_numbers++;
        }
    }
    printf("Всього простих = %d\n", prime_numbers);
}

