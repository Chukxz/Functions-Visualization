#include <iostream>
#include <random>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define AB (1 + (3.0 * M_PI) / 2)

using namespace std;
// Function prototypes
double random_double(double min, double max, std::mt19937 mt);
int next_odd(int value);
// Function to generate a valid odd b within range
int random_valid_b(int min_b, int max_b, std::mt19937 mt);

// Export macro for DLL functions
#ifndef EXPORT
#define EXPORT __declspec(dllexport)  
#endif

// Function to generate random a and b values
extern "C" EXPORT double* random_a_b(double* a_p = nullptr, int* b_p = nullptr, int *range_p = nullptr);
// Weierstrass function: W(a, b, x) = sum_{n=0}^{N} a^n * cos(b^n * pi * x)
extern "C" EXPORT double weierstrass(double a, double b, double x, int n = 0);
// Weierstrass group function: generates N points in the range [min_x, max_x]
// Returns an array of size N*2+1, where the first element is N,
// followed by pairs of x and y values.
// The y value is calculated using the Weierstrass function.
extern "C" EXPORT double* weierstrassGroup(double a, double b, double min_x, double max_x, int n = 0, int N = 100);
// Function to free the dynamically allocated double pointer
// This function should be called to avoid memory leaks
extern "C" EXPORT void freeDblPointer(double* arr);

// Function to generate a random double between min and max
double random_double(double min, double max, std::mt19937 mt) {
  std::uniform_int_distribution<int> int_dist(min, max);
  return int_dist(mt);
}

// Function to get the next odd integer >= value
int next_odd(int value) {
  return (value % 2 == 0) ? value + 1: value;
}

// Function to generate a valid odd b within range
int random_valid_b(int min_b, int max_b, std::mt19937 mt) {
  if (min_b % 2 == 0) min_b++; // make min odd
  if (max_b % 2 == 0) max_b++; // make max odd

  int count = (max_b - min_b) / 2 + 1;
  std::uniform_int_distribution<int> int_dist(0, count - 1);
  return min_b + 2 * int_dist(mt);
}

extern "C" {
  double* random_a_b(double* a_p, int* b_p, int *range_p) {
    std::random_device rd;
    std::mt19937 mt(rd());
    double a;
    int b, range;

    if (a_p == nullptr) {
      // Randomize a between 0 (inclusive) and 1 (exclusive)
      std::uniform_real_distribution<double> double_dist(0.0, 1.0);
      a = double_dist(mt);
      while (a == 0.0) a = double_dist(mt);
    }
    else a = *a_p;

    if (b_p == nullptr) {
      // Calculate minimum b and ensure it is an odd integer
      int min_b = std::max(3, next_odd(ceil(AB / a)));

      if (range_p == nullptr) range = 100;
      else range = *range_p;

      // Randomize a valid b within a limited range
      int max_b = min_b + range;
      b = random_valid_b(min_b, max_b, mt);
    }
    else b = *b_p;

    double *arr = new double[3];
    arr[0] = a;
    arr[1] = static_cast<double>(b);
    arr[2] = static_cast<double>(range);

    return arr;
  }

  double weierstrass(double a, double b, double x, int n) {
    double y = 0;
    for (std::size_t i = 0; i <= n; i++){
      y += pow(a, n) * cos(pow(b, n) * M_PI * x);
    }

    return y;
  }

  double* weierstrassGroup(double a, double b, double min_x, double max_x, int n, int N) {
    double delta = (max_x - min_x) / (N - 1);
    double *x_y_values = new double[N*2+1];
    x_y_values[0] = N;

    for (std::size_t i = 0; i < N; i++) {
      double x = min_x + i * delta;
      x_y_values[i*2+1] = x;
      x_y_values[i*2+2] = weierstrass(a, b, x, n);
    }

    return x_y_values;
  }

  void freeDblPointer(double* arr) {
    delete [] arr;
  }
}