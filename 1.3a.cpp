#include <stdio.h>

int main_12412(){
    int n = 5;
//    a)
//    double p=1.0, d=1.0;
//    for(int i=1;i<=n;i++){
//        d /= i;
//        p *= (2 + d);
//    }
//    printf("%lf", p);

    double p=1.0;
    for(int i=1;i<=n;i++){
       p *= (i + 1)/(i + 2);
    }
    printf("%lf", p);

}
