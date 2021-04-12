//4.1.9

#include <stdio.h>

typedef struct {
    unsigned key;
    char date[10];
}T;

int append_struct(const char* fname){
    FILE *f1 = fopen(fname,"a+b");

    if(f1==NULL){
        printf("error file %s",fname);
        return -1;
    }

    unsigned n, key;
    char date[20];
    printf("Input n=");
    scanf("%u",&n);
    for (int i = 0; i < n; ++i) {
        T sr;
        printf("key=");
        scanf("%u",&key);

        printf("date:");
        scanf(" %s", date);
        sr.key = key;
        *sr.date = *date;
        fwrite(&sr,sizeof(sr),1,f1);
    }


    fclose(f1);

}

int search(const char* fname, unsigned search_key){
    FILE* fp = fopen(fname,"rb");
    if(fp==NULL) {
        fprintf(stderr, "Error open file %s",fname);
        return -1;
    }

    while(!feof(fp)){
        T x;
        fread(&x,sizeof(x), 1, fp);

        if(x.key==search_key){
            printf("under key %u is the information %s\n", x.key, x.date);
        }
    }

    fclose(fp);
    return 0;
}

int remove_struct(const char* fname, const char* fname1, unsigned rem_key){
    FILE* fp = fopen(fname,"rb");
    if(fp==NULL) {
        fprintf(stderr, "Error open file %s",fname);
        return -1;
    }
    remove(fname1);
    FILE *f1 = fopen(fname1,"wb");

    if(f1==NULL){
        printf("error file %s",fname1);
        return -1;
    }

    T x;
    while(!feof(fp)){

        fread(&x,sizeof(x), 1, fp);

        if(x.key==rem_key){ continue;}
        else{
            fwrite(&x,sizeof(x),1,f1);
        }
    }

    fclose(fp);
    fclose(f1);

    FILE* fp2 = fopen(fname1,"rb");
    if(fp==NULL) {
        fprintf(stderr, "Error open file %s",fname);
        return -1;
    }
    remove(fname);
    FILE *f3 = fopen(fname,"wb");

    if(f1==NULL){
        printf("error file %s",fname1);
        return -1;
    }

    T srt;
    while(!feof(fp)){

        fread(&srt,sizeof(x), 1, fp2);

        fwrite(&srt,sizeof(x),1,f3);
    }

    fclose(fp2);
    fclose(f3);

    return 0;
}

int main(){
    char* file= "date.dat";
    char* file1= "date_res.dat";
    append_struct(file);
    unsigned rem_key;
    printf("remove_key=");
    scanf("%u", &rem_key);
    remove_struct(file, file1, rem_key);
    unsigned search_key;
    printf("search_key=");
    scanf("%u",&search_key);
    search(file, search_key);
}