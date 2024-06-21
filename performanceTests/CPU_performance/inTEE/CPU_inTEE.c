#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>

#define NUM_TESTS 100
#define WORKLOAD_SIZE 100000000 // Aumentado para estressar ainda mais a CPU

void perform_math_test(FILE *log_file, long *total_time) {
    for (int test_num = 1; test_num <= NUM_TESTS; test_num++) {
        clock_t start, end;
        long cpu_time;

        start = clock();
        for (int i = 0; i < WORKLOAD_SIZE; i++) {
            volatile double result = sin(i) * cos(i) * tan(i) * sqrt(i) * log(i + 1);
        }
        end = clock();
        cpu_time = ((long)(end - start)) * 1000 / CLOCKS_PER_SEC;

        fprintf(log_file, "%d,math,%ld\n", test_num, cpu_time);
        *total_time += cpu_time;
    }
}

void perform_int_test(FILE *log_file, long *total_time) {
    for (int test_num = 1; test_num <= NUM_TESTS; test_num++) {
        clock_t start, end;
        long cpu_time;

        start = clock();
        for (int i = 0; i < WORKLOAD_SIZE; i++) {
            volatile int result = i * i / (i + 1);
            result -= i * i % (i + 1);
            result *= (i + 1);
            result /= (i + 2);
        }
        end = clock();
        cpu_time = ((long)(end - start)) * 1000 / CLOCKS_PER_SEC;

        fprintf(log_file, "%d,int,%ld\n", test_num, cpu_time);
        *total_time += cpu_time;
    }
}

void perform_float_test(FILE *log_file, long *total_time) {
    for (int test_num = 1; test_num <= NUM_TESTS; test_num++) {
        clock_t start, end;
        long cpu_time;

        start = clock();
        for (int i = 0; i < WORKLOAD_SIZE; i++) {
            volatile float result = (float)i / (i + 1) * (float)i;
            result -= (float)i / (i + 2) * (float)i;
            result *= (float)i / (i + 3);
            result /= (float)i / (i + 4);
        }
        end = clock();
        cpu_time = ((long)(end - start)) * 1000 / CLOCKS_PER_SEC;

        fprintf(log_file, "%d,float,%ld\n", test_num, cpu_time);
        *total_time += cpu_time;
    }
}

void perform_array_test(FILE *log_file, long *total_time) {
    for (int test_num = 1; test_num <= NUM_TESTS; test_num++) {
        clock_t start, end;
        long cpu_time;
        int *array = (int *)malloc(WORKLOAD_SIZE * sizeof(int));
        if (array == NULL) {
            fprintf(log_file, "%d,array,Allocation failed\n", test_num);
            return;
        }

        start = clock();
        for (int i = 0; i < WORKLOAD_SIZE; i++) {
            array[i] = i;
        }
        for (int i = 0; i < WORKLOAD_SIZE; i++) {
            array[i] = array[i] * 2;
        }
        for (int i = 0; i < WORKLOAD_SIZE; i++) {
            array[i] = array[i] / 2;
        }
        end = clock();
        cpu_time = ((long)(end - start)) * 1000 / CLOCKS_PER_SEC;

        free(array);

        fprintf(log_file, "%d,array,%ld\n", test_num, cpu_time);
        *total_time += cpu_time;
    }
}

int main() {
    FILE *log_file = fopen("cpu_inTEE.csv", "w");
    if (log_file == NULL) {
        printf("Failed to open log file\n");
        return 1;
    }

    // Write CSV header
    fprintf(log_file, "Test Number,Test Type,CPU Time (ms)\n");

    long total_time = 0;

    perform_math_test(log_file, &total_time);
    perform_int_test(log_file, &total_time);
    perform_float_test(log_file, &total_time);
    perform_array_test(log_file, &total_time);

    fclose(log_file);

    printf("Total execution time: %ld milliseconds\n", total_time);

    return 0;
}

