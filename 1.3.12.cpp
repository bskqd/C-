#include <stdio.h>

void bin(unsigned n){
    if (n > 1)
        bin(n / 2);

    printf("%d", n % 2);
}

int main(){
    unsigned n;
    printf("Input n: ");
    scanf("%d", &n);
    bin(n);
}