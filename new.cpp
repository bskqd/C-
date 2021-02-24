#include <cstdio>

int main_1(){

    long long n, m, k;
    scanf("%Ld, %Ld, %Ld", &n, &m, &k);
    long long num = n*m*k;
    printf("%Ld", num);

    printf("int_size=%zu, long_size=%zu, long_long_size=%zu", sizeof(int), sizeof(long), sizeof(long long));

}

