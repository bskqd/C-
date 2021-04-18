// 6.0.37
#include <iostream>
#include <fstream>
#include <string>
using namespace std;

int main_fegrehtfyhm35t3r32fete() {
    string text;
    ifstream myReadFile("/home/bskqd/CLionProjects/study_f/filename4.txt");
    ofstream myWriteFile("/home/bskqd/CLionProjects/study_f/filename4_output.txt");
    while(!myReadFile.eof())
    // a)
    {
        getline(myReadFile,text);
        myWriteFile << text << endl;
    }
    // b)
    {
        getline(myReadFile,text);
        if(text.length() > 60) {
            myWriteFile << text << endl;
        }
    }
    myReadFile.close();
    myWriteFile.close();
}
