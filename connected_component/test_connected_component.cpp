#include <vector>
#include <stdio.h>
#include <iostream>
#include <stack>
//#include <opencv2/core.hpp>

int main()
{
  std::vector<char> tactile_data = {  1,1,0,0,0,0,
                                      1,0,1,0,0,0,
                                      0,1,1,0,0,0,
                                      0,0,0,1,0,0,
                                      0,0,0,0,1,1,
                                      0,1,0,0,0,0 };
  int rows = 6;
  int cols = 6;
  int dx[4] = {1, 0, -1, 0};
  int dy[4] = {0, 1, 0, -1};

  std::vector<char> tactile_lable(tactile_data);
  std::vector<char> tactile_max_area(sizeof(tactile_data));//init empty to store max connected area
  int label = 1;  // start by 2
  int current_index = -1;
  for (int i = 0; i < rows; ++i){
    for (int j = 0; j < cols; ++j){
      ++current_index;
      int current_area = 0;//record this compon 
      //std::cout<<i<<j;
      if(tactile_lable[current_index] == 1){//find a connected component not visited
        std::stack<int> neiborindex;
        neiborindex.push(current_index);
        ++label;
        while(!neiborindex.empty()){
          // get the top pixel on the stack 
          auto current_neibor_index = neiborindex.top();
          // label it with the same label of current component
          tactile_lable.at(current_neibor_index) = label;
          // pop the top pixel
          ++current_area;
          neiborindex.pop();
          // push the foreground pixels (4 or 8-neighbors)
          for (int k = 0; k < 4; ++k) {
            int y = current_neibor_index/cols + dy[k];
            int x = current_neibor_index%rows + dx[k];
            int temp_index = current_neibor_index + dx[k] + dy[k] * cols;
            if (x < 0 || x >= cols || y < 0 || y >= rows) {//out of space
              continue;
            }
            else if (tactile_lable.at(temp_index) == 1){//neibor pixcel not visited
              neiborindex.push(temp_index);
              //std::cout<<"x="<<x<<",y="<<y<<",index="<<temp_index<<"; ";
            }
          }//end of for k
        }//end of while(!neiborindex.empty())
      }//end of if tactile_lable[current_index]==1, find one connected component
      if(current_area>0)
        std::cout << "this area size = " << current_area << std::endl;
    }
  }
}
