
#include "OpenCVApplication.h"
#include "stdafx.h"
#include <cmath>
#include "common.h"
#include "Functions.h"
#include <string.h>
#include <iostream>
#include <vector>
#include <limits>
#include <string>
#include <numeric>

using namespace std;



void singlehierarchicalClustering(Mat& binaryImage, vector<vector<Point>>& clusters) {
	const int connectivity = 8;
	const int minClusterSize = 5;
	Mat labels, stats, centroids;
	int numLabels = connectedComponentsWithStats(binaryImage,
		labels, stats, centroids, connectivity, CV_32S);

	for (int label = 1; label < numLabels; ++label) {
		if (stats.at<int>(label, CC_STAT_AREA) >= minClusterSize) {
			vector<Point> cluster;
			for (int i = 0; i < binaryImage.rows; ++i) {
				for (int j = 0; j < binaryImage.cols; ++j) {
					if (labels.at<int>(i, j) == label) {
						cluster.push_back(Point(j, i));
					}
				}
			}
			clusters.push_back(cluster);
		}
	}
}

double pointDistance(Point a, Point b) {
	return sqrt((a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y));
}

bool filterByCircle(const vector<Point>& cluster, Point center, double radius) {
	int countOutside = 0;
	for (const auto& point : cluster) {
		double dist = pointDistance(point, center);
		if (dist > radius) {
			countOutside++;
		}
	}
	return (countOutside / static_cast<double>(cluster.size())) > 0.10;
}

void mergeCloseClusters(vector<vector<Point>>& clusters, double distanceThreshold) {

	vector<Point> centroids;
	for (const auto& cluster : clusters) {
		Point sum(0, 0);
		for (const auto& point : cluster) {
			sum += point;
		}
		centroids.push_back(sum / static_cast<int>(cluster.size()));
	}

	vector<vector<Point>> mergedClusters;
	vector<bool> visited(clusters.size(), false);

	for (size_t i = 0; i < clusters.size(); ++i) {
		if (!visited[i]) {
			vector<Point> mergedCluster = clusters[i];
			visited[i] = true;

			queue<size_t> q;
			q.push(i);

			while (!q.empty()) {
				size_t current = q.front();
				q.pop();

				for (size_t j = 0; j < clusters.size(); ++j) {
					if (!visited[j] && pointDistance(centroids[current], centroids[j]) < distanceThreshold) {
						visited[j] = true;
						mergedCluster.insert(mergedCluster.end(), clusters[j].begin(), clusters[j].end());
						q.push(j);
					}
				}
			}

			mergedClusters.push_back(mergedCluster);
		}
	}
	clusters = mergedClusters;
}

void filterClustersOutsideCircle(vector<vector<Point>>& clusters, Point center, double radius) {
	vector<vector<Point>> filteredClusters;
	for (const auto& cluster : clusters) {
		if (!cluster.empty() && !filterByCircle(cluster, center, radius)) {
			filteredClusters.push_back(cluster);
		}
	}
	clusters = filteredClusters;
}

double closestPointsDistance(const vector<Point>& cluster1, const vector<Point>& cluster2) {
	double minDistance = 999999999999999;

	for (const auto& point1 : cluster1) {
		for (const auto& point2 : cluster2) {
			double dist = norm(point1 - point2);
			if (dist < minDistance) {
				minDistance = dist;
			}
		}
	}
	return minDistance;
}

void uniteClusters(vector<vector<Point>>& clusters, double distanceThreshold) {
	// Create a new set of merged clusters
	vector<vector<Point>> mergedClusters;
	vector<bool> visited(clusters.size(), false);

	for (size_t i = 0; i < clusters.size(); ++i) {
		if (!visited[i]) {
			vector<Point> mergedCluster = clusters[i];
			visited[i] = true;

			// Iterate over remaining clusters
			for (size_t j = i + 1; j < clusters.size(); ++j) {
				if (!visited[j]) {
					double dist = closestPointsDistance(clusters[i], clusters[j]);
					if (dist < distanceThreshold) {
						visited[j] = true;
						mergedCluster.insert(mergedCluster.end(), clusters[j].begin(), clusters[j].end());
					}
				}
			}

			mergedClusters.push_back(mergedCluster);
		}
	}

	clusters = mergedClusters;
}


int main(int argc, char* argv[]) {

	string filename_aux;
	

	std::vector<std::string> files;
	string filename = argv[1];
	int end = stoi(argv[2]);
	for (int i = 1; i <= end; ++i) {
		filename_aux = filename + std::to_string(i) + ".png";
		files.push_back(filename_aux);
	}



	char fname[MAX_PATH];

	std::string outputFolder;
	std::string outputFileName;
	std::string outputPath;





	for (int counter = 0; counter < end; counter++)
	{
		Mat binaryImage = imread(files[counter], IMREAD_GRAYSCALE);
		if (binaryImage.empty()) {
			cerr << "Error: Could not open image " << files[counter] << endl;
			continue;
		}


		threshold(binaryImage, binaryImage, 75, 255, THRESH_BINARY);
		GaussianBlur(binaryImage, binaryImage, Size(5, 5), 0);

		Mat element2 = getStructuringElement(MORPH_RECT, Size(2, 2));
		erode(binaryImage, binaryImage, element2, Point(-1, -1), 1);
		dilate(binaryImage, binaryImage, element2, Point(-1, -1), 1);



		vector<vector<Point>> clusters;
		singlehierarchicalClustering(binaryImage, clusters);

		double distanceThreshold = 19;
		mergeCloseClusters(clusters, distanceThreshold);

		Point center(binaryImage.cols / 2, binaryImage.rows / 2);
		double radius = 116.0;
		filterClustersOutsideCircle(clusters, center, radius);


		double distanceThreshold2 = 50;

		Mat clusteredImage = Mat::zeros(binaryImage.size(), CV_8UC3);
		RNG rng(12345);
		for (size_t i = 0; i < clusters.size(); ++i) {
			Vec3b color = Vec3b(rng.uniform(0, 256), rng.uniform(0, 256), rng.uniform(0, 256));
			for (size_t j = 0; j < clusters[i].size(); ++j) {
				clusteredImage.at<Vec3b>(clusters[i][j]) = color;
			}
		}


		Scalar color(0, 0, 255);                        
		int thickness = 2;
		cout << counter << endl;
		outputFolder = "Images/Rezultate_Licenta/";
		outputFileName = std::to_string(counter) + ".png";
		outputPath = outputFolder + outputFileName;
		imwrite(outputPath, clusteredImage);

	}
	return 0;
}
