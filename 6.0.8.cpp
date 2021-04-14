#include <iostream>
#include <fstream>
#include <string>
#include <cstdlib>
#include <algorithm>
using namespace std;

int main() {
    string myText;
    string result;
    string result2;
    ifstream MyReadFile("/home/bskqd/CLionProjects/study_f/filename2.txt");
    while (getline (MyReadFile, myText)) {
        result += myText;
    }
    MyReadFile.close();
    string temp_num;
    int j = 0;
    for(string::size_type i = 0; i < result.size(); i++) {
        if (isspace(result[i + 1]) || i == result.size() - 1 ||
        result[i + 1] == ',' || result[i + 1] == '.' || result[i + 1] == '!' ||
            result[i + 1] == '?') {
            temp_num.push_back(result[i]);
            reverse(temp_num.begin(), temp_num.end());
            result2 += temp_num;
            if (i != result.size() - 1) {
                result2.push_back(result[i + 1]);
            }
            temp_num = "";
            i++;
            j++;
        } else {
            temp_num.push_back(result[i]);
        }
    }
    cout << result2;
}
