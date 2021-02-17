#include <iostream>
#include <cstring>
#include <string>
#include <unistd.h>
using namespace std;

#include "CAENHVWrapper.h"

int main() {

  //void *parlist[100];
  int handle = 0;
  int handle2 = 0;

  std::string myip = ("142.90.105.151");
  //unsigned short chan[] = {1, 3};
  //char chan_name[50][12];
  int return_val = 0;
  //int chan_num;
  //char *chan_info_list;

  return_val = CAENHV_InitSystem(13, 0, myip.c_str(), ' ', ' ', &handle);
  cout << "My Return value : " << return_val << "\n";

//  CAENHV_GetChName(handle, 0, 2, chan, chan_name);
//  CAENHV_GetChParamInfo(handle, 0, 2, &chan_info_list, &chan_num);
//  for(int i = 0; i<chan_num; i++) {
//    chan_info_list += 10;
//    cout << chan_info_list<<"\n";
//  }

  //cout << chan_info_list << "\n";
  CAENHV_DeinitSystem(handle);
  sleep(2);
  free(handle);
  handle = NULL;
  return_val = CAENHV_InitSystem(13, 0, myip.c_str(), ' ', ' ', &handle2);
  cout << "My Return value : " << std::hex << return_val << "\n";


  CAENHV_DeinitSystem(handle2);

  return 0;
}
