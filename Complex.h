
#include <exception>

using namespace std;

/**
 * a+bi
 * */
class Complex {
    double a;
    double b;

public:
    Complex(double a, double b) {
        this->a = a;
        this->b = b;
    }

    Complex() {
        input();
    }

    static Complex atan(Complex z);

    void print();

    void input();
};

class BadDataException : public exception {
public:
    const char *what() const throw() {
        return "Provided data is invalid";
    }
};

class NonAbsLessOne : public exception {
public:
    const char *what() const throw() {
        return "Number is not less than 1";
    }
};