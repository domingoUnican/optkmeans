#include<string>
#include<set>
#include<cstdlib>
#include<iostream>
#include<list>
#include<fstream>
#include<sstream>
#include "mat_RR.h"
#include "cluster.h"
using namespace std;
//#include "omp.h"
#define FILAS 100
#define COLUMNAS 100


bool Comp( const Cluster &s1, const Cluster &s2)
{
    for (int i=0; i<s1.get_num();i++)
      {
        if (!s1.get_i(i) && s2.get_i(i))
          {
            return true;
          }
        else if (s1.get_i(i) && !s2.get_i(i))
          {
            return false;
          }
      }
    return false;
}


void lectura_reales(char* nombre, mat_RR& M ){
    string::size_type sz;
    ifstream fich;
    string linea,token;
    int c_filas, c_columnas;
    c_filas = 0;
    c_columnas = 0;
    fich.open(nombre);
    if (fich.is_open()){
        while (getline(fich,linea)){
            c_columnas =0;
            istringstream iss(linea);
            while (getline(iss,token,',')){
                if (c_columnas<M.NumCols() && c_filas<M.NumRows())
                {
                    M.set(c_filas, c_columnas, atof(token.c_str()));
                    c_columnas ++;
                }
            }
            c_filas ++;
        }
    }
    fich.close();
}

void lectura_enteros(char* nombre, matrix& M ){
    string::size_type sz;
    ifstream fich;
    string linea,token;
    int c_filas, c_columnas;
    c_filas = 0;
    c_columnas = 0;
    fich.open(nombre);
    if (fich.is_open()){
        while (getline(fich,linea)){
            c_columnas =0;
            istringstream iss(linea);
            while (getline(iss,token,',')){
                if (c_columnas<M.NumCols() && c_filas<M.NumRows())
                {
		  M.set(c_filas,c_columnas, atoi(token.c_str()));
                    c_columnas ++;
                }
            }
            c_filas ++;
        }
    }
    fich.close();
}

void lectura_bool(char* nombre, list<Cluster>* h, int cols ){
  string::size_type sz;
  ifstream fich;
  string linea,token;
  int c_columnas;
  bool temp[cols];
  c_columnas = 0;
  fich.open(nombre);
  if (fich.is_open()){
    while (getline(fich,linea)){
      c_columnas =0;
      istringstream iss(linea);
      while (getline(iss,token,',')){
        if (c_columnas<cols)
          {
            temp[c_columnas] = atoi(token.c_str());
            c_columnas++;
          }

      }
      Cluster c(cols, temp);
      h->push_front(c);
    }
  }
  fich.close();
}

float intra_cluster(int* c, int pos, int len, mat_RR& values)
{
  int n_cols = values.NumCols() ;
  float v[n_cols];
  for (int i =0; i<n_cols;i++)
    {
      v[i]=0.0;
    }
  for (int it = 0 ; it<pos; it++)
    {
      for (int j=0;j<n_cols;j++)
        {
          v[j] = v[j]+values.get(c[it],j);
        }
    }
  
  float num_puntos = pos;
  if (pos >0)
    {
      float pos1 = 1/float(pos);
      for (int i =0; i<n_cols;i++)
        {
          v[i]=v[i]*pos1;
        }
      // for (int j=0;j<n_cols;j++)
      //   {
      //     cout <<v[j]<<",";
      //   }
      // cout <<endl;
      pos1 = 0.0;
      float temp_rr = 0;
      for (int it = 0; it < pos; it++ )
        {
          for (int j=0;j<n_cols;j++)
            {
              pos1 = pos1 +(v[j]-values.get((c[it]),j))*(v[j]-values.get((c[it]),j));
            }
        }
      return (pos1);
    }
  else{
    // cout << "Vacio"<<endl;
    // cout << "num_puntos:"<<num_puntos<<endl;
    // cout << "medida intracluster:"<<0<<endl;
    return float(0.0);
  }
}


float minimum_cluster(list<Cluster>* l, mat_RR& m_float)

