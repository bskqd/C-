/*
 Done by Konovalenko Bohdan (statistics group 2)
 Implementation of all needed functions
*/
#include <stdio.h>
#include <math.h>
#include <string.h>
#include "Union.h"
// max array size, used in numbers() to define an array
#define MAX_INT_FOR_NUMBERS 6

/*
 function that gets a char*line and returns an array of variables needed for a function,
 casts every number from the line to a double and adds it to the array,
 used when the input method is from the test file
*/
double * numbers(char * line) {
    char * token = strtok(line, " ");
    int numbersCount = 0;
    static double numbers[MAX_INT_FOR_NUMBERS];
    while(token != NULL) {
        sscanf(token, "%lf", &numbers[numbersCount]);
        token = strtok(NULL, " ");
        numbersCount++;
    }
    return numbers;
}

/*
 function that gets an int - line from the test file to get test data,
 starts with 0, so the first line in the test file is 0,
 returns needed line, the result passes to numbers() to define variables
 used when the input method is from the test file
*/
char * getLine(int lineNumber) {
    int count = 0;
    static const char filename[] = "/home/bskqd/CLionProjects/Union_C/Union_test.txt";
    FILE *file = fopen(filename, "r");
    if ( file != NULL ) {
        static char line[256];
        while (fgets(line, sizeof line, file) != NULL) {
            if (count == lineNumber) {
                fclose(file);
                return line;
            }
            else {
                count++;
            }
        }
        fclose(file);
    }
}

/*
 implementation of function for the first task
 takes two int arguments to define the input method (console, text file) and coordinatesType (descartes, polar),
 distance is calculated depending on coordinatesType, result is printed to the console and written to the output file
*/
void firstTask(int option, int coordinatesType) {
    PointCoordinate1 point;
    double distance;
    if (option == 1) {
        printf("Input first coordinate (x1 | r1): ");
        scanf("%lf", &point.coord1);
        printf("Input second coordinate (y1 | theta1): ");
        scanf("%lf", &point.coord2);
        printf("Input third coordinate (x2 | r2): ");
        scanf("%lf", &point.coord3);
        printf("Input fourth coordinate (y2 | theta2): ");
        scanf("%lf", &point.coord4);
    }
    else if (option == 2) {
        double * coordinates = numbers(getLine(0));
        point.coord1 = coordinates[0];
        point.coord2 = coordinates[1];
        point.coord3 = coordinates[2];
        point.coord4 = coordinates[3];
    }
    if (coordinatesType == 1) {
        double x1 = point.coord1, y1 = point.coord2, x2 = point.coord3, y2 = point.coord4;
        // calculate the distance in descartes coordinates
        distance = sqrt((y2 - y1) * (y2 - y1) + (x2 - x1) * (x2 - x1));
    }
    else if (coordinatesType == 2) {
        double r1 = point.coord1, theta1 = point.coord2, r2 = point.coord3, theta2 = point.coord4;
        // calculate the distance in polar coordinates
        distance = sqrt(r1*r1 + r2*r2 - 2*r1*r2*cos(theta2 - theta1));
    }
    // open the output file for writing, print the distance to the console and write it to the output file
    FILE * fp = fopen("/home/bskqd/CLionProjects/Union_C/Union_output_result.txt", "w");
    printf("distance = %lf", distance);
    fprintf(fp, "distance = %lf", distance);
}


/*
 implementation of function for the second task
 takes two int arguments to define the input method (console, text file) and moneyType (hryvnas and penny, penny only),
 function returns amount of money only in penny and in hryvnas and penny,
 result is printed to the console and written to the output file
*/
void secondTask(int option, int moneyType) {
    Money money;
    double hryvnasAndPenny;
    int penny;
    if (option == 1 && moneyType == 1) {
        printf("Input hryvnas and penny (double): ");
        scanf("%lf", &money.hryvnasAndPenny);
    }
    else if (option == 1 && moneyType == 2) {
        printf("Input penny (integer): ");
        scanf("%d", &money.penny);
    }
    else if (option == 2 && moneyType == 1) {
        double * amount = numbers(getLine(1));
        money.hryvnasAndPenny = amount[0];
    }
    else if (option == 2 && moneyType == 2) {
        double * penny = numbers(getLine(2));
        money.penny = (int)penny[0];
    }
    if (moneyType == 1) {
        penny = (int)(money.hryvnasAndPenny * 100);
        hryvnasAndPenny = money.hryvnasAndPenny;
    }
    else if (moneyType == 2) {
        hryvnasAndPenny = money.penny / 100.0;
        penny = money.penny;
    }
    /*
      open the output file for writing, print the amount of money in hryvnas and penny and only in penny
      to the console and write it to the output file
    */
    FILE * fp = fopen("/home/bskqd/CLionProjects/Union_C/Union_output_result.txt", "w");
    printf("in hryvnas and penny = %lf, in penny = %d", hryvnasAndPenny, penny);
    fprintf(fp, "in hryvnas and penny = %lf, in penny = %d", hryvnasAndPenny, penny);
}


