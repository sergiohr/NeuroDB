#include <iostream>
#include <vector>
#include <math.h>
#include <stdio.h>
using namespace std;

#define DIM 3
#define elif else if

#ifndef bool
    #define bool int
    #define false ((bool)0)
    #define true  ((bool)1)
#endif

struct Point3d {
    double x;
    double y;
    double z;
    Point3d(double xin, double yin, double zin) : x(xin), y(yin), z(zin) {}
};

void dataPro(vector<vector<double> > &src, vector<Point3d> &dst){
    for(int i = 0; i < src.size(); i++){
        Point3d pt(src[i][0], src[i][1], src[i][2]);
        dst.push_back(pt);
    }
}

double getDistance(Point3d &pt1, Point3d &pt2){
    double tmp = pow(pt1.x - pt2.x, 2) + pow(pt1.y - pt2.y, 2) + pow(pt1.z - pt2.z, 2);
    return pow(tmp, 0.5);
}

double getdc(vector<Point3d> &data, double neighborRateLow, double neighborRateHigh){
    int nSamples = data.size();
    int nLow = neighborRateLow * nSamples * nSamples;
    int nHigh = neighborRateHigh * nSamples * nSamples;
    double dc = 0.0;
    int neighbors = 0;
    cout<<"nLow = "<<nLow<<", nHigh = "<<nHigh<<endl;
    while(neighbors < nLow || neighbors > nHigh){
    //while(dc <= 1.0){
        neighbors = 0;
        for(int i = 0; i < nSamples - 1; i++){
            for(int j = 0; j < nSamples; j++){
                if(i == j) continue;
                if(getDistance(data[i], data[j]) <= dc) ++neighbors;
                if(neighbors > nHigh) goto DCPLUS;
            }
        }
DCPLUS: dc += 0.03;
        cout<<"dc = "<<dc<<", neighbors = "<<neighbors<<endl;
    }
    return dc;
}

vector<int> getLocalDensity(vector<Point3d> &points, double dc){
    int nSamples = points.size();
    vector<int> rho(nSamples, 0);
    for(int i = 0; i < nSamples - 1; i++){
        for(int j = i + 1; j < nSamples; j++){
            if(getDistance(points[i], points[j]) < dc){
                ++rho[i];
                ++rho[j];
            }
        }
        //cout<<"getting rho. Processing point No."<<i<<endl;
    }
    return rho;
}

vector<double> getDistanceToHigherDensity(vector<Point3d> &points, vector<int> &rho){
    int nSamples = points.size();
    vector<double> delta(nSamples, 0.0);

    for(int i = 0; i < nSamples; i++){
        double dist = 0.0;
        bool flag = false;
        for(int j = 0; j < nSamples; j++){
            if(i == j) continue;
            if(rho[j] > rho[i]){
                double tmp = getDistance(points[i], points[j]);
                if(!flag){
                    dist = tmp;
                    flag = true;
                }else dist = tmp < dist ? tmp : dist;
            }
        }
        if(!flag){
            for(int j = 0; j < nSamples; j++){
                double tmp = getDistance(points[i], points[j]);
                dist = tmp > dist ? tmp : dist;
            }
        }
        delta[i] = dist;
        //cout<<"getting delta. Processing point No."<<i<<endl;
    }
    return delta;
}

int main(int argc, char** argv)
{
    long start, end;
    FILE *input;
    input = fopen("dataset.txt", "r");
    vector<vector<double> > data;
    double tpdouble;
    int counter = 0;
    while(1){
        if(fscanf(input, "%lf", &tpdouble)==EOF) break;
        if(counter / 3 >= data.size()){
            vector<double> tpvec;
            data.push_back(tpvec);
        }
        data[counter / 3].push_back(tpdouble);
        ++ counter;
    }
    fclose(input);
    //random_shuffle(data.begin(), data.end());

    start = clock();
    cout<<"********"<<endl;
    vector<Point3d> points;
    dataPro(data, points);
    double dc = getdc(points, 0.016, 0.020);
    vector<int> rho = getLocalDensity(points, dc);
    vector<double> delta = getDistanceToHigherDensity(points, rho);
//    saveToTxt(rho, delta);
    // now u get the cluster centers
    end = clock();
    cout<<"used time: "<<((double)(end - start)) / CLOCKS_PER_SEC<<endl;
    return 0;
}
