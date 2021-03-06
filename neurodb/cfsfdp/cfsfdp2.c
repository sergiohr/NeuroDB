//compiling with : gcc -fPIC -o cfsfdp.so -shared cfsfdp.c -I/usr/include/pgsql -L/usr/lib/postgresql92/lib64 -lpq

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <libpq-fe.h>
#include <string.h>
#include <math.h>

//TODO Returns array. Now all arrays are defined in python a passed it by parameters.

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

double mean(double v[], int n)
{
    int i;
    float m = 0;

    for(i=0; i<n; i++) m += v[i];

    return m/n;
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
        sscanf(PQgetvalue(res, i, k),"%f",&(x1[k]));
    }

    for(k=0; k<n; k++)
    {
        sscanf(PQgetvalue(res, j, k),"%f",&(x2[k]));
    }

    tmp = get_distance(x1, x2, n);
    free(x1);
    free(x2);
    return tmp;

}

char* build_query(char *id_block, char *channel, int n)
{
    char *query = (char*)malloc(sizeof(char)*500);
    char aux[6];
    int i;

    strcpy(query, "SELECT ");

    for(i=1; i<n+1; i++)
    {
        sprintf(aux, "p%d, ", i);
        strcat(query, aux);
    }

    query[strlen(query)-2] = ' ';
    query[strlen(query)-1] = '\0';

    strcat(query, "from SPIKE JOIN segment ON id_segment = segment.id ");
    strcat(query, "JOIN recordingchannel ON id_recordingchannel = recordingchannel.id ");
    strcat(query, "WHERE segment.id_block = ");
    strcat(query, id_block);
    strcat(query, " AND recordingchannel.index = ");
    strcat(query, channel);

    query = realloc(query, sizeof(char)*(strlen(query)+1));

    return query;
}

float** get_distances(char connect[], char id_block[], char channel[], int n, int* rec_count)
{
    PGconn          *conn;
    PGresult        *res;
    int i, j;
    char* query;

    float** distances;

    conn = PQconnectdb(connect);
    if (PQstatus(conn) == CONNECTION_BAD) {
        printf("We were unable to connect to the database");
        return NULL;
    }

    query = build_query(id_block, channel, n);

    res = PQexec(conn,query);

    if (PQresultStatus(res) != PGRES_TUPLES_OK) {
        printf("get_dc: We did not get any data!");
        return NULL;
    }

    *rec_count = PQntuples(res);

    distances = (float**)malloc(*rec_count*sizeof(float*));

    for(i=0; i<*rec_count; i++)
    {
        distances[i] = (float*)calloc(*rec_count,sizeof(float));
    }

    for(i=0; i<*rec_count; i++)
    {
        for(j=0; j<*rec_count; j++)
        {
            distances[i][j] = get_distance_from_res(res, i, j, n);
        }
    }

    PQclear(res);
    PQfinish(conn);
    free(query);

    return distances;
}

float get_dc(char connect[], char id_block[], char channel[], float percent, int n)
{
    float **distances;
    float *array_distances;
    float dc;

    int i, j, k;
    int rec_count;
    int position;

    distances = get_distances(connect, id_block, channel, n, &rec_count);
    array_distances = calloc(rec_count*(rec_count+1)/2-rec_count, sizeof(float));

    for (i = 0, k = 0; i < rec_count; i++) {
          for (j = i+1 ; j < rec_count; j++, k++) {
                array_distances[k] = distances[i][j];
          }
      }

    //There are rec_count zeros, because distances from itselfs
    position = k*percent/100 -1;//position = rec_count + 2*rec_count*percent/100 -1;
    qsort(array_distances, k, sizeof(float), &compare);

    dc = array_distances[position];

    for (i = 0; i < rec_count; i++) {
        free(distances[i]);
    }
    free(distances);
    free(array_distances);

    return dc;
}

int get_local_density(float** distances, int rec_count, float dc, double* local_density, char kernel[20])
//TODO: Parameter size
{
    int i, j;
    float distance;

    printf("Local density - dc: %f\n", dc);

    for (i = 0; i < rec_count; i++) local_density[i] = 0;

    if (!strcmp(kernel, "cutoff") )
    {
        for (i = 0; i < rec_count; i++) {
              for (j = i+1; j < rec_count; j++) {
                    distance = distances[i][j];
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
                    distance = distances[i][j];
                    local_density[i] = local_density[i] + exp(-(distance/dc)*(distance/dc));
                    local_density[j] = local_density[j] + exp(-(distance/dc)*(distance/dc));
              }
          }
    }

    return 0;
}

