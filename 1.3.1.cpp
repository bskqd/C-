#include <stdio.h>

int main_ywhe(){

    unsigned char n;
    unsigned long long m;
    printf("n = ");
    scanf("%hhu", &n);

    m = 1<<n; // n < 64, (2 ** n), 1 = 1 << 0, 1 << 1 == (10) == 2
    printf("m = %Lu", m);

}
