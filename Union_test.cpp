/*
 Done by Konovalenko Bohdan (statistics group 2)
 Test file with tests for all tasks
*/
#include <iostream>
#include "Union.h"

using namespace std;

int main( ) {
    // fun_num - task number to be tested
    // option - variable to define the input method: 1 - terminal, 2 - test file
    int fun_num, option;
    cout << "Choose a function to test:\n"
           "1 - calculate distance between two points in either descartes or polar coordinates\n"
           "2 - calculate amount of money in hryvnas and penny or only in penny" << endl;
    cin >> fun_num;
    printf("1 - using terminal, 2 - using the test file: ");
    cin >> option;
    // test for the first task: calculate distance between two points in either descartes or polar coordinates
    if (fun_num == 1) {
        // coordinatesType - variable to define coordinates type: 1 - descartes, 2 - polar
        int coordinatesType;
        cout << "1 - descartes coordinates, 2 - polar coordinates: " << endl;
        cin >> coordinatesType;
        firstTask(option, coordinatesType);
    }
    // test for the second task: calculate amount of money in hryvnas and penny or only in penny
    else if (fun_num == 2) {
        // moneyType - variable to define money type: 1 - hryvnas and penny, 2 - penny only
        int moneyType;
        cout << "1 - hryvnas and penny, 2 - penny only: " << endl;
        cin >> moneyType;
        secondTask(option, moneyType);
    }
}
