/**
 * Quick Sort implementation in C.
 *
 * Quick Sort is a divide-and-conquer sorting algorithm that works by selecting a 'pivot' element
 * from the array and partitioning the other elements into two sub-arrays according to whether
 * they are less than or greater than the pivot.
 *
 * Time Complexity: O(n log n) average case, O(n²) worst case
 * Space Complexity: O(log n) due to recursion stack
 */
#include <stdio.h>

/**
 * Swap two elements in an array.
 *
 * @param a First element
 * @param b Second element
 */
void swap(int* a, int* b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

/**
 * Partition the array and return the partition index.
 *
 * @param arr Array to be partitioned
 * @param low Starting index
 * @param high Ending index
 * @return Partition index
 */
int partition(int arr[], int low, int high) {
    // Choose the rightmost element as pivot
    int pivot = arr[high];
    
    // Index of smaller element
    int i = (low - 1);
    
    for (int j = low; j < high; j++) {
        // If current element is smaller than the pivot
        if (arr[j] < pivot) {
            i++;
            swap(&arr[i], &arr[j]);
        }
    }
    swap(&arr[i + 1], &arr[high]);
    return (i + 1);
}

/**
 * Sort an array using quick sort algorithm.
 *
 * @param arr Array to be sorted
 * @param low Starting index
 * @param high Ending index
 */
void quickSort(int arr[], int low, int high) {
    if (low < high) {
        // Find the partition index
        int pi = partition(arr, low, high);
        
        // Recursively sort elements before and after partition
        quickSort(arr, low, pi - 1);
        quickSort(arr, pi + 1, high);
    }
}

// Utility function to print an array
void printArray(int arr[], int size) {
    for (int i = 0; i < size; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
}

// Example usage
int main() {
    // Test with a sample array
    int testArray[] = {10, 7, 8, 9, 1, 5};
    int n = sizeof(testArray) / sizeof(testArray[0]);
    
    printf("Original array: ");
    printArray(testArray, n);
    
    quickSort(testArray, 0, n - 1);
    printf("Sorted array: ");
    printArray(testArray, n);
    
    return 0;
}
