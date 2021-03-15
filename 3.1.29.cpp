#include <stdio.h>
#include <cstring>

#define N 10

int main(){
    char str[N], new_str[N];
    printf("Input string: ");
    fgets(str, N, stdin);
    int len = strlen(str);
    for (int i = 0; i < len; i++) {
        if (str[i] != str[len - 1 - i]){
            for (int j = i; j < len - i; j++) {
                strncat(new_str, &str[j], 1);
            }
            break;
        }
    }
    printf("%s", new_str);
}
