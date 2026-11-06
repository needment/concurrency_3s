#include <stdio.h>
#include <thread>
#include <vector>
#include "../common/CycleTimer.h"

struct WorkerArgs {
    float x0, y0, x1, y1;
    int width;
    int height;
    int maxIterations;
    int* output;
    int threadId;
    int numThreads;
};

extern void mandelbrotSerial(
    float x0, float y0, float x1, float y1,
    int width, int height,
    int startRow, int numRows,
    int maxIterations,
    int output[]);

void workerThreadStart(WorkerArgs * const args) {
    double startTime = CycleTimer::currentSeconds();

    // Блочное разбиение: каждый поток получает непрерывный блок строк
    int totalRows = args->height;
    int rowsPerThread = totalRows / args->numThreads;
    int startRow = args->threadId * rowsPerThread;
    int numRows = (args->threadId == args->numThreads - 1) 
                  ? (totalRows - startRow) 
                  : rowsPerThread;

    mandelbrotSerial(args->x0, args->y0, args->x1, args->y1,
                     args->width, args->height,
                     startRow, numRows,
                     args->maxIterations, args->output);

    double endTime = CycleTimer::currentSeconds();
    // Пункт 3: Замер времени каждого потока
    // printf("[Поток %d]: %.3f мс\n", args->threadId, (endTime - startTime) * 1000);
}

void mandelbrotThread(
    int numThreads,
    float x0, float y0, float x1, float y1,
    int width, int height,
    int maxIterations, int output[])
{
    static constexpr int MAX_THREADS = 32;
    if (numThreads > MAX_THREADS) {
        fprintf(stderr, "Error: Max %d threads\n", MAX_THREADS);
        exit(1);
    }

    std::thread workers[MAX_THREADS];
    WorkerArgs args[MAX_THREADS];

    for (int i = 0; i < numThreads; ++i) {
        args[i].x0 = x0; args[i].y0 = y0; args[i].x1 = x1; args[i].y1 = y1;
        args[i].width = width; args[i].height = height;
        args[i].maxIterations = maxIterations;
        args[i].output = output;
        args[i].threadId = i;
        args[i].numThreads = numThreads;
    }

    for (int i = 1; i < numThreads; ++i) {
        workers[i] = std::thread(workerThreadStart, &args[i]);
    }
    workerThreadStart(&args[0]);

    for (int i = 1; i < numThreads; ++i) {
        workers[i].join();
    }
}