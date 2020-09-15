#include <iostream>
#include <cstring>
#include <string>
using namespace std;

#include "CAENHVWrapper.h"

int main() {
  cout << "Hello\n";
  //int system = 13;
  //int linktype = 0;
  //void *arg;
  //arg = "142.90.105.151";
  void *parlist[100];
  int handle;
  std::string myip = ("142.90.105.151");
  std::string parname = ("Pon");
  unsigned short chan[] = {1, 3};
  char chan_name[50][12];

  int chan_num;
  char *chan_info_list;

//  cout << (char*)myip.c_str();
  CAENHV_InitSystem(13, 0, myip.c_str(), ' ', ' ', &handle);
//  CAENHV_GetChName(handle, 0, 2, chan, chan_name);
  CAENHV_GetChParamInfo(handle, 0, 2, &chan_info_list, &chan_num);
  for(int i = 0; i<chan_num; i++) {
    chan_info_list += 10;
    cout << chan_info_list<<"\n";
  }

  cout << chan_info_list << "\n";
  CAENHV_DeinitSystem(handle);
  return 0;
}
