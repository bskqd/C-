#include <iostream>
#include <cstdlib>
using namespace std;

void split(const string myText, char delimeter){
    string temp_num;
    double array[myText.size()];
    int j = 0;
    for(string::size_type i = 0; i < myText.size(); i++) {
        if (myText[i + 1] == delimeter || i == myText.size() - 1) {
            temp_num += myText[i];
            array[j] = std::atof(temp_num.c_str());
            temp_num = "";
            i++;
            j++;
        } else {
            temp_num += myText[i];
        }
    }
    for (int i = 0; i < j; i++){
        cout << array[i] << "\n";
    }
}

int main() {
    string myText;
    string result;
    getline(cin, myText);
    split(myText, 'v');
}
