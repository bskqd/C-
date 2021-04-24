#include <iostream>
#include <fstream>
#include <string>
using namespace std;

class Book {
public:
    string name;
    string author;
    int pages, year;

    void input(unsigned numberOfBooks);
    void output(const Book&);

    void find_by_author(string author);
};

void Book::input(unsigned numberOfBooks) {
    ofstream file_obj;

    file_obj.open("/home/bskqd/CLionProjects/study_f/books.txt", ios::app);
    for (int i = 0; i < numberOfBooks; i++) {
        Book obj;

        cout<<"name: ";
        cin>>obj.name;
        cout<<"author: ";
        cin>>obj.author;
        cout<<"pages: ";
        cin>>obj.pages;
        cout<<"year: ";
        cin>>obj.year;

        file_obj.write((char*)&obj, sizeof(obj));
    }
}


void Book::output(const Book& book) {
    cout<<"name: "<<book.name<<endl;
    cout<<"author: "<<book.author<<endl;
    cout<<"pages: "<<book.pages<<endl;
    cout<<"year: "<<book.year<<endl;
}


void Book::find_by_author(string author) {
    ifstream file_obj;

    file_obj.open("/home/bskqd/CLionProjects/study_f/books.txt", ios::in);

    Book obj;

    while (!file_obj.eof()) {
        file_obj.read((char*)&obj, sizeof(obj));
        if (obj.author == author) {
            obj.output(obj);
            break;
        }
    }
}

int main() {
    unsigned numberOfBooks;
    cin>>numberOfBooks;
    Book object;
    object.input(numberOfBooks);

    string author;
    cout<<"find by author, input author:";
    cin>>author;
    object.find_by_author(author);

    return 0;
}
