//compiling with : gcc -fPIC -o cfsfdp.so -shared cfsfdp.c -I/usr/include/pgsql -L/usr/lib/postgresql92/lib64 -lpq
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <libpq-fe.h>
#include <math.h>
#include <ctype.h>


int compare(const void *_a, const void *_b) {
    int *a, *b;

    a = (int *) _a;
    b = (int *) _b;

    return (*a - *b);
}

int pivot(double *array, double *index, int left, int right)
{
    int i;
    int pivote;
    double pivot_value;
    double aux;
    double aux2;

    pivote = left;
    pivot_value = array[pivote];
    for (i=left+1; i<=right; i++){
        if (array[i] > pivot_value){
                pivote++;
                aux=array[i];
                aux2=index[i];
                array[i]=array[pivote];
                index[i]=index[pivote];
                array[pivote]=aux;
                index[pivote]=aux2;

        }
    }
    aux=array[left];
    aux2=index[left];
    array[left]=array[pivote];
    index[left]=index[pivote];
    array[pivote]=aux;
    index[pivote]=aux2;
    return pivote;
}

void Quicksort(double *array, double *index, int left, int right)
{
     int pivote;
     if(left < right){
        pivote=pivot(array, index, left, right);
        Quicksort(array, index, left, pivote-1);
        Quicksort(array, index, pivote+1, right);
     }
}


double mean(double *array, int n)
{
    int i;
    double acum = 0;
    for(i=0; i<n; i++)
    {
        acum = acum + array[i];
    }
    return acum/n;
}

char* build_query2(double* spikeFeaturesId, int nspikes, int points)
{
    char *query = (char*)malloc(sizeof(char)*20*nspikes);
    char aux[25];
    int i;

    strcpy(query, "SELECT id_spike, ");

    for(i=1; i<points+1; i++)
    {
        sprintf(aux, "p%d, ", i);
        strcat(query, aux);
    }

    query[strlen(query)-2] = ' ';
    query[strlen(query)-1] = '\0';

    strcat(query, ",id from FEATURES where "); //La query no devuelve los registros con el orden de id especificado

    for(i=0; i<nspikes; i++)
    {
        sprintf(aux, "id = %d or ", (int)spikeFeaturesId[i]);
        strcat(query, aux);
    }
    query[strlen(query)-4] = '\0';

    query = realloc(query, sizeof(char)*(strlen(query)+1));

    return query;
}

char* build_query(double* id_spike, int nspikes, int points)
{
    char *query = (char*)malloc(sizeof(char)*17*nspikes);
    char aux[25];
    int i;

    strcpy(query, "SELECT id, ");

    for(i=1; i<points+1; i++)
    {
        sprintf(aux, "p%d, ", i);
        strcat(query, aux);
    }

    query[strlen(query)-2] = ' ';
    query[strlen(query)-1] = '\0';

    strcat(query, "from SPIKE where ");

    for(i=0; i<nspikes; i++)
    {
        sprintf(aux, "id = %d or ", (int)id_spike[i]);
        strcat(query, aux);
    }
    query[strlen(query)-4] = '\0';

    query = realloc(query, sizeof(char)*(strlen(query)+1));

    return query;
}

double* cp_vector(double* vector, int n)
{
    int i;
    double* copy = (double*)calloc(n,sizeof(double));
    for(i=0; i<n; i++)
    {
        copy[i] = vector[i];
    }

    return copy;
}

double argmaxvector(double* rho, int n)
{
    int i;
    int argmax = 0;
    double max = rho[argmax];
    for(i=1; i<n; i++)
    {
        if (max<rho[i])
        {
            argmax=i;
            max = rho[i];
        }
    }

    return argmax;
}

double argminvector(double* rho, int n)
{
    int i;
    int argmin = 0;
    double min = rho[argmin];
    for(i=1; i<n; i++)
    {
        if (min>rho[i])
        {
            argmin=i;
            min = rho[i];
        }
    }

    return argmin;
}

