#include <cstdio>
#include <math.h>

double printSquareEquation(double a, double b, double c){

    if (a == 0){
        printf("%lf", -c);
        printf("One: %lf", -c / b);
    } else {
        double d = sqrt(b * b - 4 * a * c);
        double x1, x2;
        x1 = (-b + d) / (2 * a);
        x2 = (-b - d) / (2 * a);
        printf("Two: %lf, %lf", x1, x2);
    }

}

int main_9(){

    double a, b, c;
    scanf("%lf, %lf, %lf", &a, &b, &c);
    printSquareEquation(a, b, c);

}

