// 1.1.9

#include <cstdio>

int main_6() {

    double x, y, r, a, b, c;
    int count = 0;
    printf("x y r a b c: ");
    scanf("%lf %lf %lf %lf %lf %lf", &x, &y, &r, &a, &b, &c);

    if (x != a){
        printf("x must be equal to a");
    } else if (y <= b or y >= b + c*c){
        printf("b <= y <= b + c*c");
    }

    if (x == r){
        count++;
    } else if (x <= r){
        count += 2;
    }

    if (b == r or (b == -r and b + c*c >= r)){
        count++;
    } else if (b == -r and b + c*c == r){
        count += 3;
    } else if (b == -r and b + c*c == r) {
        count += 2;
    }

    printf("%d", count);
}
