/*
 Done by Konovalenko Bohdan (statistics group 2)
 Header file for all needed union structures and functions
*/
#ifndef UNION_C_UNION_H
#define UNION_C_UNION_H
#include <stdio.h>
#include <math.h>

// union structure for the first task, define 4 coordinates which can be either descartes or polar
union PointCoordinate1 {
    struct {
        double coord1, coord2, coord3, coord4;
    };
};


/*
 function for the first task
 calculates the distance between two points, points can be in polar or descartes coordinates
*/
void firstTask(int, int);


// union structure for the second task, defines a double for hryvnas and penny or an integer for penny only
union Money {
    double hryvnasAndPenny;
    int penny;
};


/*
 function for the second task
 outputs amount of money a user inputs in hryvnas and penny and only in penny
*/
void secondTask(int, int);


/*
  union structure for the third task, defines two structures:
  Point - to input four coordinates (2 for every point) and VectorCoordinates - to input a vector with its coordinates
*/
union Vector {
    struct Point {
        double x1, y1, x2, y2;
    } point;
    struct VectorCoordinates {
        double firstCoordinate, secondCoordinate;
    } vectorCoordinates;
};


/*
 function for the third task
 outputs all three coordinates with given coordinates and either there are collinear or not
*/
void thirdTask(int);


// union structure for the fourth task, defines 4 coordinates which can be either descartes, polar or spherical
union PointCoordinate2 {
    struct DescartesPolar {
        double coord1, coord2, coord3, coord4;
    } descartesPolar;
    struct Spherical{
        double r1, r2, theta1, theta2, f1, f2;
    } spherical;
};


/*
 function for the fourth task
 calculates the distance between two points, points can be in polar, descartes coordinates or spherical
*/
void fourthTask(int, int);


/*
 union structure Figure for the fifth task, defines Square, Circle, Triangle, Rectangle and Trapezoid structures,
 every structure defines needed arguments to calculate perimeter and square of a figure
*/
union Figure {
    struct Square {
        double side;
    } square;
    struct Circle {
        double radius;
    } circle;
    struct Triangle {
        double side1, side2, side3;
    } triangle;
    struct Rectangle {
        double side1, side2;
    } rectangle;
    struct Trapezoid {
        double side1, side2, side3, side4, h;
    } trapezoid;
};


/*
 function for the fifth task
 calculates perimeter and square of a chosen figure
*/
void fifthTask(int, int);

#endif
