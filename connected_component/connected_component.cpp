#include <vector>
#include <stdio.h>
#include <iostream>
#include <stack>
using namespace std;

vector<char> connected_component(const vector<int>& tactile_data, int rows, int cols, int threshold){
  
  int dx[4] = {1, 0, -1, 0};
  int dy[4] = {0, 1, 0, -1};
  vector<char> tactile_label(tactile_data.size());
  for (int i = 0; i < tactile_data.size(); ++i)
    tactile_label[i] = static_cast<char>(tactile_data[i] >= threshold);
  int label = 1;  // start by 2
  int current_index = -1;
  for (int i = 0; i < rows; ++i){
    for (int j = 0; j < cols; ++j){
      ++current_index;
      int current_area = 0;//record this compon 
      //std::cout<<i<<j;
      if(tactile_label[current_index] == 1){//find a connected component not visited
        std::stack<int> neiborindex;
        neiborindex.push(current_index);
        ++label;
        while(!neiborindex.empty()){
          // get the top pixel on the stack 
          auto current_neibor_index = neiborindex.top();
          // label it with the same label of current component
          tactile_label.at(current_neibor_index) = label;
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
            else if (tactile_label.at(temp_index) == 1){//neibor pixcel not visited
              neiborindex.push(temp_index);
              //std::cout<<"x="<<x<<",y="<<y<<",index="<<temp_index<<"; ";
            }
          }//end of for k
        }//end of while(!neiborindex.empty())
      }//end of if tactile_label[current_index]==1, find one connected component
      if(current_area>0)
        std::cout << "this area size = " << current_area << std::endl;
    }
  }
  return tactile_label;
}

vector<char> max_connected_component(const vector<int>& tactile_data, int rows, int cols, int threshold){
  
  int dx[4] = {1, 0, -1, 0};
  int dy[4] = {0, 1, 0, -1};
  vector<char> tactile_label(tactile_data.size());
  for (int i = 0; i < tactile_data.size(); ++i)
    tactile_label[i] = static_cast<char>(tactile_data[i] >= threshold);

  int label = 1;  // start by 2
  int current_index = -1;
  int max_area = 0;//record the max area
  int max_area_val = 0;//record the max area mul val
  int max_area_label = 1;
  for (int i = 0; i < rows; ++i){
    for (int j = 0; j < cols; ++j){
      ++current_index;
      //std::cout<<i<<j;
      if(tactile_label[current_index] == 1){//find a connected component not visited
        int current_area = 0;//record this component area
        int current_area_val = 0;
        std::stack<int> neiborindex;
        neiborindex.push(current_index);
        ++label;
        while(!neiborindex.empty()){
          // get the top pixel on the stack 
          auto current_neibor_index = neiborindex.top();
          // label it with the same label of current component
          tactile_label.at(current_neibor_index) = label;
          // pop the top pixel
          ++current_area;
          current_area_val += tactile_data[current_neibor_index];
          neiborindex.pop();
          // push the foreground pixels (4 or 8-neighbors)
          for (int k = 0; k < 4; ++k) {
            int y = current_neibor_index/cols + dy[k];
            int x = current_neibor_index%rows + dx[k];
            int temp_index = current_neibor_index + dx[k] + dy[k] * cols;
            if (x < 0 || x >= cols || y < 0 || y >= rows) {//out of space
              continue;
            }
            else if (tactile_label.at(temp_index) == 1){//neibor pixcel not visited
              neiborindex.push(temp_index);
              //std::cout<<"x="<<x<<",y="<<y<<",index="<<temp_index<<"; ";
            }
          }//end of for k
        }//end of while(!neiborindex.empty())
        if(current_area > max_area || (current_area == max_area && current_area_val > max_area_val)){
          max_area_label = label;
          max_area = current_area;
          max_area_val = current_area_val;
        }
      }//end of if tactile_label[current_index]==1, find one connected component done
    }
  }
  vector<char> tactile_max_area(tactile_label);//init empty to store max connected area
  for (auto& tactile_iter : tactile_max_area)
    tactile_iter = (tactile_iter == max_area_label? 1:0);
  // for (int i = 0; i < tactile_max_area.size(); ++i){
  //   tactile_max_area[i] = (tactile_max_area[i] == max_area_label? 1:0);
  // }
  return tactile_max_area;
}

void print_tactile_data(const vector<int>& tactile_data, int rows, int cols){
  int current_index = -1;
  for (int i = 0; i < rows; ++i){
    for (int j = 0; j < cols; ++j){
      ++current_index;
      cout<<tactile_data.at(current_index);
    }
    cout<<endl;
  }
}


// int main()
// {
//   std::vector<int> tactile_data = { 1,15,0,0,0,0,
//                                     1,0,2,0,0,0,
//                                     0,1,24,0,0,0,
//                                     0,0,0,1,0,0,
//                                     0,0,0,0,1,1,
//                                     0,1,0,0,0,0 };
//   int rows = 6;
//   int cols = 6;

//   vector<char> tactile_lable = max_connected_component(tactile_data, rows, cols, 1);
//   vector<int> tactile_int2print(tactile_lable.begin(),tactile_lable.end());
//   print_tactile_data(tactile_int2print, rows, cols);
// }

