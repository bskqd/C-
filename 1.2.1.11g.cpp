// 1.2.1.11г
#include <stdio.h>

int main_1526y() {
    int n, k = 3;
    long double a0 = 0.0, a1 = 1.0, a, sum = 2, fact = 2;
    printf("Input n: ");
    scanf("%d", &n);

    if (n == 1){
        printf("%Lf", a0);
    } else if (n == 2){
        printf("%Lf", a1 * 2);
    } else {
        while (k <= n) {
            fact *= k;
            a = a1 + a0 / (fact / k);
            a0 = a1;
            a1 = a;
            sum += fact * a;
            k++;
        }
    }
    printf("%Lf", sum);
}
