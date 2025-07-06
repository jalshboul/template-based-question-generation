/**
 * Binary Search implementation in C.
 *
 * Binary Search is an efficient algorithm for finding a target value within a sorted array.
 * It works by repeatedly dividing the search interval in half.
 *
 * Time Complexity: O(log n)
 * Space Complexity: O(1) for iterative implementation, O(log n) for recursive implementation
 */
#include <stdio.h>

/**
 * Search for a target value in a sorted array using binary search algorithm.
 *
 * @param arr Sorted array of comparable elements
 * @param left Starting index
 * @param right Ending index
 * @param target Value to search for
 * @return Index of the target if found, -1 otherwise
 */
int binarySearch(int arr[], int left, int right, int target) {
    while (left <= right) {
        // Calculate middle index
        int mid = left + (right - left) / 2;
        
        // Check if target is present at mid
        if (arr[mid] == target) {
            return mid;
        }
        
        // If target is greater, ignore left half
        if (arr[mid] < target) {
            left = mid + 1;
        }
        // If target is smaller, ignore right half
        else {
            right = mid - 1;
        }
    }
    
    // Target is not present in the array
    return -1;
}

// Example usage
int main() {
    // Test with a sorted array
    int testArray[] = {2, 3, 4, 10, 40};
    int n = sizeof(testArray) / sizeof(testArray[0]);
    int target = 10;
    
    int result = binarySearch(testArray, 0, n - 1, target);
    if (result != -1) {
        printf("Element %d is present at index %d\n", target, result);
    } else {
        printf("Element %d is not present in array\n", target);
    }
    
    return 0;
}
