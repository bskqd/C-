#include <stdio.h>

#define N 100

int createDoubleFile(const char* fname, int * mas, int n){
    FILE * fp;
    fp = fopen(fname, "wb");
    if(fp==NULL){
        fprintf(stderr, "Error create file %s", fname);
        return -1;
    }
    int res = fwrite(mas, sizeof(int ), n, fp);
    fclose(fp);
    return res;
}

int readDoubleFile(const char* fname){
    FILE * fp;
    fp = fopen(fname, "rb");
    if(fp==NULL){
        fprintf(stderr, "Error create file %s", fname);
        return -1;
    }
    int x;
    int k = 0;
    int mas[N];
    while(!feof(fp)){
        int r = fread(&x, sizeof(int), 1, fp);
        if(r==0) break;
        if(x%2 == 0) {
            mas[k++] = x;
        }
    }
    fclose(fp);
    int f = createDoubleFile("1.dat", mas, k);
    printf("write %d ints", f);
    return k;
}

int main_fdsgfdhgmvgsnjgf(){
    int mas[N];
    int n;
    printf("n=");
    scanf("%d", &n);
    for(int i=0;i<n;++i){
        printf("a[%d]=",i);
        scanf("%d", &mas[i]);
    }
    char fname[20] = "1.dat";
    createDoubleFile(fname, mas, n);
    readDoubleFile(fname);
}
