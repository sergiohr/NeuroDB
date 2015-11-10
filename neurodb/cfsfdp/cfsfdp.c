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
        acum = acum + array[0];
    }
    return acum/n;
}

char* build_query2(double* spikeFeaturesId, int nspikes, int points)
{
    char *query = (char*)malloc(sizeof(char)*17*nspikes);
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
    int i, j;
    int rec_count;
    char* query;

    float* distances;
    float id;

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

    for(i=0; i<rec_count; i++)
    {
        for(j=0; j<rec_count; j++)
        {
            distances[i*rec_count+j] = get_distance_from_res(res, i, j, points);
        }
    }

    for (i = 0; i < n; i++)
    {
        sscanf(PQgetvalue(res, i, 0),"%f",&(id));
        id_spike[i] = (double)id;
    }

    //esto es para que los id de features coincida con el orden de los ids
    // se agrego a la query
    for (i = 0; i < n; i++)
    {
        sscanf(PQgetvalue(res, i, points +1),"%f",&(id));
        spikeFeatures[i] = (double)id;
    }

    PQclear(res);
    PQfinish(conn);
    free(query);

    return distances;
}

float* get_distances(char connect[], double* id_spike, int nspikes, int points)
{
    PGconn          *conn = NULL;
    PGresult        *res;
    int i, j;
    int rec_count;
    char* query;

    float* distances;
    float id;

    conn = PQconnectdb(connect);
    if (PQstatus(conn) == CONNECTION_BAD) {
        printf("We were unable to connect to the database");
        return NULL;
    }

    query = build_query(id_spike, nspikes, points);

    res = PQexec(conn,query);

    if (PQresultStatus(res) != PGRES_TUPLES_OK) {
        printf("get_dc: We did not get any data!");
        return NULL;
    }

    rec_count = PQntuples(res);

    distances = (float*)calloc(rec_count*rec_count,sizeof(float));

    for(i=0; i<rec_count; i++)
    {
        for(j=0; j<rec_count; j++)
        {
            distances[i*rec_count+j] = get_distance_from_res(res, i, j, points);
        }
    }

    for (i = 0; i < nspikes; i++)
    {
        sscanf(PQgetvalue(res, i, 0),"%f",&(id));
        id_spike[i] = (double)id;
    }

    PQclear(res);
    PQfinish(conn);
    free(query);

    return distances;
}

float get_dc(char connect[], double* id_spike, int nspikes, float percent, int points)
{
    float *distances;
    float *array_distances;
    float dc;

    int i, j, k;
    int position;

    distances = get_distances(connect, id_spike, nspikes, points);
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
    //minimum distance to the point with higher density than own
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

                //index_nneigh contains index of the point that minimum distance
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


void get_centers(double* rho, double *delta, double* centers, int rec_count)
{
    double *deltacp;
    double max;
    double m, b, sd;
    double *ajuste;
    int i, argmax;
    double pmean;

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

    deltacp[argmax] = 0;

    //least squares over deltacp and the centers are points over sd+least square
    // least_square y=m*x+b
    least_squares(rho, deltacp, rec_count, &m, &b, &sd);

    ajuste = (double*)calloc(rec_count, sizeof(double));
    for(i=0; i<rec_count; i++)
        ajuste[i] = m*rho[i] + b;

    deltacp[argmax] = max;

    for(i=0; i<rec_count; i++)
    {
        if(deltacp[i] > ajuste[i] + 2*sd)
        {
            centers[0]++;
            centers[(int)centers[0]] = i;
        }
    }
    printf("cant centers: %lf\n", centers[0]);
    free(deltacp);
    free(ajuste);
}

int dp(double* x, double *y, int n, double* labels, double* centers, char kernel[20])
{
    int i, j, k=0, position;
    float* distances =(float*)malloc(n*n*sizeof(float*));
    double* rho = (double*)calloc(n,sizeof(double));
    double* delta = (double*)calloc(n,sizeof(double));
    double* nneigh = (double*)calloc(n,sizeof(double));
    float* vdistances = (float*)calloc(n*n,sizeof(float));
    float dc;
    double* bord_rho;
    double* ordrho_index;
    double* ordrho;
    double rho_average;

    distances = (float*)calloc(n*n,sizeof(float));

    for(i=0; i<n; i++)
    {
        for(j=0; j<n; j++)
        {
            distances[i*n+j] = pow(pow(x[i]-x[j],2)+pow(y[i]-y[j],2), 0.5);
            vdistances[k] = (float)distances[i*n+j];
            k++;
        }
    }

    qsort(vdistances, k, sizeof(float), &compare);

    position = (k*2/100 -1)+27;
    dc = vdistances[position];

    get_local_density(distances, n, dc, rho, kernel);
    get_distance_to_higher_density(distances, n, rho, delta, nneigh);
    get_centers(rho, delta, centers, n);

    ordrho_index = (double*)calloc(n, sizeof(double));
    for(i=0; i<n; i++)
    {
        labels[i] = -1;
        ordrho_index[i] = i;
    }

    for(i=1; i<centers[0]+1; i++)
    {
        labels[(int)centers[i]] = i;
    }

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
                }
            }
        }
        for(i=0; i<n; i++)
        {
            if (rho[i] < bord_rho[(int)labels[i]])
                labels[i] = 0;
        }
    }

    free(distances);
    free(ordrho_index);
    free(bord_rho);
    free(vdistances);
    free(rho);
    free(delta);
    free(nneigh);
    return 0;

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
    }

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


