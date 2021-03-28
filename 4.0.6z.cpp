#include <stdio.h>

typedef struct {
    double base_length;
    double base_width;
    double height;
} Rect;

void input (Rect * x) {
    Rect res;
    printf("Перша сторона основи=");
    scanf("%lf", &res.base_length);
    printf("Друга сторона основи=");
    scanf("%lf", &res.base_width);
    printf("Висота=");
    scanf("%lf", &res.height);
    *x = res;
}

void output (const Rect rect) {
    printf("\nСторони вашого паралелепіпеда:\n");
    printf("Перша сторона основи=%lf\n", rect.base_length);
    printf("Друга сторона основи=%lf\n", rect.base_width);
    printf("Висота=%lf", rect.height);
}

int main() {
    Rect x;
    input(&x);
    output(x);
}
