/*Завдання 0.2.11, друга домашня робота*/
#include <cstdio>

int main(){

    float a;
    printf("Input a: ");
    scanf("%f", &a);

    // a)
    printf("\n%.5g %.5g %.5g\n", a, a, a);
    printf("%.5g %.5g %.5g\n", a, a, a);
    printf("%.5g %.5g %.5g\n", a, a, a);

    // b)
    printf("\n%.5g----------%.5g\n", a, a);
    printf("|      %.5g      |\n", a);
    printf("%.5g----------%.5g\n", a, a);

}