/*
 implementation of function for the fifth task
 takes one int argument to define the input method (console, text file),
 then there's a choice to input every vector using two points with their coordinates or using the vector coordinates,
 when all vectors are defined, function answers a question: this three vectors are collinear or not,
 result is printed to the console and written to the output file
*/
void thirdTask(int option) {
    unsigned vectors = 0;
    Vector v1, v2, v3;
    while (vectors != 3) {
        // define a vector to input coordinates
        Vector vector;
        // variable for the input type: 1 - using two points, 2 - using vector coordinates
        unsigned inputType;
        printf("Select how to input a vector: 1 - using two points, 2 - using vector coordinates: ");
        scanf("%u", &inputType);
        /*
          based on input type (1 - using two points, 2 - using vector coordinates) and option of input (1 - using terminal,
          2 - using the test file) user inputs a vector
        */
        if (option == 1 && inputType == 1) {
            printf("Input x1: ");
            scanf("%lf", &vector.point.x1);
            printf("Input y1: ");
            scanf("%lf", &vector.point.y1);
            printf("Input x2: ");
            scanf("%lf", &vector.point.x2);
            printf("Input y2: ");
            scanf("%lf", &vector.point.y2);
            // if input type is using two points - vector coordinates are being calculated and written to the VectorCoordinates structure
            vector.vectorCoordinates.firstCoordinate = vector.point.x2 - vector.point.x1;
            vector.vectorCoordinates.secondCoordinate = vector.point.y2 - vector.point.y1;
        }
        else if (option == 1 && inputType == 2) {
            printf("Input the first coordinate: ");
            scanf("%lf", &vector.vectorCoordinates.firstCoordinate);
            printf("Input the second coordinate: ");
            scanf("%lf", &vector.vectorCoordinates.secondCoordinate);
        }
        else if (option == 2 && inputType == 1) {
            double * points = numbers(getLine(0));
            vector.point.x1 = points[0];
            vector.point.y1 = points[1];
            vector.point.x2 = points[2];
            vector.point.y2 = points[3];
            // if input type is using two points - vector coordinates are being calculated and written to the VectorCoordinates structure
            vector.vectorCoordinates.firstCoordinate = vector.point.x2 - vector.point.x1;
            vector.vectorCoordinates.secondCoordinate = vector.point.y2 - vector.point.y1;
        }
        else if (option == 2 && inputType == 2) {
            double * coordinates = numbers(getLine(6));
            vector.vectorCoordinates.firstCoordinate = coordinates[0];
            vector.vectorCoordinates.secondCoordinate = coordinates[1];
        }
        // based on iteration count, vector coordinates are written to needed vector (v1, v2 or v3)
        if (vectors == 0) {
            v1.vectorCoordinates.firstCoordinate = vector.vectorCoordinates.firstCoordinate;
            v1.vectorCoordinates.secondCoordinate = vector.vectorCoordinates.secondCoordinate;
        }
        else if (vectors == 1) {
            v2.vectorCoordinates.firstCoordinate = vector.vectorCoordinates.firstCoordinate;
            v2.vectorCoordinates.secondCoordinate = vector.vectorCoordinates.secondCoordinate;
        }
        else if (vectors == 2) {
            v3.vectorCoordinates.firstCoordinate = vector.vectorCoordinates.firstCoordinate;
            v3.vectorCoordinates.secondCoordinate = vector.vectorCoordinates.secondCoordinate;
        }
        vectors += 1;
    };
    // check if three vectors are collinear or not
    bool collinear = true;
    if (v1.vectorCoordinates.firstCoordinate/v2.vectorCoordinates.firstCoordinate !=
    v1.vectorCoordinates.secondCoordinate/v2.vectorCoordinates.secondCoordinate ||
    v2.vectorCoordinates.firstCoordinate/v3.vectorCoordinates.firstCoordinate !=
    v2.vectorCoordinates.secondCoordinate/v3.vectorCoordinates.secondCoordinate
    ) {
        collinear = false;
    }
    /*
      open the output file for writing, print coordinates of all three vectors and either they collinear or not
      to the console and write it to the output file
    */
    FILE *fp = fopen("/home/bskqd/CLionProjects/Union_C/Union_output_result.txt", "w");
    printf("V1: first coordinate: %lf, second coordinate: %lf\n"
           "V2: first coordinate: %lf, second coordinate: %lf\n"
           "V3: first coordinate: %lf, second coordinate: %lf\n"
           "collinear: %s",
           v1.vectorCoordinates.firstCoordinate, v1.vectorCoordinates.secondCoordinate,
           v2.vectorCoordinates.firstCoordinate, v2.vectorCoordinates.secondCoordinate,
           v3.vectorCoordinates.firstCoordinate, v3.vectorCoordinates.secondCoordinate,
           collinear ? "true" : "false");
    fprintf(fp, "V1: first coordinate: %lf, second coordinate: %lf\n"
                "V2: first coordinate: %lf, second coordinate: %lf\n"
                "V3: first coordinate: %lf, second coordinate: %lf\n"
                "collinear: %s",
                v1.vectorCoordinates.firstCoordinate, v1.vectorCoordinates.secondCoordinate,
                v2.vectorCoordinates.firstCoordinate, v2.vectorCoordinates.secondCoordinate,
                v3.vectorCoordinates.firstCoordinate, v3.vectorCoordinates.secondCoordinate,
                collinear ? "true" : "false");
}


