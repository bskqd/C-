#include <stdio.h>

int recurs(int n) {
    int a = n;
    for(unsigned i=1;i<=n;i++){
        if (i % 2 != 0){
            a = 3*a + 1;
        } else {
            a = a / 2;
        }
    }
    return a;
}

int main_tryjfh(){
    int n;
    scanf("%d", &n);
    printf("%d", recurs(n));
}
