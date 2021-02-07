// 0.3.6ж

#include <stdio.h>
#include <math.h>

double sigmoid(double x) {
    double result = 1 / (1 + exp(-x));
    return result;
}

double sigmoid_derivative(double x){
    double result = sigmoid(x) * (1 - sigmoid(x));
    return result;
}

int main_4(){
    double x, sigm, sigm_der;
    scanf("%lf", &x);
    sigm = sigmoid(x);
    sigm_der = sigmoid_derivative(x);
    printf("f(x)=%lf\n", sigm);
    printf("g(x)=%lf", sigm_der);
}