int get_distance_to_higher_density(float** distances, int rec_count, double* rho, double* delta, double* nneigh){

    double dist;
    double tmp;
    int i, j, k, flag;
    int index_nneigh;

    for (i = 0; i < rec_count; i++)
        delta[i] = 0;

    for(i = 0; i < rec_count; i++){
        dist = 0.0;
        flag = 0;
        for(j = 0; j < rec_count; j++){
            if(i == j) continue;
            if(rho[j] > rho[i]){

                tmp = distances[i][j];

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
        }
        if(!flag){
            for(k = 0; k < rec_count; k++){
                tmp = distances[i][k];
                if (tmp > dist) {
                    dist = tmp;
                    index_nneigh = k;
                }
            }
        }
        delta[i] = dist;
        nneigh[i] = index_nneigh;
    }

    return 0;
}

double maxvector(double* rho, int n)
{
    int i;
    double max = rho[0];
    for(i=1; i<n; i++)
    {
        if (max<rho[i]) max=rho[i];
    }

    return max;
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

void get_centers(double* rho, double *delta, double* centers, int rec_count)
{
    double *deltacp;
    double max;
    double m, b, sd;
    double *ajuste;
    int i;

    //eliminate firsts deltas, because it are a isolate centers
    deltacp = cp_vector(delta, rec_count);
    max = maxvector(rho, rec_count);
    max = max*0.06;

    for(i=0; i<rec_count; i++)
    {
        if (rho[i] < max)
            deltacp[i] = 0;
    }

    //least squares over deltacp and the centers are points over sd+least square
    // least_square y=m*x+b
    least_squares(rho, deltacp, rec_count, &m, &b, &sd);

    ajuste = (double*)calloc(rec_count, sizeof(double));
    for(i=0; i<rec_count; i++)
        ajuste[i] = m*rho[i] + b;

    for(i=0; i<rec_count; i++)
    {
        if(deltacp[i] > ajuste[i] + 1.7*sd)
        {
            centers[0]++;
            centers[(int)centers[0]] = i;
        }
    }
    free(deltacp);
    free(ajuste);
}

int cluster_dp(char connect[], char id_block[], char channel[], double* rho, double *delta, double* id_spike, double* cluster_index, double* nneigh, double* centers, float dc, int points, char kernel[20])
{
    float **distances;
    int rec_count;
    int i, j;
    double* ordrho;
    double* ordrho_index;
    double* bord_rho;
    double rho_average;

    distances = get_distances(connect, id_block, channel, points, &rec_count);

    get_local_density(distances, rec_count, dc, rho, kernel);
    get_distance_to_higher_density(distances, rec_count, rho, delta, nneigh);

    get_centers(rho, delta, centers, rec_count);

    ordrho_index = (double*)calloc(rec_count, sizeof(double));
    for(i=0; i<rec_count; i++)
    {
        cluster_index[i] = -1;
        ordrho_index[i] = i;
    }

    for(i=1; i<centers[0]+1; i++)
    {
        cluster_index[(int)centers[i]] = i;
    }

    ordrho = cp_vector(rho, rec_count);
    Quicksort(ordrho, ordrho_index, 0, rec_count-1);

    for(i=0; i<rec_count; i++)
    {
        if (cluster_index[(int)ordrho_index[i]] == -1)
            cluster_index[(int)ordrho_index[i]] = cluster_index[(int)nneigh[(int)ordrho_index[i]]];
    }

    bord_rho = (double*)calloc((int)centers[0]+1,sizeof(double));
    if (centers[0]>1)
    {
        for(i=0; i<rec_count-1; i++)
        {
            for(j=i+1; j<rec_count; j++)
            {
                if ((cluster_index[i]!=cluster_index[j]) && (distances[i][j] <= dc))
                {
                    rho_average = (rho[i]+rho[j])/2.0;
                    if (rho_average > bord_rho[(int)cluster_index[i]])
                        bord_rho[(int)cluster_index[i]] = rho_average;
                    if (rho_average > bord_rho[(int)cluster_index[j]])
                        bord_rho[(int)cluster_index[j]] = rho_average;
                }
            }
        }
        for(i=0; i<rec_count; i++)
        {
            if (rho[i] < bord_rho[(int)cluster_index[i]])
                cluster_index[i] = 0;
        }
    }

    for (i = 0; i < rec_count; i++) {
        free(distances[i]);
    }
    free(distances);
    free(ordrho_index);
    return 0;
}

int get_n_dbspikes(char connect[], char id_block[], char channel[])
{
    PGconn          *conn;
    PGresult        *res;

    char query[250];
    int nspikes;

    conn = PQconnectdb(connect);

    strcpy(query, "SELECT count(spike.id) from SPIKE ");
    strcat(query, "JOIN segment ON id_segment = segment.id ");
    strcat(query, "JOIN recordingchannel ON id_recordingchannel = recordingchannel.id ");
    strcat(query, "WHERE segment.id_block = ");
    strcat(query, id_block);
    strcat(query, " AND recordingchannel.index = ");
    strcat(query, channel);

    if (PQstatus(conn) == CONNECTION_BAD) {
        puts("cluster_dp: We were unable to connect to the database");
        return 1;
    }

    res = PQexec(conn,query);

    sscanf(PQgetvalue(res, 0, 0),"%d",&nspikes);

    return nspikes;
}


int get_clusters(char connect[], char id_block[], char channel[], double* spikes_id)
{
    PGconn          *conn;
    PGresult        *res;

    int rec_count, i;
    char query[250];
    float value;

    conn = PQconnectdb(connect);
    strcpy(query, "SELECT spike.id from SPIKE ");
    strcat(query, "JOIN segment ON id_segment = segment.id ");
    strcat(query, "JOIN recordingchannel ON id_recordingchannel = recordingchannel.id ");
    strcat(query, "WHERE segment.id_block = ");
    strcat(query, id_block);
    strcat(query, " AND recordingchannel.index = ");
    strcat(query, channel);
    res = PQexec(conn,query);
    rec_count = PQntuples(res);

    for (i = 0; i < rec_count; i++) {
        sscanf(PQgetvalue(res, i, 0),"%f",&value);
        spikes_id[i] = value;
    }

    PQclear(res);
    PQfinish(conn);
    return 0;
}

int main(int argc, char* argv[])
{
    //float dc = 0;
    char connect[100] = "dbname=demo host=172.16.162.128 user=postgres password=postgres";
    double* local_density = (double*)calloc(1026,sizeof(double));
    double* distance_to_higher_density = (double*)calloc(1026,sizeof(double));
    double* nneigh = (double*)calloc(1026,sizeof(double));
    //double* gamma = (double*)calloc(1026,sizeof(double));
    double* centers = (double*)calloc(5,sizeof(double));
    //double* cluster = (double*)calloc(1026,sizeof(double));
    double** clusters = (double**)malloc(sizeof(double*)*2);
    clusters[0] = (double*)calloc(1026,sizeof(double));
    clusters[1] = (double*)calloc(1026,sizeof(double));
//
    float dc = get_dc(connect, "57", "20", 1.8, 3);

    cluster_dp(connect, "57", "20", local_density, distance_to_higher_density, clusters[0], clusters[1], nneigh, centers, dc, 10, "gaussian");
//
//    get_distance_to_higher_density3("dbname=demo host=192.168.2.2 user=postgres password=postgres", "54", "3", local_density, distance_to_higher_density);
//
    //get_centers_cluster_dp("dbname=demo host=192.168.2.2 user=postgres password=postgres", "54", "3", centers, dc);

    //get_cluster_dp("dbname=demo host=192.168.2.2 user=postgres password=postgres", "54", "3", centers[2], cluster, dc);
//
//    clusters = get_cluster_dp("dbname=demo host=192.168.2.2 user=postgres password=postgres", "54", centers);

    //get_cluster_dp2("dbname=demo host=192.168.2.2 user=postgres password=postgres", "54", "3", clusters[0], clusters[1], dc);
    //get_clusters(connect, "54", "3", centers, clusters[0], clusters[1], 3, dc);

    //double a[] = {9, 3, 1, 4, 2, 0, 5, 7, 6, 8};
    //double b[] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
    //Quicksort(a, b, 0, 9);

    free(clusters[0]);
    free(clusters[1]);
    free(centers);
    free(clusters);
    free(local_density);
    free(distance_to_higher_density);
    free(nneigh);
    return 1;
}
