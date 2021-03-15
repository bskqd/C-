#include <stdio.h>
#include <cstring>

#define N 10

int count_char(char* str, char ch){
    int i = 0, count = 0;

    while(i < strlen(str)) {
        if(str[i]==ch) {
            count++;
        }
        i++;
    }
    return count;
}

int main_afdsgfhdgjfhkg(){
    char str[N];
    int max_count = 0, min_count;
    char min, max;
    printf("Input string: ");
    fgets(str, N, stdin);
    for (int i = 0; i < strlen(str); i++) {
        int count = 0;
        count += count_char(str, str[i]);
        if (i == 0){
            min_count = count;
        }
        if (count > max_count) {
            max_count = count;
            max = str[i];
        }
        if (count < min_count) {
            min_count = count;
            min = str[i];
        }
    }
    printf("Max count = %d, char = %c\n", max_count, max);
    printf("Min count = %d, char = %c", min_count, min);
}
