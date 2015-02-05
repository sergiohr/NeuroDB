//compiling with : gcc -fPIC -o cfsfdp.so -shared cfsfdp.c -I/usr/include/pgsql -L/usr/lib/postgresql92/lib64 -lpq

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <libpq-fe.h>
#include <string.h>
#include <math.h>

//TODO Returns array. Now all arrays are defined in python a passed it by parameters.

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
    pivot_value = index[pivote];
    for (i=left+1; i<=right; i++){
        if (index[i] < pivot_value){
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

/**
  @brief Get Eclidean Distance within 2 3D points (P1 and P2).

  P1 contains 3 components (float) x1, y1 and z1
  P2 contains 3 components (float) x2, y2 and z2

  @param x1
  @param x2
  @param y1
  @param y2
  @param z1
  @param z2

  @returns Eclidean Distance within P1 and P2
  */
float get_distance(float x1, float y1, float z1, float x2, float y2, float z2)
{
    double tmp = pow(x1 - x2, 2) + pow(y1 - y2, 2) + pow(z1 - z2, 2);
    return pow(tmp, 0.5);
}


/**
  @brief Get Eclidean Distance within 2 3D points from a PGresult group of points.

  Points are from structure PGresult (structure of libpq, that represent a result of a query): parameter res.
  Each position of res, contains a point and the first 3 components of each position must be the components of
  point, see example.
  Points into structure are indexed by i and j parameters.

  @param res, PGresult that contains in each position the 3 components of the point.
  @param i, index of point i.
  @param j, index of point j.

  @returns Eclidean Distance within point j and point i from a PGresult.

  Example:
  \verbatim
      float      distance;
      PGconn     *conn;
      PGresult   *res;
      char       query[] = "SELECT spike.p1, spike.p2, spike.p3, spike.id from SPIKE JOIN
                            segment ON id_segment = segment.id WHERE segment.id_block = 54";

      conn = PQconnectdb("dbname=demo host=192.168.2.2 user=postgres password=postgres");

      res = PQexec(conn,query);

      distance = get_distance_from_res(res, 0, 1); //Euclidean distance within point 0 and point 1
   \endverbatim

  */
float get_distance_from_res(PGresult *res, int i, int j)
{
    float tmp;
    float x1, x2, y1, y2, z1, z2;
    sscanf(PQgetvalue(res, i, 0),"%f",&x1);
    sscanf(PQgetvalue(res, i, 1),"%f",&y1);
    sscanf(PQgetvalue(res, i, 2),"%f",&z1);
    sscanf(PQgetvalue(res, j, 0),"%f",&x2);
    sscanf(PQgetvalue(res, j, 1),"%f",&y2);
    sscanf(PQgetvalue(res, j, 2),"%f",&z2);
    tmp = get_distance(x1, y1, z1, x2, y2, z2);

    return tmp;

}


/**
  @brief DC is a cutoff distance used by dp algorithm to consider a point closer of farther
  to a center of point's density.

  DC is the average number of neighbors, around 1 to 2% of the total number of points in the data set.

  @param connect, string of data connect. See example.
  @param id_block, id project block where this function calculates the dc.
  @param percent, percent of the total number of points in the data set to consider.

  @returns Cutoff distance, DC.

  Example:
  \verbatim
      float      dc;
      char connect[] = "dbname=demo host=192.168.2.2 user=postgres password=postgres";

      dc = get_dc(connect, 54, 2);
   \endverbatim

  */
float get_dc(char connect[], char id_block[], char channel[], float percent)
{
    char query[250];
    strcpy(query, "SELECT spike.p1, spike.p2, spike.p3 from SPIKE ");
    strcat(query, "JOIN segment ON id_segment = segment.id ");
    strcat(query, "JOIN recordingchannel ON id_recordingchannel = recordingchannel.id ");
    strcat(query, "WHERE segment.id_block = ");
    strcat(query, id_block);
    strcat(query, " AND recordingchannel.index = ");
    strcat(query, channel);

    PGconn          *conn;
    PGresult        *res;
    int             rec_count;

    int n = 0, i, j;
    float dc = 0.0;
    float* distances = NULL;
    int position;

    conn = PQconnectdb(connect);

    if (PQstatus(conn) == CONNECTION_BAD) {
        puts("We were unable to connect to the database");
        return 0.0;
    }
    res = PQexec(conn,query);

    if (PQresultStatus(res) != PGRES_TUPLES_OK) {
        puts("get_dc: We did not get any data!");
        return 0.0;
    }

    rec_count = PQntuples(res);
    distances = (float*)malloc(sizeof(float)*rec_count*rec_count);

    for (i = 0, n = 0; i < rec_count; i++) {
          for (j = 0; j < rec_count; j++, n++) {
                distances[n] = get_distance_from_res(res, i, j);
          }
      }

    //There are rec_count zeros, because distances from itselfs
    position = rec_count*percent/100 -1;//position = rec_count + 2*rec_count*percent/100 -1;
    qsort(distances, rec_count, sizeof(float), &compare);

    dc = distances[position];

    PQclear(res);
    PQfinish(conn);
    return dc;
}


/**
  @brief Local Density or Rho is basically equal to the number of points that are closer than dc to point i.

  @param connect, string of data connect. See example.
  @param id_block, id project block where this function calculates the dc.
  @param local_density, array to return with local density of each point.
  @param kernel, criteria of measure distance, it must be "cutoff" or "gaussian".

  @returns Code Error (TODO)

  \verbatim
      float      dc;
      char connect[] = "dbname=demo host=192.168.2.2 user=postgres password=postgres";
      double* local_density = (double*)calloc(1026,sizeof(double));

      dc = get_dc(connect, 54, 2);
      get_local_density(connect, "54", dc, local_density, "gaussian");
   \endverbatim

  */
int get_local_density(char connect[], char id_block[], char channel[], float dc, double* local_density, char kernel[20])
//TODO: Parameter size
{

    PGconn          *conn;
    PGresult        *res;
    int             rec_count;

    char query[250];
    int i, j;
    double distance;

    if (strcmp(kernel, "gaussian") && strcmp(kernel, "cutoff"))
    {
        puts("Kernel parameter must be \"gaussian\" or \"cutoff\".");
        return 1;
    }

    strcpy(query, "SELECT spike.p1, spike.p2, spike.p3 from SPIKE ");
    strcat(query, "JOIN segment ON id_segment = segment.id ");
    strcat(query, "JOIN recordingchannel ON id_recordingchannel = recordingchannel.id ");
    strcat(query, "WHERE segment.id_block = ");
    strcat(query, id_block);
    strcat(query, " AND recordingchannel.index = ");
    strcat(query, channel);

    conn = PQconnectdb(connect);

    if (PQstatus(conn) == CONNECTION_BAD) {
        puts("We were unable to connect to the database");
        return 1;
    }


    res = PQexec(conn,query);

    if (PQresultStatus(res) != PGRES_TUPLES_OK) {
        puts("get_local_density: We did not get any data!");
        return 2;
    }

    rec_count = PQntuples(res);

    for (i = 0; i < rec_count; i++) local_density[i] = 0;

    if (!strcmp(kernel, "cutoff") )
    {
        for (i = 0; i < rec_count; i++) {
              for (j = i+1; j < rec_count; j++) {
                    distance = get_distance_from_res(res, i, j);
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
                    distance = get_distance_from_res(res, i, j);
                    local_density[i] = local_density[i] + exp(-(distance/dc)*(distance/dc));
                    local_density[j] = local_density[j] + exp(-(distance/dc)*(distance/dc));
              }
          }
    }

    PQclear(res);
    PQfinish(conn);

    return 0;
}

/**
  @brief Minimum Distance with higher density is measured by computing the minimum
  distance between the point i and any other point with higher density.

  @param connect, string of data connect. See example.
  @param id_block, id project block.
  @param rho, array from get_local_density.
  @param delta, array to return.
  @param size, array lenght.

  @returns Code Error (TODO)

  \verbatim
      float      dc;
      char connect[] = "dbname=demo host=192.168.2.2 user=postgres password=postgres";
      double* local_density = (double*)calloc(1026,sizeof(double));
      double* distance_to_higher_density = (double*)calloc(1026,sizeof(double));

      dc = get_dc(connect, 54, 2);

      get_local_density(connect, "54", dc, local_density, "gaussian");
      get_distance_to_higher_density(connect, "54",local_density, distance_to_higher_density, 1026);


   \endverbatim

  */
int get_distance_to_higher_density(char connect[], char id_block[], char channel[], double* rho, double* delta){

    PGconn          *conn;
    PGresult        *res;
    int             rec_count;

    double dist;
    double tmp;
    char query[250];
    int i, j, k, flag;

    strcpy(query, "SELECT spike.p1, spike.p2, spike.p3 from SPIKE ");
    strcat(query, "JOIN segment ON id_segment = segment.id ");
    strcat(query, "JOIN recordingchannel ON id_recordingchannel = recordingchannel.id ");
    strcat(query, "WHERE segment.id_block = ");
    strcat(query, id_block);
    strcat(query, " AND recordingchannel.index = ");
    strcat(query, channel);

    conn = PQconnectdb(connect);

    if (PQstatus(conn) == CONNECTION_BAD) {
        puts("We were unable to connect to the database");
        return 1;
    }

    res = PQexec(conn,query);

    if (PQresultStatus(res) != PGRES_TUPLES_OK) {
        puts("get_distance_to_higher_density: We did not get any data!");
        return 2;
    }

    rec_count = PQntuples(res);

    for (i = 0; i < rec_count; i++)
        delta[i] = 0;

    for(i = 0; i < rec_count; i++){
        dist = 0.0;
        flag = 0;
        for(j = 0; j < rec_count; j++){
            if(i == j) continue;
            if(rho[j] > rho[i]){

                tmp = get_distance_from_res(res, i, j);

                if(!flag){
                    dist = tmp;
                    flag = 1;
                }else dist = tmp < dist ? tmp : dist;
            }
        }
        if(!flag){
            for(k = 0; k < rec_count; k++){
                tmp = get_distance_from_res(res, i, k);
                dist = tmp > dist ? tmp : dist;
            }
        }
        delta[i] = dist;
    }

    PQclear(res);
    PQfinish(conn);

    return 0;
}

/**
  @brief Select centers of clusters

  @param connect, string of data connect. See example.
  @param id_block, id project block.
  @param channel, index of channel.
  @param centers, array where centers are returned.
  @param dc, see get_dc .

  @returns Code Error (TODO)

  \verbatim
      float      dc;
      char connect[] = "dbname=demo host=192.168.2.2 user=postgres password=postgres";
      double* centers = (double*)calloc(1026,sizeof(double));

      dc = get_dc(connect, "54", "3", 2);

      get_centers_cluster_dp(connect, "54", "3", centers, dc);

   \endverbatim

  */
int get_centers_cluster_dp(char connect[], char id_block[], char channel[], double* centers, double dc)
{
    PGconn          *conn;
    PGresult        *res;
    int             rec_count;

    char query[250];
    double* local_density;
    double* distance_to_higher_density;
    double* gamma;
    float meanf;
    int i;

    conn = PQconnectdb(connect);

    strcpy(query, "SELECT spike.id, spike.p1, spike.p2, spike.p3 from SPIKE ");
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
    rec_count = PQntuples(res);
    local_density = (double*)calloc(rec_count,sizeof(double));
    distance_to_higher_density = (double*)calloc(rec_count,sizeof(double));
    gamma = (double*)calloc(rec_count,sizeof(double));

    get_local_density(connect, id_block, channel, dc, local_density, "gaussian");
    get_distance_to_higher_density(connect, id_block, channel, local_density, distance_to_higher_density);

    Quicksort(distance_to_higher_density, local_density, 0, rec_count-1);

    // gamma is rho*delta
    for(i=0; i<rec_count; i++)
    {
        gamma[i] = i*distance_to_higher_density[i];
    }

    //points > 5*mean are centers of cluster
    meanf = mean(gamma, rec_count);

    centers[0] = 0;
    for(i=0; i<rec_count; i++)
    {
        if (gamma[i] > 2.5*meanf)
        {
            //sscanf(PQgetvalue(res, i, 0),"%lf",&centers[(int)centers[0]+1]);
            centers[(int)centers[0]+1] = i;
            centers[0]++;
        }
    }
    return 0;
    // centers contains index of spike centers, centers[0] is lenght of center
}

/**
  @brief From a center, returns all spikes ids with distance minor than dc to the center

  @param connect, string of data connect. See example.
  @param id_block, id project block.
  @param channel, index of channel.
  @param center, index of the center of cluster to returned
  @param cluster, array where the cluster are returned, it contains ids of spikes.
  @param dc, see get_dc .

  @returns Code Error (TODO)

  \verbatim
      float      dc;
      char connect[] = "dbname=demo host=192.168.2.2 user=postgres password=postgres";
      double* centers = (double*)calloc(1026,sizeof(double));
      double* cluster = (double*)calloc(1026,sizeof(double));

      dc = get_dc(connect, "54", "3", 2);

      get_centers_cluster_dp(connect, "54", "3", centers, dc);
      get_cluster_dp(connect, "54", "3", centers[2], cluster, dc);

   \endverbatim

  */
int get_cluster_dp(char connect[], char id_block[], char channel[], double center, double* cluster, double dc)
{
    PGconn          *conn;
    PGresult        *res;
    int             rec_count;

    char query[250];
    int i, j;
    float distance;
    float x1, x2, y1, y2, z1, z2, aux;

    conn = PQconnectdb(connect);

    strcpy(query, "SELECT spike.id, spike.p1, spike.p2, spike.p3 from SPIKE ");
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
    rec_count = PQntuples(res);

    i = 1;
    for(j=0; j<rec_count; j++)
    {
        sscanf(PQgetvalue(res, center, 1),"%f",&x1);
        sscanf(PQgetvalue(res, center, 2),"%f",&y1);
        sscanf(PQgetvalue(res, center, 3),"%f",&z1);
        sscanf(PQgetvalue(res, j, 1),"%f",&x2);
        sscanf(PQgetvalue(res, j, 2),"%f",&y2);
        sscanf(PQgetvalue(res, j, 3),"%f",&z2);
        distance = get_distance(x1, y1, z1, x2, y2, z2);

        if (distance <= dc)
        {
            sscanf(PQgetvalue(res, j, 0), "%f", &aux);
            cluster[i] = (double)aux;
            i++;
        }
        cluster[0] = i;
    }
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


int main(int argc, char* argv[])
{
    //float dc = 0;
    int i;
    double* local_density = (double*)calloc(1026,sizeof(double));
    double* distance_to_higher_density = (double*)calloc(1026,sizeof(double));
    //double* gamma = (double*)calloc(1026,sizeof(double));
    double* centers = (double*)calloc(1026,sizeof(double));
    double* cluster = (double*)calloc(1026,sizeof(double));
    //double** clusters;
//
    float dc = get_dc("dbname=demo host=192.168.2.2 user=postgres password=postgres", "54", "3", 2);
//
//    get_local_density("dbname=demo host=192.168.2.2 user=postgres password=postgres", "54", dc, local_density, "gaussian");
//
//    get_distance_to_higher_density("dbname=demo host=192.168.2.2 user=postgres password=postgres", "54",local_density, distance_to_higher_density, 1026);
//
    get_centers_cluster_dp("dbname=demo host=192.168.2.2 user=postgres password=postgres", "54", "3", centers, dc);

    get_cluster_dp("dbname=demo host=192.168.2.2 user=postgres password=postgres", "54", "3", centers[2], cluster, dc);
//
//    clusters = get_cluster_dp("dbname=demo host=192.168.2.2 user=postgres password=postgres", "54", centers);

    return 1;
}


/*
double* get_centers_cluster_dp(char connect[], char id_block[])
{
    PGconn          *conn;
    PGresult        *res;
    int             rec_count;

    char query[200];
    float dc;
    double* local_density;
    double* distance_to_higher_density;
    double* gamma;
    float meanf;
    double* centers = NULL;
    int k=0, i;

    conn = PQconnectdb(connect);

    strcpy(query,"SELECT spike.id, spike.p1, spike.p2, spike.p3 from SPIKE JOIN  segment ON id_segment = segment.id WHERE segment.id_block = ");
    strcat(query, id_block);

    if (PQstatus(conn) == CONNECTION_BAD) {
        puts("cluster_dp: We were unable to connect to the database");
        return NULL;
    }

    res = PQexec(conn,query);
    rec_count = PQntuples(res);
    local_density = (double*)calloc(rec_count,sizeof(double));
    distance_to_higher_density = (double*)calloc(rec_count,sizeof(double));
    gamma = (double*)calloc(rec_count,sizeof(double));

    dc = get_dc("dbname=demo host=192.168.2.2 user=postgres password=postgres", "54", 2);

    get_local_density("dbname=demo host=192.168.2.2 user=postgres password=postgres", "54", dc, local_density, "gaussian");
    get_distance_to_higher_density("dbname=demo host=192.168.2.2 user=postgres password=postgres", "54",local_density, distance_to_higher_density);

    Quicksort(distance_to_higher_density, local_density, 0, rec_count-1);

    // gamma is rho*delta
    for(i=0; i<rec_count; i++)
    {
        gamma[i] = i*distance_to_higher_density[i];
    }

    //points > 5*mean are centers of cluster
    meanf = mean(gamma, rec_count);
    centers = (double*)malloc(sizeof(double));

    centers[0] = 0;
    for(i=0; i<rec_count; i++)
    {
        if (gamma[i] > 2.5*meanf)
        {
            centers = (double*)realloc(centers, sizeof(double)*(centers[0]+1));
            //sscanf(PQgetvalue(res, i, 0),"%lf",&centers[(int)centers[0]+1]);
            centers[(int)centers[0]+1] = i;
            centers[0]++;
        }
    }
    // centers contains index of spike centers, centers[0] is lenght of center
    return centers;
}*/

/*double** get_cluster_dp(char connect[], char id_block[], double* centers)
{
    PGconn          *conn;
    PGresult        *res;
    int             rec_count;

    char query[200];
    int i, j;
    double** clusters;
    float dc, distance;
    float x1, x2, y1, y2, z1, z2, aux;

    conn = PQconnectdb(connect);

    strcpy(query,"SELECT spike.id, spike.p1, spike.p2, spike.p3 from SPIKE JOIN  segment ON id_segment = segment.id WHERE segment.id_block = ");
    strcat(query, id_block);

    if (PQstatus(conn) == CONNECTION_BAD) {
        puts("cluster_dp: We were unable to connect to the database");
        return NULL;
    }

    res = PQexec(conn,query);
    rec_count = PQntuples(res);

    dc = get_dc("dbname=demo host=192.168.2.2 user=postgres password=postgres", "54", 2);
    if((centers != NULL)&&(centers[0] > 0))
    {
        clusters = (double**)malloc(sizeof(double*)*centers[0]);
        for(i=1; i<centers[0]+1; i++)
        {
            clusters[i-1] = (double*)calloc(1,sizeof(double));
            for(j=0; j<rec_count; j++)
            {
                sscanf(PQgetvalue(res, centers[i], 1),"%f",&x1);
                sscanf(PQgetvalue(res, centers[i], 2),"%f",&y1);
                sscanf(PQgetvalue(res, centers[i], 3),"%f",&z1);
                sscanf(PQgetvalue(res, j, 1),"%f",&x2);
                sscanf(PQgetvalue(res, j, 2),"%f",&y2);
                sscanf(PQgetvalue(res, j, 3),"%f",&z2);
                distance = get_distance(x1, y1, z1, x2, y2, z2);
                if (distance <= dc/4)
                {
                    clusters[i-1] = (double*)realloc(clusters[i-1], sizeof(double)*(clusters[i-1][0]+2));
                    sscanf(PQgetvalue(res, j, 0), "%f", &aux);
                    clusters[i-1][(int)clusters[i-1][0]+1] = (double)aux;
                    clusters[i-1][0]++;
                }
            }
        }
    }

    return clusters;
}*/
