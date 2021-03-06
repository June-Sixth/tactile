#include "outlier.h"
#include "filter.h"
#include "connected_component.h"

int main()
{
  //vector<int> tactile_data = {-1,1,1,2,-2,2,3,3,-3,4,-4,4};
  std::vector <int> tactile_data = { 1,1,0,0,0,0,
                                      1,0,1,0,0,0,
                                      0,1,1,0,0,0,
                                      0,0,0,1,0,0,
                                      0,0,0,0,0,1,
                                      0,1,0,0,0,0 };
  int rows = 6;
  int cols = 6;
  std::vector <char> tactile_data_outered;
  tactile_data_outered = max_connected_component(tactile_data, rows, cols, 1);
  int current_index = -1;
  for (int i = 0; i < rows; ++i){
    for (int j = 0; j < cols; ++j){
      ++current_index;
      std::cout<<(int)tactile_data_outered.at(current_index);
    }
    std::cout<<std::endl;
  }

  return 0;
}