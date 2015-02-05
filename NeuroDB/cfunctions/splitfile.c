#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

// Compilar: gcc -Wall -03 -shared splitfiles.c -o splitfiles.so

int splitfile(int nchannels, char dtype[2], char input_file_name[20], char output_path[100])
/*Separates the trial files in files per channel.
      dtype: i2, i4
*/
{
    FILE **output_files;
    FILE *input_file;
    char nfile[3];
    char ch_header[9]={"channel_"};
    char base_name[109];
    char channel[112];
    int i;
    int16_t i16;
    int32_t i32;
    void* int_t;
    
    strcpy(base_name,output_path);
    strcat(base_name,"/");
    strcat(base_name,ch_header);
    
    if (!strcmp(dtype,"i2")) int_t = &i16;
    else if (!strcmp(dtype,"i4")) int_t = &i32;

    output_files = (FILE**)malloc(nchannels*(sizeof(FILE*)));
    for(i=0;i<nchannels;i++)
    {
        strcpy(channel,base_name);
        
        if (i < 10)
            sprintf(nfile,"00%d",i);
        else if ((i >= 10) && (i < 100))
            sprintf(nfile,"0%d",i);
        else sprintf(nfile,"%d",i);

        strcat(channel,nfile);
        output_files[i]=fopen(channel,"ab");
    }

    input_file = fopen(input_file_name,"rb");

    i=0;
    while(fread(int_t,sizeof(*int_t),1,input_file))
    {
        fwrite(int_t,sizeof(*int_t),1,output_files[i]);
        (i == (nchannels-1))? i=0 : i++;
    }


    for(i=0;i<nchannels;i++)
    {
        fclose(output_files[i]);
    }

    fclose(input_file);

    return 0;
}

