#include <vector>
#include <stdio.h>
#include <iostream>
//#include <opencv2/core.hpp>

int main()
{
  std::vector<bool> tactile_data = {  1,1,0,0,0,0,
                                      1,0,1,0,0,0,
                                      0,1,1,0,0,0,
                                      0,0,0,1,0,0,
                                      0,0,0,0,1,1,
                                      0,0,0,0,0,0 };
  int rows = 6;
  int cols = 6;
  int dx[4] = {1, 0, -1, 0};
  int dy[4] = {0, 1, 0, -1};

  std::vector<int> tactile_lable(sizeof(tactile_data));
  int label = 1;  // start by 2
  int current_index = -1;
  for (int i = 1; i < rows - 1; i++){
    for (int j = 1; j < cols - 1; j++){
      ++current_index;
      if(!tactile_data[current_index]){
        continue;
      }
      printf("%d ",(int)tactile_data[current_index]);
    }
    printf("\n");
  }

}

  // int table_cnt = 0;
  // for(std::vector<int>::iterator iter = tactile_lable.begin(); iter != tactile_lable.end(); iter++){
  //   table_cnt++;
  //   std::cout<<(*iter)<<" "<<table_cnt<<" ";
  // }