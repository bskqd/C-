#include "Complex.h"
#include <bits/stdc++.h>

using namespace std;


double atanSimple(double x) {
    int i = 3;
    int one = -1;
    double prev = 0;
    double s = x;

    while (abs(prev - s) > DBL_EPSILON) {
        prev = s;
        s += one * pow(x, i) / i;
        one *= -1;
        i += 2;
    }
    return s;
}

Complex Complex::atan(Complex z) {
    int i = 3;
    int one = -1;
    complex<double> prev = 0;
    complex<double> x(z.a, z.b);
    complex<double> s = x;

    if (abs(x) >= 1) {
        throw NonAbsLessOne();
    }

    while (abs(prev.operator-=(s)) > DBL_EPSILON) {
        prev = s;
        s += pow(x, i).operator*=(one).operator/=(i);
        one *= -1;
        i += 2;
    }

    return Complex{s.real(), s.imag()};
}

void Complex::print() {
    cout << this->a << " + " << this->b << "i" << endl;
}

void Complex::input() {
    double real;
    cout << "a=";
    cin >> a;
    this->a = real;

    if (cin.fail()) {
        throw BadDataException();
    }

    double img;
    cout << "b=";
    cin >> b;
    this->b = img;

    if (cin.fail()) {
        throw BadDataException();
    }
}
