// 2.0.12
#include <stdio.h>
#define N 10
#define TRIPLE_N 30

void output(int mas[]) {
    for(int i = 0; i < N; i++){
        printf("mas_b[%d]=%d\n", i, mas[i]);
    }
}

void code(int mas_a[], int mas_b[]) {
    printf("CODE\n");
    for(int i = 0; i < N; i++) {
        if(i == 0) {
            mas_b[0] = mas_a[0];
        } else {
            mas_b[i] = mas_a[i - 1] == mas_a[i] ? 1 : 0;
        }
    }
    output(mas_b);
}

void decode(int mas_b[], int mas_a[]) {
    printf("DECODE\n");
    for(int i = 0; i < N; i++) {
        if(i == 0) {
            mas_a[0] = mas_b[0];
        } else {
            if(mas_b[i] == 1) {
                mas_a[i] = mas_a[i - 1];
            } else {
                mas_a[i] = mas_a[i - 1] == 1 ? 0 : 1;
            }
        }
    }
    output(mas_a);
}

void decode_with_errors(int mas_b[], int mas_a[]) {
    int new_mas_b[N];
    for(int i = 0; i < TRIPLE_N; i++) {
        if((i + 1) % 3 == 0) {
            int check_triple = 0;
            check_triple += mas_b[i - 2];
            check_triple += mas_b[i - 1];
            check_triple += mas_b[i];
            new_mas_b[i - 2] = check_triple >= 2 ? 1 : 0;
        }
    }
    decode(new_mas_b, mas_a);
}

int main() {
    int mas_a[N], mas_b[N], triple_mas_b[TRIPLE_N];
//  для пунктів а), б)
    for(int i = 0; i < N; i++) {
        bool passed = false;
        while(not passed) {
            printf("mas_a[%d]=", i);
            scanf("%d", &mas_a[i]);
            if(mas_a[i] == 1 || (mas_a[i] == 0)){
                passed = true;
            }
        }
    }
    code(mas_a, mas_b);
    decode(mas_b, mas_a);
//  для пункту с)
    for(int i = 0; i < TRIPLE_N; i++) {
        bool passed = false;
        while(not passed) {
            printf("triple_mas_b[%d]=", i);
            scanf("%d", &triple_mas_b[i]);
            if(triple_mas_b[i] == 1 || (triple_mas_b[i] == 0)){
                passed = true;
            }
        }
    }
    decode_with_errors(triple_mas_b, mas_a);
}
