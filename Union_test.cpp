/*
 Done by Konovalenko Bohdan (statistics group 2)
 Test file with tests for all tasks
*/
#include <stdio.h>
#include "Union.h"

int main( ) {
    // fun_num - task number to be tested
    // option - variable to define the input method: 1 - terminal, 2 - test file
    int fun_num, option;
    printf("Choose a function to test:\n"
           "1 - calculate distance between two points in either descartes or polar coordinates\n"
           "2 - calculate amount of money in hryvnas and penny or only in penny\n"
           "3 - check if three vectors are collinear or not\n"
           "4 - calculate distance between two points in either descartes, polar or spherical coordinates\n"
           "5 - calculate perimeter and square of a chosen figure\n");
    scanf("%d", &fun_num);
    printf("1 - using terminal, 2 - using the test file: ");
    scanf("%d", &option);
    // test for the first task: calculate distance between two points in either descartes or polar coordinates
    if (fun_num == 1) {
        // coordinatesType - variable to define coordinates type: 1 - descartes, 2 - polar
        int coordinatesType;
        printf("1 - descartes coordinates, 2 - polar coordinates: ");
        scanf("%d", &coordinatesType);
        firstTask(option, coordinatesType);
    }
    // test for the second task: calculate amount of money in hryvnas and penny or only in penny
    else if (fun_num == 2) {
        // moneyType - variable to define money type: 1 - hryvnas and penny, 2 - penny only
        int moneyType;
        printf("1 - hryvnas and penny, 2 - penny only: ");
        scanf("%d", &moneyType);
        secondTask(option, moneyType);
    }
    // test for the third task: check if three vectors are collinear or not
    else if (fun_num == 3) {
        thirdTask(option);
    }
    // test for the fourth task: calculate distance between two points in either descartes, polar or spherical coordinates
    else if (fun_num == 4) {
        // coordinatesType - variable to define coordinates type: 1 - descartes, 2 - polar, 3 - spherical
        int coordinatesType;
        printf("1 - descartes coordinates, 2 - polar coordinates, 3 - spherical coordinates: ");
        scanf("%d", &coordinatesType);
        fourthTask(option, coordinatesType);
    }
    // test for the fifth task: calculate perimeter and square of a chosen figure
    else if (fun_num == 5) {
        // figureType - variable to define a figure type: 1 - square, 2 - circle, 3 - triangle, 4 - rectangle, 5 - trapezoid
        int figureType;
        printf("1 - square, 2 - circle, 3 - triangle, 4 - rectangle, 5 - trapezoid: ");
        scanf("%d", &figureType);
        fifthTask(option, figureType);
    }
}