void least_squares(double *x,double *y,int n, double *m, double *b, double *sd)
{
    double k=0,t=0,w=0,k2=0;
    int i;
    double *x1 = x;
    double *y1 = y;
    double sumerr = 0;
    //Efectuando las respectivas sumas y productos requeridos en la ecuacion
    for(i=0; i<n; i++,x1++,y1++)
    {
        k+=*x1;
        t+=*y1;
        w+= (*x1)*(*y1);
        k2+=(*x1)*(*x1);
    }
    //Resolviendo la ecuacion de la Pendiente ajustada a minimos cuadrados
    *m=(n*w-k*t)/(n*k2-k*k);

    k=0,t=0,w=0,k2=0;
    x1 = x;
    y1 = y;
    //Efectuando las respectivas sumas y productos requeridos en la ecuacion
    for(i=0; i<n; i++,x1++,y1++)
    {
        k+=*x1;
        t+=*y1;
        w+= (*x1)*(*y1);
        k2+=(*x1)*(*x1);
    }
//Resolviendo la ecuacion para hallar el punto de corte por minimos cuadrados
    *b=(t*k2-k*w)/(n*k2-k*k);

    y1 = y;
    x1 = x;
    for(i=0; i<n; i++,x1++,y1++)
    {
        sumerr = sumerr + pow(*y1 - (*m*(*x1)+*b), 2);
    }

    *sd = sqrt(sumerr / (float)n);
}

float get_distance(float x1[], float x2[], int n)
{
    int i;
    double tmp = 0;
    for(i=0; i<n; i++)
    {
        tmp = tmp + pow(x1[i] - x2[i], 2);
    }
    return pow(tmp, 0.5);
}

float get_distance_from_res(PGresult *res, int i, int j, int n)
{
    int k;
    float tmp;
    float *x1 = calloc(n, sizeof(float));
    float *x2 = calloc(n, sizeof(float));

    for(k=0; k<n; k++)
    {
        sscanf(PQgetvalue(res, i, k+1),"%f",&(x1[k]));
    }

    for(k=0; k<n; k++)
    {
        sscanf(PQgetvalue(res, j, k+1),"%f",&(x2[k]));
    }

    tmp = get_distance(x1, x2, n);
    free(x1);
    free(x2);
    return tmp;

}

float* featuresDistances(double* spikeFeatures, double* id_spike, int n, int points)
{
    PGconn          *conn = NULL;
    PGresult        *res;
    int i, j, q, k;
    int rec_count;
    char* query;

    float* distances;
    int * index;
    double id;

    conn = PQconnectdb("dbname=demo host=172.16.162.128 user=postgres password=postgres");
    if (PQstatus(conn) == CONNECTION_BAD) {
        printf("We were unable to connect to the database");
        return NULL;
    }

    query = build_query2(spikeFeatures, n, points);

    res = PQexec(conn,query);

    if (PQresultStatus(res) != PGRES_TUPLES_OK) {
        printf("get_dc: We did not get any data!");
        return NULL;
    }

    rec_count = PQntuples(res);

    distances = (float*)calloc(rec_count*rec_count,sizeof(float));
    index = (int*)calloc(rec_count*rec_count,sizeof(int));
    //con index guardo el indice del vector resultado que coincide con el id de cluster, no viene ordenado
    for(i=0; i<rec_count; i++)
    {
        for(j=0; j<rec_count; j++)
        {
            sscanf(PQgetvalue(res, j, points +1),"%lf",&(id));
            if (id == spikeFeatures[i])
            {
                index[i] = j;
                sscanf(PQgetvalue(res, j, 0),"%lf",&(id));
                id_spike[i] = id;
                break;
            }

        }
    }

    for(i=0; i<rec_count; i++)
    {
        for(j=0; j<rec_count; j++)
        {
            distances[i*rec_count+j] = get_distance_from_res(res, index[i], index[j], points);
        }
    }

    //esto es para que los id de features coincida con el orden de los ids
    // se agrego a la query
//    for (i = 0; i < n; i++)
//    {
//        sscanf(PQgetvalue(res, i, points +1),"%f",&(id));
//        spikeFeatures[i] = (double)id;
//    }

    PQclear(res);
    PQfinish(conn);
    free(query);

    return distances;
}

