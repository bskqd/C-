#include <stdio.h>

int main(){
    int a = 0, result = 0;

    do {
        printf("a[%d]=", a);
        scanf("%d", &a);
        result += a;
    } while (a != 0);

    printf("result: %d", result);
}
