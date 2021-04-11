#include <iostream>
#include <fstream>
#include <cstdlib>
using namespace std;

int main_fdsgfdhgf2134() {
    string myText;
    string result;
    ifstream MyReadFile("/home/bskqd/CLionProjects/study_f/filename.txt");
    while (getline (MyReadFile, myText)) {
        result += myText;
    }
    MyReadFile.close();
    string temp_num;
    double array[result.size()];
    int j = 0;
    for(string::size_type i = 0; i < result.size(); i++) {
        if (isspace(result[i + 1]) || i == result.size() - 1) {
            temp_num += result[i];
            array[j] = std::atof(temp_num.c_str());
            temp_num = "";
            i++;
            j++;
        } else {
            temp_num += result[i];
        }
    }
    double max = array[0];
    for (int i = 0; i < j; i++){
        if (array[i] > max){
            max = array[i];
        }
    }
    cout << max;
}