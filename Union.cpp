/*
 Done by Konovalenko Bohdan (statistics group 2)
 Implementation of all needed functions
*/
#include <iostream>
#include <cmath>
#include <string>
#include <variant>
#include <fstream>
#include "Union.h"
// max array size, used in numbers() to define an array
#define MAX_INT_FOR_NUMBERS 4
using namespace std;


/*
 function that gets a char*line and returns an array of variables needed for a function,
 casts every number from the line to a double and adds it to the array,
 used when the input method is from the test file
*/
double * numbers(string line) {
    unsigned numbersCount = 0, last_word = 0;
    static double numbers[MAX_INT_FOR_NUMBERS];
    string delimiter = " ";
    string token;
    auto start = 0U;
    auto end = line.find(delimiter);
    while (last_word != 2){
        token = line.substr(start, end - start);
        numbers[numbersCount] = stod(token);
        numbersCount++;
        start = end + delimiter.length();
        end = line.find(delimiter, start);
        if (end == string::npos) {
            last_word++;
        }
    }
    return numbers;
}

/*
 function that gets an int - line from the test file to get test data,
 starts with 0, so the first line in the test file is 0,
 returns needed line, the result passes to numbers() to define variables
 used when the input method is from the test file
*/
string getLine(int lineNumber) {
    int count = 0;
    string line;
    ifstream reader("/home/bskqd/CLionProjects/Union_CPP/Union_test.txt");
    while(getline(reader, line)) {
        if (count == lineNumber)
            return line;
        count++;
    }
}

/*
 implementation of function for the first task
 takes two int arguments to define the input method (console, text file) and coordinatesType (descartes, polar),
 distance is calculated depending on coordinatesType, result is printed to the console and written to the output file
*/
void firstTask(int option, int coordinatesType) {
    Point point_var;
    variant<Point> var_point;
    var_point = point_var;
    Point p2 = std::get<Point>(var_point);
    double distance;
    if (option == 1) {
        printf("Input first coordinate (x1 | r1): ");
        scanf("%lf", &p2.coord1);
        printf("Input second coordinate (y1 | theta1): ");
        scanf("%lf", &p2.coord2);
        printf("Input third coordinate (x2 | r2): ");
        scanf("%lf", &p2.coord3);
        printf("Input fourth coordinate (y2 | theta2): ");
        scanf("%lf", &p2.coord4);
    }
    else if (option == 2) {
        double * coordinates = numbers(getLine(0));
        p2.coord1 = coordinates[0];
        p2.coord2 = coordinates[1];
        p2.coord3 = coordinates[2];
        p2.coord4 = coordinates[3];
    }
    if (coordinatesType == 1) {
        double x1 = p2.coord1, y1 = p2.coord2, x2 = p2.coord3, y2 = p2.coord4;
        // calculate the distance in descartes coordinates
        distance = sqrt((y2 - y1) * (y2 - y1) + (x2 - x1) * (x2 - x1));
    }
    else if (coordinatesType == 2) {
        double r1 = p2.coord1, theta1 = p2.coord2, r2 = p2.coord3, theta2 = p2.coord4;
        // calculate the distance in polar coordinates
        distance = sqrt(r1*r1 + r2*r2 - 2*r1*r2*cos(theta2 - theta1));
    }
    // open the output file for writing, print the distance to the console and write it to the output file
    ofstream outputFile;
    outputFile.open("/home/bskqd/CLionProjects/Union_CPP/Union_output_result.txt");
    cout << "distance = " << distance << endl;
    outputFile << "distance = " << distance;
    outputFile.close();
}


/*
 implementation of function for the second task
 takes two int arguments to define the input method (console, text file) and moneyType (hryvnas and penny, penny only),
 function returns amount of money only in penny and in hryvnas and penny,
 result is printed to the console and written to the output file
*/
void secondTask(int option, int moneyType) {
    variant<int, double> money;
    int penny;
    double hryvnasAndPenny;
    if (option == 1 && moneyType == 1) {
        cout << "Input hryvnas and penny (double): ";
        cin >> hryvnasAndPenny;
        money = hryvnasAndPenny;
    }
    else if (option == 1 && moneyType == 2) {
        cout << "Input penny (integer): ";
        cin >> penny;
        money = penny;
    }
    else if (option == 2 && moneyType == 1) {
        double * amount = numbers(getLine(1));
        money = amount[0];
    }
    else if (option == 2 && moneyType == 2) {
        double * penny = numbers(getLine(2));
        money = (int)penny[0];
    }
    if (moneyType == 1) {
        penny = (int)(get<double>(money) * 100);
        hryvnasAndPenny = get<double>(money);
    }
    else if (moneyType == 2) {
        hryvnasAndPenny = get<int>(money) / 100.0;
        penny = get<int>(money);
    }
    /*
      open the output file for writing, print the amount of money in hryvnas and penny and only in penny
      to the console and write it to the output file
    */
    ofstream outputFile;
    outputFile.open("/home/bskqd/CLionProjects/Union_CPP/Union_output_result.txt");
    cout << "in hryvnas and penny = " << hryvnasAndPenny << " in penny = " << penny << endl;
    outputFile << "in hryvnas and penny = " << hryvnasAndPenny << " in penny = " << penny;
    outputFile.close();
}
