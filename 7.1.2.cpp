#include <iostream>
#include <cmath>

using namespace std;

struct Point{
    double x, y;
    static int counter;

    void input(){
        cout << "x, y: ";
        cin >> x >> y;
        counter++;
    }

    static int getCount(){
        return counter;
    }
};

int Point::counter = 0;

double dist(Point p1, Point p2){
    double distance;
    distance = pow((p2.x - p1.x) * (p2.x - p1.x) + (p2.y - p1.y) * (p2.y - p1.y), 0.5);
    return distance;
}

int main_defrshdtwehwet21432(){
    string answer;
    Point p_prev;
    double d1 = 0;
    do {
        cout << "Continue enter points?y/n";
        cin >> answer;
        if(answer.length()>=1 && tolower(answer[0])=='y'){
            Point p;
            p.input();
            if(p.counter>1){
                d1 += dist(p, p_prev);
            }
            p_prev = p;
        } else{
            break;
        }
    } while (true);
    cout<<"points: "<<Point::getCount()<<endl;
    cout<<"perimeter: "<<d1;
}
