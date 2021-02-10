//1.1.16а
#include <stdio.h>
#include <math.h>
#include <float.h>

bool check_sign(double x, double y) {
    return ((x<0) == (y<0));
}

int main_124114() {
    double x0, y0, x1, y1, x2, y2, x3, y3;
    const double lowest_double = -DBL_MAX;
    printf("Input x0 y0 x1 y1 x2 y2 x3 y3: ");
    scanf("%lf %lf %lf %lf %lf %lf %lf %lf", &x0, &y0, &x1, &y1, &x2, &y2, &x3, &y3);

    if ((x0 == x1 && y0 == y1) || (x0 == x2 && y0 == y2) || (x0 == x3 && y0 == y3) || (x1 == x2 && y1 == y2) || (x1 == x3 && y1 == y3) || (x2 == x3 && y2 == y3)) {
        printf("Трикутник не може існувати");
    } else {
        double result1 = (x1-x0)*(y2-y1)-(x2-x1)*(y1-y0);
        double result2 = (x2-x0)*(y3-y2)-(x3-x2)*(y2-y0);
        double result3 = (x3-x0)*(y1-y3)-(x1-x3)*(y3-y0);
        if (fabs(result1) < lowest_double || fabs(result2) < lowest_double || fabs(result3) < lowest_double) {
            printf("Точка лежить на одній зі сторін трикутника");
        } else if (check_sign(result1, result2) && check_sign(result1, result3) && check_sign(result2, result3)) {
            printf("Точка належить трикутнику");
        } else {
            printf("Точка лежить поза трикутником");
        }
    }
}
