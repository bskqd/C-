// 4.0.4.14ав
#include <iostream>
#include <stdlib.h>

using namespace std;


typedef struct Person{
    int sex;
    int height;
} Person;

void input(Person* person){
    cout << "sex = ";
    cin >> person -> sex;
    if (person->sex > 1 || person->sex < 0){
        cout << "0 - male, 1 - female"<< endl;
        exit(EXIT_FAILURE);
    }
    cout << "height = ";
    cin >> person -> height;
}

int main() {
    int n;
    cout << "n = ";
    cin >> n;
    Person persons[n];
    for(int i = 0; i < n; i++){
        input(&persons[i]);
    }
    int heightSum = 0;
    int countFemales = 0;
    for (int i = 0; i < n; ++i) {
        if(persons[i].sex == 1) {
            heightSum += persons[i].height;
            ++countFemales;
        }
    }
    cout << "average female height = " << heightSum/countFemales << endl;

    int currentHeight = 0;
    for (int i = 0; i < n; ++i) {
        currentHeight = persons[i].height;
        for (int j = i + 1; j < n; ++j) {
            if(persons[j].height == currentHeight) {
                cout << "person " << i << " and person " << j << " have the same height" << endl;
                exit(EXIT_SUCCESS);
            }
        }
    }
    cout << "there are no people of the same height" << endl;
}
