#include <iostream>
#include <cstring>
#include <string>
#include <unistd.h>
using namespace std;

#include "CAENHVWrapper.h"

int main() {

  int handle = 0;
  int handle2 = 0;
  std::string myip = ("142.90.105.151");
  int return_val = 0;

  return_val = CAENHV_InitSystem(13, 0, myip.c_str(), ' ', ' ', &handle);
  cout << "My Return value : " << return_val << "\n";

  CAENHV_DeinitSystem(handle);
  sleep(2);
  free(handle);
  handle = NULL;

  return_val = CAENHV_InitSystem(13, 0, myip.c_str(), ' ', ' ', &handle2);
  cout << "My Return value : " << std::hex << return_val << "\n";
  CAENHV_DeinitSystem(handle2);

  return 0;
}
