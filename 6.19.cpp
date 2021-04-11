#include <iostream>
using namespace std;


int main(){
    string text;
    getline(cin, text);
    string tmpWord;
    int all_words = 0, double_letters = 0;
    for(int i=0; i < (int)text.length(); i++){
        if(!isspace(text[i])){
            tmpWord += text[i];
        }
        else{
            for(int j=0; j < (int)tmpWord.length(); j++){
                if(tmpWord[j] != 'a' && tmpWord[j] != 'e' && tmpWord[j] != 'i' &&
                    tmpWord[j] != 'o' && tmpWord[j] != 'u' && tmpWord[j] != 'A' &&
                        tmpWord[j] != 'E' && tmpWord[j] != 'I' && tmpWord[j] != 'O' &&
                            tmpWord[j] != 'U' && bool(tmpWord[j] == tmpWord[j + 1]) == 1){
                    double_letters++;
                }
            }
            all_words++;
            tmpWord = "";
        }
    }
    cout << (double_letters / all_words) * 100;
}
