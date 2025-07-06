/**
 * Selection Sort implementation in C.
 *
 * Selection Sort is a simple comparison-based sorting algorithm.
 * It divides the input list into two parts: a sorted sublist and an unsorted sublist.
 * The algorithm repeatedly finds the minimum element from the unsorted sublist
 * and moves it to the end of the sorted sublist.
 *
 * Time Complexity: O(n^2)
 * Space Complexity: O(1)
 */
#include <stdio.h>

/**
 * Sort an array using selection sort algorithm.
 *
 * @param arr Array of comparable elements
 * @param n Size of the array
 */
void selectionSort(int arr[], int n) {
    // Traverse through all array elements
    for (int i = 0; i < n; i++) {
        // Find the minimum element in remaining unsorted array
        int minIdx = i;
        for (int j = i + 1; j < n; j++) {
            if (arr[j] < arr[minIdx]) {
                minIdx = j;
            }
        }
        
        // Swap the found minimum element with the first element
        int temp = arr[minIdx];
        arr[minIdx] = arr[i];
        arr[i] = temp;
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
    int testArray[] = {64, 25, 12, 22, 11};
    int n = sizeof(testArray) / sizeof(testArray[0]);
    
    printf("Original array: ");
    printArray(testArray, n);
    
    selectionSort(testArray, n);
    printf("Sorted array: ");
    printArray(testArray, n);
    
    return 0;
}
