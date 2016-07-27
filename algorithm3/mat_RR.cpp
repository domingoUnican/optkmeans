#include "mat_RR.h"
#include<iostream>
using namespace std;
mat_RR::mat_RR(int const r, int const c){
  numRows = r;
  numCols = c;
  mat[r-1][c-1] = 1.0;
}
void mat_RR::SetDims(int i, int j){
  numRows=i;
  numCols=j;
}
int mat_RR::NumCols()
{
  return numCols;
}

int mat_RR::NumRows()
{
  return numRows;
}

void mat_RR::set(int i, int j, float value){
  mat[i][j]=value;
}

float mat_RR::get(int i, int j)
{
  return mat[i][j];
}


matrix::matrix(int const r, int const c){
  numRows = r;
  numCols = c;
  mat[r-1][c-1] = 1;
}

int matrix::NumCols()
{
  return numCols;
}

void matrix::SetDims(int i, int j){
  numRows=i;
  numCols=j;
}


int matrix::NumRows()
{
  return numRows;
}

void matrix::set(int i, int j, bool value){
  mat[i][j]=value;
}

bool matrix::get(int i, int j)
{
  return mat[i][j];
}

