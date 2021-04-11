#include <iostream>
#include <string>
#include <cstdlib>


int main_14215125(){
    std::string num_1, num_2, num_3;
    std::cin >> num_1;
    std::cin >> num_2;
    std::cin >> num_3;
    double num1 = std::atof(num_1.c_str());
    double num2 = std::atof(num_2.c_str());
    double num3 = std::atof(num_3.c_str());
    double harmonic = 3 / ((1/num1) + (1/num2) + (1/num3)) ;
    std::cout << harmonic << std::endl;
    std::cout << harmonic << std::scientific;
}