float getDC(char connect[], double* features,  double* id_spikes, int nspikes, float percent, int points)
{
    float *distances;
    float *array_distances;
    float dc;

    int i, j, k;
    int position;

    distances = featuresDistances(features, id_spikes, nspikes, points);
    array_distances = calloc(nspikes*(nspikes+1)/2-nspikes, sizeof(float));

    for (i = 0, k = 0; i < nspikes; i++) {
          for (j = i+1 ; j < nspikes; j++, k++) {
                array_distances[k] = distances[i*nspikes+j];
          }
      }

    //There are nspikes zeros, because distances from itselfs
    position = k*percent/100 -1 + nspikes;
    //position = nspikes + 2*nspikes*percent/100 -1;
    qsort(array_distances, k, sizeof(float), &compare);

    dc = array_distances[position];

    free(distances);
    free(array_distances);

    return dc;
}

int get_local_density(float* distances, int rec_count, float dc, double* local_density, char kernel[20])
//TODO: Parameter size
{
    int i, j;
    float distance;

    for (i = 0; i < rec_count; i++) local_density[i] = 0;

    if (!strcmp(kernel, "cutoff") )
    {
        for (i = 0; i < rec_count; i++) {
              for (j = i+1; j < rec_count; j++) {
                    distance = distances[i*rec_count+j];
                    if ( (distance - dc) < 0 )
                    {
                        local_density[i] += 1;
                        local_density[j] += 1;
                    }
              }
          }
    }

    if (!strcmp(kernel, "gaussian") )
    {
        for (i = 0; i < rec_count; i++) {
              for (j = i+1; j < rec_count; j++) {
                    distance = distances[i*rec_count+j];
                    local_density[i] = local_density[i] + exp(-(distance/dc)*(distance/dc));
                    local_density[j] = local_density[j] + exp(-(distance/dc)*(distance/dc));
              }
          }
    }

    return 0;
}

int get_distance_to_higher_density(float* distances, int rec_count, double* rho, double* delta, double* nneigh){
    //distancia minima a otro punto con mayor densidad
    double dist;
    double tmp;
    int i, j, k, flag;
    int index_nneigh, index_m;

    for (i = 0; i < rec_count; i++)
        delta[i] = 0;

    for(i = 0; i < rec_count; i++){
        dist = 0.0;
        flag = 0;
        for(j = 0; j < rec_count; j++){
            if(i == j) continue;
            if(rho[j] > rho[i]){
                //distance between i and j
                tmp = distances[i*rec_count+j];

                //index_nneigh es el indice del punto con menor distancia
                if(!flag){ //first time
                    dist = tmp;
                    index_nneigh = j;
                    flag = 1;
                }else{
                    if (tmp < dist) {
                        dist = tmp;
                        index_nneigh = j;
                    }
                }
            }
        }// Si i se trata de un punto de mayor densidad se carga la distancia maxima
        if(!flag){
            for(k = 0; k < rec_count; k++){
                tmp = distances[i*rec_count+k];
                if (tmp > dist) {
                    dist = 0;
                    index_nneigh = k;
                }
            }
            index_m = i;
        }
        delta[i] = dist;
        nneigh[i] = index_nneigh;
    }

    tmp = 0;
    for(k = 0; k < rec_count; k++){
        if (delta[k] > tmp){
            tmp = delta[k];
        }
    }
    delta[index_m] = 2*tmp;

    return 0;
}


