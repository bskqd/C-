#include "Vector.h"

#include<iostream>
#include <vector>
#include <fstream>

using namespace std;

Vector getVector(const string &filename) {
    vector<double> numbers;
    ifstream inputFile(filename);

    if (inputFile.good()) {
        int current_number = 0;
        while (inputFile >> current_number) {
            numbers.push_back(current_number);
        }

        inputFile.close();
    } else {
        cout << "Error!";
        _exit(0);
    }

    int n = numbers.size();

    auto *vectObj = new double[n];

    for (int i = 0; i < n; ++i) {
        vectObj[i] = numbers.at(i);
    }
    return {n, vectObj};
}
/*
int main() {
    Vector vect1;
    vect1 = getVector("vector1.txt");

    Vector vect2;
    vect2 = getVector("vector2.txt");

    Vector res1;
    res1 = vect1.crossProduct(vect2);
    cout << "Cross product: \n";
    res1.print();

    double res2 = vect1.scalarProduct(vect2);

    cout << "\nScalar product: " << res2;
}*/