int cluster_dp(char connect[], double* rho, double *delta, double* id_spike, double* cluster_index,
               double* nneigh, double* centers, float dc, int points, int nspikes, char kernel[20])
{
    float *distances;
    int i, j;
    double* ordrho;
    double* ordrho_index;
    double* bord_rho;
    double rho_average;

    distances = get_distances(connect, id_spike, nspikes, points);

    get_local_density(distances, nspikes, dc, rho, kernel);
    get_distance_to_higher_density(distances, nspikes, rho, delta, nneigh);

    get_centers(rho, delta, centers, nspikes);

    assignation(rho, nneigh, distances, dc, cluster_index, nspikes, centers);

//    ordrho_index = (double*)calloc(nspikes, sizeof(double));
//    for(i=0; i<nspikes; i++)
//    {
//        cluster_index[i] = -1;
//        ordrho_index[i] = i;
//    }
//
//    for(i=1; i<centers[0]+1; i++)
//    {
//        cluster_index[(int)centers[i]] = i;
//    }
//
//    ordrho = cp_vector(rho, nspikes);
//    Quicksort(ordrho, ordrho_index, 0, nspikes-1);
//
//    for(i=0; i<nspikes; i++)
//    {
//        if (cluster_index[(int)ordrho_index[i]] == -1)
//            cluster_index[(int)ordrho_index[i]] = cluster_index[(int)nneigh[(int)ordrho_index[i]]];
//    }
//
//    bord_rho = (double*)calloc((int)centers[0]+1,sizeof(double));
//    if (centers[0]>1)
//    {
//        for(i=0; i<nspikes-1; i++)
//        {
//            for(j=i+1; j<nspikes; j++)
//            {
//                if ((cluster_index[i]!=cluster_index[j]) && (distances[i*nspikes+j] <= dc))
//                {
//                    rho_average = (rho[i]+rho[j])/2.0;
//                    if (rho_average > bord_rho[(int)cluster_index[i]])
//                        bord_rho[(int)cluster_index[i]] = rho_average;
//                    if (rho_average > bord_rho[(int)cluster_index[j]])
//                        bord_rho[(int)cluster_index[j]] = rho_average;
//                }
//            }
//        }
//        for(i=0; i<nspikes; i++)
//        {
//            if (rho[i] < bord_rho[(int)cluster_index[i]])
//                cluster_index[i] = 0;
//        }
//    }
//
//    free(distances);
//    free(ordrho_index);
//    free(bord_rho);
    return 0;
}


int dpClustering(double* spikeFeatures, int n, float dc, int points, char kernel[20], double* id_spike, double* labels, double* rho, double* delta)
{
    float *distances;
    double* nneigh= (double*)calloc(n, sizeof(double));
    //double* rho = (double*)calloc(n, sizeof(double));
    //double* delta = (double*)calloc(n, sizeof(double));
    double* centers = (double*)calloc(n, sizeof(double));

    distances = featuresDistances(spikeFeatures, id_spike, n, points); //se reordena spikeFeatures, id_spike porque la query a la base devuelve en otro orden
    get_local_density(distances, n, dc, rho, kernel);
    get_distance_to_higher_density(distances, n, rho, delta, nneigh);

    get_centers(rho, delta, centers, n);

    assignation(rho, nneigh, distances, dc, labels, n, centers);

    return 0;
}