void get_centers(double* rho, double *delta, double* centers, int rec_count, float fsd)
{
    double *deltacp;
    double max, min;
    double m, b, sd;
    double *ajuste, *ajuste2;
    int i, argmax, argmin;
    double pmean;

    double x1, x2, y1, y2;

    //eliminate firsts deltas, because it are a isolate centers
    deltacp = cp_vector(delta, rec_count);
    argmax = argmaxvector(rho, rec_count);
    max = rho[argmax]*0.1;

    pmean = mean(deltacp, rec_count);
    for(i=0; i<rec_count; i++)
    {
        if (rho[i] < max)
            deltacp[i] = pmean;
    }

    argmax = argmaxvector(deltacp, rec_count);
    max = deltacp[argmax];

    deltacp[argmax] = max/2;

    //least squares over deltacp and the centers are points over sd+least square
    // least_square y=m*x+b
    least_squares(rho, deltacp, rec_count, &m, &b, &sd);
    //printf("ajuste1 pmean:%f m:%f b:%f sd:%f\n", pmean, m, b, sd);

    ajuste = (double*)calloc(rec_count, sizeof(double));
    for(i=0; i<rec_count; i++)
        ajuste[i] = m*rho[i] + b;

    deltacp[argmax] = max;


    // second
    ajuste2 = (double*)calloc(rec_count, sizeof(double));
    argmax = argmaxvector(rho, rec_count);
    argmin = argminvector(rho, rec_count);
    min = rho[argmin];

    y1 = delta[argmin];
    x1 = min;
    y2 = 0;
    x2 = rho[argmax]*0.1;

    b = -x1*(y2-y1)/(x2-x1) + y1;
    m = (y2-y1)/(x2-x1);
    //printf("ajuste2 m:%f b:%f \n", m, b);
    for(i=0; i<rec_count; i++)
        ajuste2[i] = m*rho[i] + b;


    // get centers
    for(i=0; i<rec_count; i++)
    {
        if((delta[i] > ajuste[i] + fsd*sd) && (delta[i] > ajuste2[i] + fsd*sd))
        {
            centers[0]++;
            centers[(int)centers[0]] = i;
        }
    }
    free(deltacp);
    free(ajuste);
    free(ajuste2);
}


int assignation(double* rho, double* nneigh, float* distances, float dc, double* labels, int n, double* centers)
{
    double *ordrho_index;
    double *ordrho;
    double rho_average;
    double *bord_rho;
    int i, j;

    ordrho_index = (double*)calloc(n, sizeof(double));
    for(i=0; i<n; i++)
    {
        labels[i] = -1;
        ordrho_index[i] = i;
    }

    for(i=1; i<centers[0]+1; i++)
    {
        labels[(int)centers[i]] = i;
        //printf("%d,%d ", (int)centers[i],i);
    }
    //printf("\n");

    ordrho = cp_vector(rho, n);
    Quicksort(ordrho, ordrho_index, 0, n-1);

    for(i=0; i<n; i++)
    {
        if (labels[(int)ordrho_index[i]] == -1)
            labels[(int)ordrho_index[i]] = labels[(int)nneigh[(int)ordrho_index[i]]];
    }

    bord_rho = (double*)calloc((int)centers[0]+1,sizeof(double));
    if (centers[0]>1)
    {
        for(i=0; i<n-1; i++)
        {
            for(j=i+1; j<n; j++)
            {
                if ((labels[i]!=labels[j]) && (distances[i*n+j] <= dc))
                {
                    rho_average = (rho[i]+rho[j])/2.0;
                    if (rho_average > bord_rho[(int)labels[i]])
                        bord_rho[(int)labels[i]] = rho_average;
                    if (rho_average > bord_rho[(int)labels[j]])
                        bord_rho[(int)labels[j]] = rho_average;
//                    if (rho[i] > bord_rho[(int)labels[i]])
//                    {
//                        bord_rho[(int)labels[i]] = rho[i];
//                    }
//                    if (rho[j] > bord_rho[(int)labels[j]])
//                    {
//                        bord_rho[(int)labels[j]] = rho[j];
//                    }
                }
            }
        }
        for(i=0; i<n; i++)
        {
            if (rho[i] < bord_rho[(int)labels[i]])
                labels[i] = 0;
        }
    }
    free(ordrho_index);
    free(ordrho);
    free(bord_rho);
    return 0;
}


