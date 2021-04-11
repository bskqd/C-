#include <iostream>
#define N 100
using namespace std;


int main_афуіпкрвап(){
    string text;
    getline(cin, text);
    string tmpWord = "";
    string minWord = text;
    string array_of_strings[N];
    int j = 0;
    for(int i=0; i < (int)text.length(); i++){
        if(!isspace(text[i])){
            tmpWord += text[i];
        }
        else{
            if(tmpWord.length() < minWord.length()) {
                minWord = tmpWord;
            }
            tmpWord = "";
        }
    }
    if(tmpWord != ""){
        if(tmpWord.length() < minWord.length()) {
            minWord = tmpWord;
        }
    }
    for(int i=0; i < (int)text.length(); i++){
        if(!isspace(text[i])){
            tmpWord += text[i];
        }
        else{
            if(tmpWord.length() == minWord.length()){
                array_of_strings[j] = tmpWord;
                ++j;
            }
            tmpWord = "";
        }
    }
//  a)
    cout << array_of_strings[0];
//  b)
    cout << array_of_strings[j];
//  c)
    for(int i = 0; i <= j; i++){
        cout << array_of_strings[i] << "\n";
    }
}
