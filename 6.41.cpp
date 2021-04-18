// 6.0.41
#include <iostream>
#include <fstream>
#include <string>
using namespace std;

int main() {
    string text;
    string longestText;
    unsigned maxLength = 0;
    ifstream myReadFile("/home/bskqd/CLionProjects/study_f/filename4.txt");
    while(!myReadFile.eof())
    {
        getline(myReadFile,text);
        if(text.length() > maxLength) {
            maxLength = text.length();
            longestText = text;
        }
    }
    myReadFile.close();
    ofstream myWriteFile("/home/bskqd/CLionProjects/study_f/filename4_output.txt");
    myWriteFile << longestText;
    myWriteFile.close();
}
