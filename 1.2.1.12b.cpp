// 1.2.1.12б
#include <stdio.h>

int main_dfasgfhdg() {
    int n, k = 2;
    long double u, v, a1, b1, a, b, sum = 1, sum_ab = 0, fact = 2;
    printf("Input n u v: ");
    scanf("%d %Lf %Lf", &n, &u, &v);

    sum_ab += u * v;
    sum *= sum_ab / fact;
    a1 = u;
    b1 = v;

    if (n == 1){
        printf("%Lf", sum);
    } else {
        while (k <= n) {
            fact *= (k + 1);
            a = 2 * b1 + a1;
            b = 2 * a1 * a1 + b1;
            a1 = a;
            b1 = b;
            sum_ab += a * b;
            sum += sum_ab / fact;
            k++;
        }
    }
    printf("%Lf", sum);
}
