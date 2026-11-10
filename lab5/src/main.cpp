#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <cstring>
#include <algorithm>

#include "../common/CycleTimer.h"

extern void mandelbrotSerial(
    float x0, float y0, float x1, float y1,
    int width, int height,
    int startRow, int numRows,
    int maxIterations,
    int output[]);

extern void mandelbrotThread(
    int numThreads,
    float x0, float y0, float x1, float y1,
    int width, int height,
    int maxIterations,
    int output[]);

extern void writePPMImage(
    int* data,
    int width, int height,
    const char *filename,
    int maxIterations);

void scaleAndShift(float& x0, float& x1, float& y0, float& y1,
                   float scale,
                   float shiftX, float shiftY)
{
    x0 *= scale;
    x1 *= scale;
    y0 *= scale;
    y1 *= scale;
    x0 += shiftX;
    x1 += shiftX;
    y0 += shiftY;
    y1 += shiftY;
}

void usage(const char* progname) {
    printf("Usage: %s [options]\n", progname);
    printf("Program Options:\n");
    printf("  -t  --threads <N>  Use N threads\n");
    printf("  -v  --view <INT>   Use specified view settings\n");
    printf("  -?  --help         This message\n");
}

bool verifyResult(int *gold, int *result, int width, int height) {
    for (int i = 0; i < height; i++) {
        for (int j = 0; j < width; j++) {
            if (gold[i * width + j] != result[i * width + j]) {
                printf("Mismatch : [%d][%d], Expected : %d, Actual : %d\n",
                       i, j, gold[i * width + j], result[i * width + j]);
                return false;
            }
        }
    }
    return true;
}

int main(int argc, char** argv) {
    const unsigned int width = 1600;
    const unsigned int height = 1200;
    const int maxIterations = 256;
    int numThreads = 2;

    float x0 = -2;
    float x1 = 1;
    float y0 = -1;
    float y1 = 1;

    // parse commandline options
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if ((arg == "-t" || arg == "--threads") && i + 1 < argc) {
            numThreads = atoi(argv[++i]);
        } else if ((arg == "-v" || arg == "--view") && i + 1 < argc) {
            int viewIndex = atoi(argv[++i]);
            if (viewIndex == 2) {
                float scaleValue = .015f;
                float shiftX = -.986f;
                float shiftY = .30f;
                scaleAndShift(x0, x1, y0, y1, scaleValue, shiftX, shiftY);
            } else if (viewIndex > 1) {
                fprintf(stderr, "Invalid view index\n");
                return 1;
            }
        } else if (arg == "-?" || arg == "--help" || arg == "-h") {
            usage(argv[0]);
            return 1;
        }
    }

    int* output_serial = new int[width * height];
    int* output_thread = new int[width * height];

    double minSerial = 1e30;
    for (int i = 0; i < 5; ++i) {
        memset(output_serial, 0, width * height * sizeof(int));
        double startTime = CycleTimer::currentSeconds();
        mandelbrotSerial(x0, y0, x1, y1, width, height, 0, height, maxIterations, output_serial);
        double endTime = CycleTimer::currentSeconds();
        minSerial = std::min(minSerial, endTime - startTime);
    }

    printf("[mandelbrot serial]:\t\t[%.3f] ms\n", minSerial * 1000);
    writePPMImage(output_serial, width, height, "mandelbrot-serial.ppm", maxIterations);

    double minThread = 1e30;
    for (int i = 0; i < 5; ++i) {
        memset(output_thread, 0, width * height * sizeof(int));
        double startTime = CycleTimer::currentSeconds();
        mandelbrotThread(numThreads, x0, y0, x1, y1, width, height, maxIterations, output_thread);
        double endTime = CycleTimer::currentSeconds();
        minThread = std::min(minThread, endTime - startTime);
    }

    printf("[mandelbrot thread]:\t\t[%.3f] ms\n", minThread * 1000);
    writePPMImage(output_thread, width, height, "mandelbrot-thread.ppm", maxIterations);

    if (!verifyResult(output_serial, output_thread, width, height)) {
        printf("Error : Output from threads does not match serial output\n");
        delete[] output_serial;
        delete[] output_thread;
        return 1;
    }

    printf("\t\t\t\t(%.2fx speedup from %d threads)\n", minSerial / minThread, numThreads);

    delete[] output_serial;
    delete[] output_thread;
    return 0;
}