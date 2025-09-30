#include <iostream>
#include <random>
#include <cmath>
#include <string>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define AB (1 + (3.0 * M_PI) / 2)

using namespace std;

// Function prototypes

// Function to generate a random double between min and max
double random_double(double min, double max, mt19937 mt);
// Function to get the next odd integer >= value
int next_odd(int value);
// Function to generate a valid odd b within range
int random_valid_b(int min_b, int max_b, mt19937 mt);
// Function to generate random a and b values
double* random_a_b(char* a_p, char* b_p, char* range_p);
// Weierstrass function: W(a, b, x) = sum_{n=0}^{N} a^n * cos(b^n * pi * x)
double weierstrass(double a, double b, double x, int n = 0);
// Weierstrass group function: generates N points in the range [min_x, max_x]
// Returns an array of size N*2+1, where the first element is N,
// followed by pairs of x and y values.
double* weierstrassGroup(double a, double b, double min_x, double max_x, int n = 0, int N = 100);
// Function to free the dynamically allocated double pointer
void freeDblPointer(double* arr);

double random_double(double min, double max, mt19937 mt) {
    uniform_real_distribution<double> dist(min, max);
    return dist(mt);
}

int next_odd(int value) {
    return (value % 2 == 0) ? value + 1 : value;
}

int random_valid_b(int min_b, int max_b, mt19937 mt) {
    if (min_b % 2 == 0) min_b++; // make min odd
    if (max_b % 2 == 0) max_b++; // make max odd

    int count = (max_b - min_b) / 2 + 1;
    uniform_int_distribution<int> int_dist(0, count - 1);
    return min_b + 2 * int_dist(mt);
}

double* random_a_b(char* a_p, char* b_p, char* range_p) {
    random_device rd;
    mt19937 mt(rd());

    double a = random_double(0.1, 0.9, mt);
    int b = random_valid_b(1, 101, mt);
    int range = b;

    if (string(a_p) != "None") a = strtod(a_p, nullptr);
    if (string(b_p) !=  "None") {
        b = strtol(b_p, nullptr, 0);
        range = b;
    }
    if (string(range_p) != "None") {
        int r = strtol(range_p, nullptr, 0);
        if (r > 0) { // Ensure range is positive
            range = r;
            b = random_valid_b(1, range, mt);
        }
    }

    double* result = new double[3];
    result[0] = a;
    result[1] = b;
    result[2] = range;

    return result;
}

double weierstrass(double a, double b, double x, int n) {
    double sum = 0.0;
    for (int i = 0; i <= n; ++i) {
        sum += pow(a, i) * cos(pow(b, i) * M_PI * x);
    }
    return sum;
}

double* weierstrassGroup(double a, double b, double min_x, double max_x, int n, int N) {
    if (N <= 0 || n < 0) return nullptr;
    if (min_x >= max_x) return nullptr;

    double* result = new double[N * 2 + 1];
    result[0] = N; // First element is N
    double step = (max_x - min_x) / N;

    for (int i = 0; i <= N; ++i) {
        double x = min_x + i * step;
        result[i * 2 + 1] = x; // x value
        result[i * 2 + 2] = weierstrass(a, b, x, n); // y value
    }

    return result;
}

void freeDblPointer(double* arr) {
    delete[] arr;
}

int main(int argc, char* argv[]) {
    // Example usage
     // Default values
    double min_x = strtod(argv[4], nullptr);
    double max_x = strtod(argv[5], nullptr);
    int n = strtol(argv[6], nullptr, 10);
    int N = strtol(argv[7], nullptr, 10);
    if (argc < 8) {
        cerr << "Usage: " << argv[0] << " <a> <b> <range> <min_x> <max_x> <n> <N>" << endl;
        return 1;
    }
    if (min_x >= max_x) {
        cerr << "Error: min_x must be less than max_x." << endl;
        return 1;
    }
    if (n < 0 || N <= 0) {
        cerr << "Error: n must be non-negative and N must be positive." << endl;
        return 1;
    }

    double* abr = random_a_b(argv[1], argv[2], argv[3]);
    double a = abr[0];
    double b = abr[1];
    double range = abr[2];

    printf("Random a: %.2f, b: %d, range: %d\n", a, static_cast<int>(b), static_cast<int>(range));

    double* group = weierstrassGroup(a, b, min_x, max_x, n, N);

    cout << "Weierstrass Group:" << endl;
    cout << group[0] << " points generated." << endl;
    cout << "x and y values:" << endl;
    for (int i = 0; i <= N; ++i) {
        cout << "(" << i << ") " << "x: " << group[i * 2 + 1] << ", y: " << group[i * 2 + 2] << endl;
    }
    
    return 0;
}