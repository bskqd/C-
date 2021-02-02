#include <cstdio>
#include <cmath> // floor

int main_3(){

    double d1, d2;
    printf("Real number: ");
    scanf("%lf %lf", &d1, &d2);

    double z1 = (d1 + d2)/2;
    printf("\nserednye arifmet= %le, serednye arifmet= %lf\n", z1, z1);

    double z2 = 2/(1/d1 + 1/d2);
    printf("[z2] = %le, [h2] = %lf\n", z2, z2);

}
