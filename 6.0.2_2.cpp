#include<iostream>
#include <cctype>


using namespace std;

string f(string& s){
    string res = "";
    for(string::size_type i = 0; i < s.size(); i++) {
        if (isspace(s[i + 1]) || i == s.size() - 1) {
        } else {
            res += s[i];
        }
    }
    return res;
}

int main() {
    string s;
    getline(cin, s);
    cout << f(s);
}
