#include <cstdio>
#include <cmath> // floor

int main_1(){

    double d;
    printf("Real number: ");
    scanf("%lf", &d);

    int z1 = floor(d);
    printf("\nzila chastyna= %d\n", z1);

    double d1;
    d1 = d - z1;
    printf("drobova chastyna= %lf\n", d1);

    int z2 = ceil(d);
    printf("[%lf]= %d\n", d, z2);

    int z3 = round(d);
    printf("round(%lf)= %d\n", z3);

}
