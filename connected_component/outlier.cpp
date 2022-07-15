#include "outlier.h"

using namespace std;
vector<bool> outlier_f(const vector<bool>& tactile_valids_, int rows, int cols){
// remove potential outliers
  vector<bool> tactile_valids_tmp(tactile_valids_);
  int current_index;

  int dx8[8] = {1, 0, -1, 0, 1, 1, -1, -1};
  int dy8[8] = {0, 1, 0, -1, 1, -1, -1, 1};
  current_index = -1;
  // printf("tactile_id=%d\n", tactile_id);
  for (int i = 0; i < rows; ++i) {
    for (int j = 0; j < cols; ++j) {
      ++current_index;
      if (!tactile_valids_[current_index]) {
        continue;
      }
      bool flag = false;
      for (int k = 0; k < 8; ++k) {
        int y = i + dy8[k];
        int x = j + dx8[k];
        if (x < 0 || x >= cols || y < 0 || y >= rows) {
          continue;
        }
        flag |= tactile_valids_[current_index + dx8[k] + dy8[k] * cols];
      }
      if (!flag) {
        tactile_valids_tmp[current_index] = false;
      }
    }
  }
  return tactile_valids_tmp;
}


