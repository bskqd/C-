#include "Vector.h"

void Vector::initArray() {
    for (int i = 0; i < this->n; ++i) {
        double el;
        cout << "arr[" << i << "] = ";
        cin >> el;
        this->setCoordinate(i, el);
    }
}

void Vector::setCoordinate(int index, double el) {
    this->coordinates[index] = el;
}

int Vector::getN() const {
    return n;
}

void Vector::setN(int n) {
    Vector::n = n;
}

double *Vector::getCoordinates() const {
    return coordinates;
}

void Vector::setCoordinates(double *coordinates) {
    Vector::coordinates = coordinates;
}

void Vector::initArray(int n, double *coordinates) {
    this->n = n;
    this->coordinates = coordinates;
}

double Vector::getCoordinate(int index) {
    if (index >= this->getN()) {
        throw invalid_argument("Provided index is grater then vector's size");
    }
    return this->coordinates[index];
}

double Vector::scalarProduct(Vector other) {
    if (this->getN() != other.getN()) {
        throw invalid_argument("Vectors' size must be equal!");
    }

    double res = 0;
    for (int i = 0; i < this->getN(); ++i) {
        res += this->getCoordinate(i) * other.getCoordinate(i);
    }
    return res;
}

Vector Vector::crossProduct(Vector other) {
    Vector res = {3, false};
    if (other.getN() != 3 || this->getN() != 3) {
        cout << other.getN() << " size is not supported";
        return res;
    }
    res.setCoordinate(0, this->getCoordinate(1) * other.getCoordinate(2) -
                         this->getCoordinate(2) * other.getCoordinate(1));
    res.setCoordinate(1, this->getCoordinate(2) * other.getCoordinate(0) -
                         this->getCoordinate(0) * other.getCoordinate(2));
    res.setCoordinate(2, this->getCoordinate(0) * other.getCoordinate(1) -
                         this->getCoordinate(1) * other.getCoordinate(0));

    return res;
}

void Vector::print() {
    cout << "(";
    for (int i = 0; i < this->getN(); ++i) {
        cout << this->getCoordinate(i);
        if (i != this->getN() - 1) {
            cout << ", ";
        }
    }
    cout << ")";
}
