#ifndef TEST_VECTOR_H
#define TEST_VECTOR_H

#include<iostream>

using namespace std;

/**
 * default amount of coordinates = 3
 * */
class Vector {
private:
    int n{3};
    double *coordinates;
public:
    Vector(int n, int initialize) {
        this->n = n;
        this->coordinates = new double[n];
        if (initialize) {
            this->initArray();
        }
    }

    Vector(int n, double *coordinates) {
        this->n = n;
        this->coordinates = coordinates;
    }

    Vector() {
        this->coordinates = new double[n];
    }

    ~Vector() {
        delete coordinates;
    }

    Vector(Vector &v) {
        this->initArray(v.getN(), v.getCoordinates());
    }

    double scalarProduct(Vector other);

    Vector crossProduct(Vector other);

    void initArray();

    void initArray(int n, double *coordinates);

    void setCoordinate(int index, double el);

    int getN() const;

    void setN(int n);

    double *getCoordinates() const;

    double getCoordinate(int index);

    void setCoordinates(double *coordinates);

    void print();
};


#endif
