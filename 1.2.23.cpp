// 1.2.23
#include <stdio.h>

int main_22141362624(){
    int n, k = 0, i = 0, result = 0;

    printf("Input n: ");
    scanf("%d", &n);

    int lst[n];

    while (i < n){
        printf("Input a number: ");
        scanf("%d", &k);
        lst[i] = k;
        i++;
    }

    for (int j = 0; j < n; j++){
        if (j != 0 && j != n-1) {
            if (lst[j-1] < lst[j] && lst[j] > lst[j+1]){
                result++;
                ++i;
            }
        }
    }

    printf("result: %d", result);
}
