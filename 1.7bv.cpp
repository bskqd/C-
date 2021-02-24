#include <stdio.h>

int main_1421515() {
    int k = 3;
    int x0 = -99, x1 = -99, x2 = -99, xn;
    if (k <= 2){
        printf("-99");
    }
    while(x2<0){
        xn = x2 + x1 + x0 + 100;
        x0 = x1;
        x1 = x2;
        x2 = xn;
        k++;
    }
}