/*
 implementation of function for the fourth task
 takes two int arguments to define the input method (console, text file) and coordinatesType (descartes, polar, spherical),
 distance is calculated depending on coordinatesType, result is printed to the console and written to the output file
*/
void fourthTask(int option, int coordinatesType) {
    PointCoordinate2 point;
    double distance;
    // if chosen coordinates are descartes or polar, use PointCoordinate2.descartesPolar struct
    if (coordinatesType == 1 || coordinatesType == 2) {
        if (option == 1) {
            printf("Input first coordinate (x1 | r1): ");
            scanf("%lf", &point.descartesPolar.coord1);
            printf("Input second coordinate (y1 | theta1): ");
            scanf("%lf", &point.descartesPolar.coord2);
            printf("Input third coordinate (x2 | r2): ");
            scanf("%lf", &point.descartesPolar.coord3);
            printf("Input fourth coordinate (y2 | theta2): ");
            scanf("%lf", &point.descartesPolar.coord4);
        } else if (option == 2) {
            double *coordinates = numbers(getLine(0));
            point.descartesPolar.coord1 = coordinates[0];
            point.descartesPolar.coord2 = coordinates[1];
            point.descartesPolar.coord3 = coordinates[2];
            point.descartesPolar.coord4 = coordinates[3];
        }
        if (coordinatesType == 1) {
            double x1 = point.descartesPolar.coord1, y1 = point.descartesPolar.coord2,
            x2 = point.descartesPolar.coord3, y2 = point.descartesPolar.coord4;
            // calculate the distance in descartes coordinates
            distance = sqrt((y2 - y1) * (y2 - y1) + (x2 - x1) * (x2 - x1));
        }
        else if (coordinatesType == 2) {
            double r1 = point.descartesPolar.coord1, theta1 = point.descartesPolar.coord2,
            r2 = point.descartesPolar.coord3, theta2 = point.descartesPolar.coord4;
            // calculate the distance in polar coordinates
            distance = sqrt(r1*r1 + r2*r2 - 2*r1*r2*cos(theta2 - theta1));
        }
    }
    // if chosen coordinates are spherical, use PointCoordinate2.spherical struct
    else if (coordinatesType == 3){
        if (option == 1) {
            printf("Input r1: ");
            scanf("%lf", &point.spherical.r1);
            printf("Input theta1: ");
            scanf("%lf", &point.spherical.theta1);
            printf("Input f1: ");
            scanf("%lf", &point.spherical.f1);
            printf("Input r2: ");
            scanf("%lf", &point.spherical.r2);
            printf("Input theta2: ");
            scanf("%lf", &point.spherical.theta2);
            printf("Input f2: ");
            scanf("%lf", &point.spherical.f2);
        } else if (option == 2) {
            double *coordinates = numbers(getLine(0));
            point.spherical.r1 = coordinates[0];
            point.spherical.theta1 = coordinates[1];
            point.spherical.f1 = coordinates[2];
            point.spherical.r2 = coordinates[3];
            point.spherical.theta2 = coordinates[4];
            point.spherical.f2 = coordinates[5];
        }
        // calculate the distance in spherical coordinates
        double r1 = point.spherical.r1, theta1 = point.spherical.theta1, f1 = point.spherical.f1,
        r2 = point.spherical.r2, theta2 = point.spherical.theta2, f2 = point.spherical.f2;
        distance = sqrt(r1*r1 + r2*r2 - 2*r1*r2*(sin(theta1)*sin(theta2)*cos(f1 - f2) + cos(theta1)*cos(theta2)));
    }
    // open the output file for writing, print the distance to the console and write it to the output file
    FILE *fp = fopen("/home/bskqd/CLionProjects/Union_C/Union_output_result.txt", "w");
    printf("distance = %lf", distance);
    fprintf(fp, "distance = %lf", distance);
}


