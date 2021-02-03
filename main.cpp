#include <cstdio>
#include <math.h>

double def(double x, double y, double z, double k){
    double A = sqrt((z-x)*(z-x) + (k-y)*(k-y));
    return A;
}

int main() {

    double a,b,c,d,e,f;
    scanf("%lf %lf", &a,&b);
    scanf("%lf %lf", &c,&d);
    scanf("%lf %lf", &e,&f);

    double A = def(a,b,c,d);
    double B = def(c,d,e,f);
    double C = def(e,f,a,b);

    double p = (A + B + C)/2;

    double S = sqrt(p*(p-A)*(p-B)*(p-C));

    printf("%lf", S);

}
