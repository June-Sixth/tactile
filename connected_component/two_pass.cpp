#include <opencv2/opencv.hpp>
#include <vector>
using namespace cv;
using namespace std;
void TwoPassLabel(const Mat &bwImg, Mat &labImg)
{
	assert(bwImg.type() == CV_8UC1);
	bwImg.convertTo(labImg, CV_32SC1);
	int rows = bwImg.rows -1;
	int cols = bwImg.cols -1;

	//二值图像像素值为0或1，为了不冲突，label从2开始
	int label = 2;
	vector<int> labelSet;
	labelSet.push_back(0);
	labelSet.push_back(1);

	//第一次扫描
	int *data_prev = (int*)labImg.data;
	int *data_cur = (int*)(labImg.data + labImg.step);
	int left, up;//指针指向的像素点的左方点和上方点
	int neighborLabels[2];
	for (int i = 1; i < rows; i++)// 忽略第一行和第一列,其实可以将labImg的宽高加1，然后在初始化为0就可以了
	{
		data_cur++;
		data_prev++;
		for (int j = 1; j < cols; j++, data_cur++, data_prev++)
		{
			if (*data_cur != 1)//当前点不为1，扫描下一个点
				continue;
			left = *(data_cur - 1);
			up = *data_prev;

			int count = 0;
			for (int curLabel : {left, up})
			{
				if (curLabel > 1)
					neighborLabels[count++] = curLabel;
			}

			if (!count)//赋予一个新的label
			{
				labelSet.push_back(label);
				*data_cur = label;
				label++;
				continue;
			}
			//将当前点标记设为左点和上点label的最小值
			int smallestLabel = neighborLabels[0];
			if (count == 2 && neighborLabels[1] < smallestLabel)
				smallestLabel = neighborLabels[1];
			*data_cur = smallestLabel;
			//设置等价表，这里可能有点难理解
			//左点有可能比上点小，也有可能比上点大，两种情况都要考虑,例如
			//0 0 1 0 1 0       x x 2 x 3 x
			//1 1 1 1 1 1  ->   4 4 2 2 2 2
			//要将labelSet中3的位置设置为2
			for (int k = 0; k < count; k++)
			{
				int neiLabel = neighborLabels[k];
				int oldSmallestLabel = labelSet[neiLabel];
				if (oldSmallestLabel > smallestLabel)
				{
					labelSet[oldSmallestLabel] = smallestLabel;
				}
				else if (oldSmallestLabel<smallestLabel)
					labelSet[smallestLabel] = oldSmallestLabel;
			}
		}
		data_cur++;
		data_prev++;
	}
	//上面一步中,有的labelSet的位置还未设为最小值，例如
	//0 0 1 0 1      x x 2 x 3
	//0 1 1 1 1  ->  x 4 2 2 2
	//1 1 1 0 1      5 4 2 x 2
	//上面这波操作中，把labelSet[4]设为2，但labelSet[5]仍为4
	//这里可以将labelSet[5]设为2
	for (size_t i = 2; i < labelSet.size(); i++)
	{
		int curLabel = labelSet[i];
		int prelabel = labelSet[curLabel];
		while (prelabel != curLabel)
		{
			curLabel = prelabel;
			prelabel = labelSet[prelabel];
		}
		labelSet[i] = curLabel;
	}
	//第二次扫描，用labelSet进行更新，最后一列
	data_cur = (int*)labImg.data;
	for (int i = 0; i < rows; i++)
	{
		for (int j = 0; j < cols; j++, data_cur++)
			*data_cur = labelSet[*data_cur];
		data_cur++;
	}

	return ;
}
