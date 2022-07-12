#include <vector>
#include <opencv2/opencv.hpp>
using namespace std;
using namespace cv;


vector<int> everage_filter(const vector<int>& tactile_data, int rows, int cols){
  int dx8[8] = {1, 0, -1, 0, 1, 1, -1, -1};
  int dy8[8] = {0, 1, 0, -1, 1, -1, -1, 1};
  int current_index = -1;
  vector<int> filted_tactile(sizeof(tactile_data));
  for (int i = 0; i < rows; ++i){
    for (int j = 0; j < cols; ++j){
      ;
    }
  }
}


Mat convertVector2Mat(const vector<int>& tactile_data, int rows, int cols){
  Mat mat = Mat(tactile_data);//vector to 1d mat
  Mat dest = mat.reshape(1,rows).clone();
  dest.convertTo(dest, CV_16SC1);
  return dest;
}

int main()
{
  vector<int> tactile_data = {-1,1,1,2,-2,2,3,3,-3,4,-4,4};
  Mat dest = convertVector2Mat(tactile_data,4,3);
  cout<< dest << endl;
  imshow("test",dest);
  waitKey(0);
  return 0;
}