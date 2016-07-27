#include<iostream>
#include "cluster.h"
using namespace std;

Cluster::~Cluster()
{
  // delete vec;
}
Cluster::Cluster(int n, bool d[])
{
  num = n;
  //vec = new bool[n];
  set_vec(d);
}

void Cluster::set_vec(bool d[])
{
  for (int i=0;i<num; i++)
    {
      vec[i] = d[i];
    }
}

bool* Cluster::get_vec()
{
  return vec;
}

void Cluster::set_num(int n)
{
  num = n;
}

void Cluster::make_and(Cluster  *c){
  for (int i=0; i<num; i++)
    {
      vec[i] = c->get_i(i) && vec[i];
    }
}
void Cluster::make_or(Cluster  *c){
  for (int i=0; i<num; i++)
    {
      vec[i] = c->get_i(i) || vec[i];
    }
}

void Cluster::make_not(){
  for (int i=0; i<num; i++)
    {
      vec[i] = !vec[i];
    }
}

void Cluster::print_vec() const{
  for (int i=0; i<num; i++)
    {
      cout<<vec[i];
    }
  cout<<endl;
}

bool Cluster::get_i(int i) const{
  return vec[i];
}

int Cluster::get_num() const {
  return num;
}

bool Cluster::condicion(Cluster *c1,Cluster *c2){
  int i =0;
  for (i=0;
       (i<num && !(((!vec[i]) && c1->get_i(i) && (!c2->get_i(i))) ||
                   ((vec[i]) && (!c1->get_i(i)) && (c2->get_i(i)))));
        i++)
    {
      //
    }
  return i>=num;
  
}

// int main()
// {
//   bool a[12] = {1,0,1,1,1,0,0,1,0,1,0,1};
//   Cluster c(12, a);
//   cout << "Valor:"<< c.get_i(4);
// }