{
  list<Cluster>::iterator it_1,it_2,it_3;
  float intra_c1,intra_c2,intra_c3;
  float minimo;
  for(int temp_i=0;temp_i<m_float.NumRows();temp_i++)
    {
      for(int temp_j=0;temp_j<m_float.NumCols();temp_j++)
        {
          minimo += m_float.get(temp_i,temp_j)*m_float.get(temp_i,temp_j)+1;
        }
    }
  int longitud_lista = l->size();
  Cluster *array_c = new Cluster[longitud_lista];
  int longitud_temp3=0;
  int longitud_temp1=0;
  int longitud_temp2=0;
  //omp_set_num_threads(1);
  for (list<Cluster>::iterator it_1 = l->begin();
       it_1 != l->end();++it_1)
    {
      array_c[longitud_temp1].set_num((*it_1).get_num());
      array_c[longitud_temp1].set_vec((*it_1).get_vec());
      longitud_temp1++;
    }
  int n_cols = array_c[0].get_num();
  Cluster cluster1,cluster2,cluster3,cluster_not;
  cluster1.set_num(array_c[0].get_num());
  cluster2.set_num(array_c[0].get_num());
  cluster3.set_num(cluster1.get_num());
  bool gran_matrix[longitud_lista][n_cols];
  for(int temp_i=0;temp_i<longitud_lista;temp_i++)
  {
      for(int temp_j=0;temp_j<n_cols;temp_j++)
      {
          gran_matrix[temp_i][temp_j] = array_c[temp_i].get_i(temp_j);
      }
  }

  int lt1=0;
  int lt2=0;
  int lt3=0;
  #pragma omp parallel private(lt1,lt2,lt3,intra_c1,intra_c2,intra_c3) shared(minimo)
  {
    #pragma omp for schedule(static,10) reduction(min:minimo)
  for (int lt1=0;lt1<longitud_lista;lt1++)
    {
      //#pragma omp for schedule(dynamic,20) nowait
      for (int lt2=0;lt2<longitud_lista;lt2++)
        {
          int pos1 = 0;
          int c_v1[n_cols];
          for (int k=0; k<n_cols; k++)
            {
              if (gran_matrix[lt1][k] && gran_matrix[lt2][k])
                {
                  c_v1[pos1]= k;
                  pos1++;
                }
            }
          intra_c1 = intra_cluster(c_v1, pos1, n_cols, m_float);
          for (int lt3=0;lt3<longitud_lista && intra_c1*3<=minimo;)
            {
              int c_v2[n_cols], c_v3[n_cols];
              int pos2 = 0;
              int pos3 = 0;
              int k = 0;
              for (;
                   (k<n_cols) && ((gran_matrix[lt1][k] == gran_matrix[lt2][k]) ||  gran_matrix[lt2][k] == gran_matrix[lt3][k]);
                   k++)
                {
                  if (!gran_matrix[lt1][k] && gran_matrix[lt3][k])
                    {
                      c_v2[pos2]= k;
                      pos2++;
                    }
                  else if (!gran_matrix[lt2][k] && !gran_matrix[lt3][k])
                    {
                      c_v3[pos3]= k;
                      pos3++;
                    }
                }
              if (k<n_cols) 
                {
                  while (gran_matrix[lt2][k] != gran_matrix[lt3][k] && lt3<longitud_lista)
                    {
                      lt3++;
                    }
                }
              else
                {
                  intra_c2 = intra_cluster(c_v2, pos2, n_cols, m_float);
                  intra_c3 = intra_cluster(c_v3, pos3, n_cols, m_float);                 
                  minimo = min(minimo,intra_c1+intra_c2+intra_c3);
                  lt3++;
                }
            }
        }
    }
  }
  delete[] array_c;
  return minimo;
}




int main(int argc, char* argv[]){
  if (argc<3){
    cout<<"Uso: hay que poner los argumentos separados por ";
    cout<<"espacios"<<endl;
    cout<<"nombre_fichero numero_filas numero_columnas clusters";
    cout<<" nombre_fichero_k=2";
    cout<<endl;
  }
  char* datos = argv[1];
  int n_filas = atoi(string(argv[2]).c_str());
  int n_col = atoi(string(argv[3]).c_str());
  int k = atoi(string(argv[4]).c_str());
  char* temp = argv[5];
  mat_RR m_float;  
  matrix m_int;
  list<Cluster> l;
  m_float.SetDims(n_filas,n_col);
  m_int.SetDims(n_filas,n_col);
  lectura_reales(datos,m_float);
  lectura_bool(temp,&l,n_filas);
  list<Cluster>::iterator it_1;
  cout << minimum_cluster(&l,m_float)<<endl; 
}