int dpClustering(double* spikeFeatures, int n, float dc, int points, char kernel[20], double* id_spike, double* labels, double* rho, double* delta, float smod)
{
    float *distances;
    double* nneigh= (double*)calloc(n, sizeof(double));
    double* centers = (double*)calloc(n, sizeof(double));
    int i;

    distances = featuresDistances(spikeFeatures, id_spike, n, points); //se reordena spikeFeatures, id_spike porque la query a la base devuelve en otro orden
    get_local_density(distances, n, dc, rho, kernel);
    get_distance_to_higher_density(distances, n, rho, delta, nneigh);

    get_centers(rho, delta, centers, n, smod);
    //printf("%lf %lf %lf\n", centers[1], centers[2], centers[3]);

    assignation(rho, nneigh, distances, dc, labels, n, centers);

    return 0;
}

int main()
{
    double id_spike[] = { 212156,  212460,  211848,  214279,  212626,  214117,  213780,  211583,  213302,  213102,  214158,  212577,  211494,  211480,  211497,  213538,  214076,  211857,  213420,  212353,  212750,  213182,  211926,  213269,  212898,  212246,  211894,  212088,  212580,  211898,  212824,  214099,  213750,  212017,  212573,  212920,  214086,  211476,  213499,  213146,  211646,  211602,  212851,  212590,  213856,  213404,  211478,  212172, 213207,  213581,  212832,  213090,  214208,  212674,  212566,  211753,  211680,  213553,  214255,  213440,  212083,  212892,  213078,  213836, 212797,  213380,  212871,  211498,  212768,  211678,  212986,  212589,  213890,  212283,  211996,  212276,  212869,  213551,  214075,  213163,  214193,  211488,  211518,  213536,  212138,  213542,  212789,  211460,  213948,  213032,  214198,  213346,  211587,  211900,  212620};

    double features[] = {75317,  75338,  75404,  75409,  74839,  74904,  74908,  74923,  74967,
  74999,  75001,  75074,  75169,  75178,  75215,  75219,  75221,  75247,
  74781,  74797,  74799,  74801,  74809,  74815,  74818,  74819,  75459,
  75477,  75493,  75567,  75597,  75604,  75674,  75781,  75887,  75894,
  75898,  75901,  75910,  75911,  75941,  75947,  75995,  76071,  76089,
  76110,  76118,  76145,  76153,  76172,  76190,  76192,  76213,  76219,
  76241,  76307,  76353,  76399,  76411,  76423,  76467,  76484,  76503,
  76528,  76590,  76623,  76667,  76701,  76725,  76741,  76761,  76820,
  76857,  76859,  76863,  76872,  76874,  76902,  77071,  77101,  77157,
  77177,  77211,  77269,  77396,  77397,  77407,  77420,  77438,  77479,
  77514,  77519,  77529,  77576,  77600};

    int nspikes = 331;
    nspikes = 21;
    int points = 10;
    float dc;
    double* local_density = (double*)calloc(nspikes,sizeof(double));
    double* distance_to_higher_density = (double*)calloc(nspikes,sizeof(double));
    double* nneigh = (double*)calloc(nspikes,sizeof(double));
    double* centers = (double*)calloc(5,sizeof(double));
    double* clusters = (double*)calloc(nspikes,sizeof(double));
    char connect[100] = "dbname=demo host=172.16.162.128 user=postgres password=postgres";

    dc = getDC(connect, features, id_spike, nspikes, 1.8, points);
    //dc = get_dc(connect, id_spike, nspikes, 1.8, points);

    //cluster_dp(connect, local_density, distance_to_higher_density, id_spike, clusters,
    //           nneigh, centers, dc, 6, nspikes, "gaussian");

    //dp(x, y, 27, labels, centers, "gaussian");
    //printf("dc:%f, 1:%lf 2:%lf\n",dc, local_density[22], distance_to_higher_density[22]);

    //dpClustering(features, nspikes, dc, 6, "gaussian", clusters);

    return 0;
}
