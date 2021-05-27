/*
 Done by Konovalenko Bohdan (statistics group 2)
 Header file for all needed union structures and functions
*/
#ifndef UNION_CPP_UNION_H
#define UNION_CPP_UNION_H


// structure for the first task, define 4 coordinates which can be either descartes or polar
struct Point{
    double coord1, coord2, coord3, coord4;
};


/*
 function for the first task
 calculates the distance between two points, points can be in polar or descartes coordinates
*/
void firstTask(int, int);


/*
 function for the second task
 outputs amount of money a user inputs in hryvnas and penny and only in penny
*/
void secondTask(int, int);

#endif