/*
 implementation of function for the fifth task
 takes two int arguments to define the input method (console, text file) and figureType (Square, Circle, Triangle, Rectangle, Trapezoid),
 calculates perimeter and square of chosen figure, result is printed to the console and written to the output file
*/
void fifthTask (int option, int figureType) {
    Figure figure;
    double perimeter, square;
    if (figureType == 1) {
        if (option == 1) {
            printf("Input a square side: ");
            scanf("%lf", &figure.square.side);
        }
        else if (option == 2) {
            double *side = numbers(getLine(4));
            figure.square.side = side[0];
        }
        double side = figure.square.side;
        // calculating Square perimeter and square
        perimeter = 4 * side;
        square = side * side;
    }
    else if (figureType == 2) {
        if (option == 1) {
            printf("Input a circle radius: ");
            scanf("%lf", &figure.circle.radius);
        }
        else if (option == 2) {
            double *side = numbers(getLine(4));
            figure.circle.radius = side[0];
        }
        double radius = figure.circle.radius;
        // calculating Circle length and square
        perimeter = 2 * radius * M_PI;
        square = M_PI * radius * radius;
    }
    else if (figureType == 3) {
        if (option == 1) {
            printf("Input first side: ");
            scanf("%lf", &figure.triangle.side1);
            printf("Input second side: ");
            scanf("%lf", &figure.triangle.side2);
            printf("Input third side: ");
            scanf("%lf", &figure.triangle.side3);
        }
        else if (option == 2) {
            double *triangleSides = numbers(getLine(5));
            figure.triangle.side1 = triangleSides[0];
            figure.triangle.side2 = triangleSides[1];
            figure.triangle.side3 = triangleSides[2];
        }
        double side1 = figure.triangle.side1, side2 = figure.triangle.side2, side3 = figure.triangle.side3;
        // calculating Triangle perimeter
        perimeter = side1 + side2 + side3;
        // calculating Triangle square using Heron's Formula
        double semiPerimeter = perimeter / 2;
        square = sqrt(semiPerimeter * (semiPerimeter - side1) * (semiPerimeter - side2) * (semiPerimeter - side3));
    }
    else if (figureType == 4) {
        if (option == 1) {
            printf("Input side1: ");
            scanf("%lf", &figure.rectangle.side1);
            printf("Input side2: ");
            scanf("%lf", &figure.rectangle.side2);
        }
        else if (option == 2) {
            double *rectangleSides = numbers(getLine(6));
            figure.rectangle.side1 = rectangleSides[0];
            figure.rectangle.side2 = rectangleSides[1];
        }
        double side1 = figure.rectangle.side1, side2 = figure.rectangle.side2;
        // calculating Rectangle perimeter and square
        perimeter = 2*side1 + 2*side2;
        square = side1 * side2;
    }
    else if (figureType == 5) {
        if (option == 1) {
            printf("Input first side: ");
            scanf("%lf", &figure.trapezoid.side1);
            printf("Input second side: ");
            scanf("%lf", &figure.trapezoid.side2);
            printf("Input third side: ");
            scanf("%lf", &figure.trapezoid.side3);
            printf("Input fourth side: ");
            scanf("%lf", &figure.trapezoid.side4);
            printf("Input height: ");
            scanf("%lf", &figure.trapezoid.h);
        }
        else if (option == 2) {
            double *trapezoidSides = numbers(getLine(7));
            figure.trapezoid.side1 = trapezoidSides[0];
            figure.trapezoid.side2 = trapezoidSides[1];
            figure.trapezoid.side3 = trapezoidSides[2];
            figure.trapezoid.side4 = trapezoidSides[3];
            figure.trapezoid.h = trapezoidSides[4];
        }
        double side1 = figure.trapezoid.side1, side2 = figure.trapezoid.side2,
        side3 = figure.trapezoid.side3, side4 = figure.trapezoid.side4, height = figure.trapezoid.h;
        // calculating Trapezoid perimeter and square
        perimeter = side1 + side2 + side3 + side4;
        square = (side1 * side2)/2 * height;
    }
    /*
      open the output file for writing, print the perimeter and square of chosen figure
      to the console and write it to the output file
    */
    FILE *fp = fopen("/home/bskqd/CLionProjects/Union_C/Union_output_result.txt", "w");
    printf("perimeter = %lf, square = %lf", perimeter, square);
    fprintf(fp, "perimeter = %lf, square = %lf", perimeter, square);
}
