#include <stdio.h>
#include <string.h>

#define N 100

int main(){
    char str[N];  //char* str = NULL pointer
    printf("Input string: ");
    fgets(str, N, stdin);
    int n = strlen(str);
    int i = 0, j = 0;
    char str2[N];
    while(i < n) {
        if(str[i] == '('){
            int k = i + 1;
            while(str[k - 1] != ')'){
                if(k == n){
                    printf("Wrong sentence");
                } else{
                    if(str[k] == '('){
                        printf("Nested ()");
                    }
                }
                k++;
                i++;
            }
        } else{
            str2[j] = str[i];
            j++;
        }
        i++;
    }
    printf("%s", str2);
}