int main()
{
    double id_spike[] = { 136060, 136816, 132559, 137671, 136520, 134386, 130932, 137943, 130951, 136204,
                            136588, 133250, 137043, 131845, 131522, 133864, 132292, 134846, 132863, 135983,
                            135810, 137945, 131869, 134349, 136100, 133632, 137515, 136622, 130879, 130826,
                            136173, 134813, 134353, 134236, 131356, 137129, 132899, 131330, 131644, 133759,
                            132435, 132670, 132970, 134018, 136051, 135090, 136395, 131401, 135516, 134812,
                            135360, 131205, 134952, 135660, 135689, 132678, 137862, 135688, 132205, 130878,
                            134595, 134081, 134070, 135459, 130828, 133503, 131032, 137912, 131398, 133312,
                            130791, 133933, 132546, 134060, 137288, 132018, 137565, 134524, 134596, 137055,
                            136707, 136910, 133220, 136952, 133796, 136683, 135575, 131388, 135280, 133005,
                            133251, 131854, 136632, 137200, 137681, 136031, 135489, 131910, 132565, 131842,
                            135140, 133332, 135588, 135651, 134369, 133493, 134077, 135859, 131799, 133149,
                            132195, 134417, 132620, 137578, 131782, 131753, 133345, 135361, 133151, 132196,
                            137205, 132153, 134365, 132958, 134454, 136758, 134117, 134021, 131783, 136349,
                            131271, 134605, 136244, 133410, 133276, 136087, 132341, 134141, 137382, 130825,
                            133616, 132446, 131214, 131185, 131020, 134020, 136750, 137237, 136621, 132270,
                            135098, 134915, 135974, 131679, 131549, 131029, 135566, 131328, 135681, 131349,
                            134913, 131361, 133846, 131650, 134110, 137357, 134679, 136926, 135570, 136736,
                            133183, 133903, 131889, 134566, 137247, 130810, 135069, 135348, 132636, 133965,
                            134254, 133869, 134751, 133171, 135882, 135997, 133458, 137414, 137779, 134488,
                            136421, 137034, 137178, 132786, 136969, 135524, 137571, 134287, 135363, 133422,
                            133510, 135213, 135408, 130769, 134853, 132635, 132403, 137199, 131843, 133304,
                            134400, 133395, 132301, 131687, 131123, 134811, 133394, 137117, 131752, 135201,
                            134170, 135035, 133424, 132188, 131984, 131104, 134597, 130944, 131920, 137116,
                            134188, 135659, 131304, 136999, 135124, 132957, 135790, 133117, 131767, 131615,
                            136749, 137251, 134704, 133637, 136686, 134124, 134393, 133745, 130869, 137239,
                            131275, 131982, 131274, 132567, 133838, 136611, 137569, 136649, 134944, 132994,
                            131561, 134871, 131277, 134620, 133172, 133461, 132624, 136911, 132367, 136184,
                            133551, 136630, 132991, 137313, 136136, 135048, 132473, 133597, 134291, 132560,
                            136059, 132836, 133696, 131729, 130776, 132798, 137220, 134802, 136762, 134971,
                            131024, 135215, 136972, 136848, 133026, 137910, 135191, 137256, 135858, 131993,
                            136576, 135761, 135940, 133911, 133196, 133798, 135718, 135133, 130857, 133044,
                            136441, 134088, 134984, 136027, 135908, 132939, 137557, 136187, 132477, 133067,
                            135233, 137105, 134090, 136172, 131794, 133453, 135597, 134125, 131332, 132275,
                            132418, 137551, 134538, 133578, 136853, 137293, 135829, 131145, 136490, 132309,
                            132692, 137758, 135788, 133059, 137856, 133315, 136367, 134389, 133261, 136265,
                            134845, 133291, 130855, 134645, 133107, 136139, 137656, 137249, 132297, 135167 };

    double features[] = {   23658, 23659, 23660, 23661, 23662, 23663, 23664, 23665, 23666,
                            23667, 23668, 23669, 23670, 23671, 23672, 23673, 23674, 23675,
                            23676, 23677, 23678};

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

    dc = getDC(connect, features, local_density, nspikes, 1.8, points);
    //dc = get_dc(connect, id_spike, nspikes, 1.8, points);

    //cluster_dp(connect, local_density, distance_to_higher_density, id_spike, clusters,
    //           nneigh, centers, dc, 6, nspikes, "gaussian");

    //dp(x, y, 27, labels, centers, "gaussian");
    //printf("dc:%f, 1:%lf 2:%lf\n",dc, local_density[22], distance_to_higher_density[22]);

    //dpClustering(features, nspikes, dc, 6, "gaussian", clusters);

    return 0;
}
