/**
 * Greedy Algorithm implementation in C - Activity Selection Problem.
 *
 * The Activity Selection Problem is a classic optimization problem where we need to select
 * the maximum number of activities that can be performed by a single person, given the start
 * and finish times of each activity. The person can only work on a single activity at a time.
 *
 * Time Complexity: O(n log n) where n is the number of activities (due to sorting)
 * Space Complexity: O(n) for storing the result
 */
#include <stdio.h>
#include <stdlib.h>

// Structure to represent an activity
typedef struct {
    int startTime;
    int finishTime;
    int index;
} Activity;

// Comparison function for qsort
int compareActivities(const void* a, const void* b) {
    return ((Activity*)a)->finishTime - ((Activity*)b)->finishTime;
}

/**
 * Solve the Activity Selection Problem using a greedy approach.
 *
 * @param startTimes Array of start times of activities
 * @param finishTimes Array of finish times of activities
 * @param n Number of activities
 * @param selected Output array to store selected activities (1 if selected, 0 otherwise)
 * @return Number of selected activities
 */
int activitySelection(int startTimes[], int finishTimes[], int n, int selected[]) {
    // Create an array of activities
    Activity* activities = (Activity*)malloc(n * sizeof(Activity));
    for (int i = 0; i < n; i++) {
        activities[i].startTime = startTimes[i];
        activities[i].finishTime = finishTimes[i];
        activities[i].index = i;
        selected[i] = 0;  // Initialize all to not selected
    }
    
    // Sort activities by finish time
    qsort(activities, n, sizeof(Activity), compareActivities);
    
    // Select the first activity
    selected[activities[0].index] = 1;
    int lastFinishTime = activities[0].finishTime;
    int count = 1;
    
    // Consider the rest of the activities
    for (int i = 1; i < n; i++) {
        // If this activity starts after the finish time of the last selected activity
        if (activities[i].startTime >= lastFinishTime) {
            // Select this activity
            selected[activities[i].index] = 1;
            lastFinishTime = activities[i].finishTime;
            count++;
        }
    }
    
    // Free memory
    free(activities);
    
    return count;
}

// Example usage
int main() {
    // Example problem
    int startTimes[] = {1, 3, 0, 5, 8, 5};
    int finishTimes[] = {2, 4, 6, 7, 9, 9};
    int n = sizeof(startTimes) / sizeof(startTimes[0]);
    
    // Array to store which activities are selected
    int* selected = (int*)malloc(n * sizeof(int));
    
    int count = activitySelection(startTimes, finishTimes, n, selected);
    
    printf("Number of selected activities: %d\n", count);
    printf("Selected activities (0-indexed): ");
    int first = 1;
    for (int i = 0; i < n; i++) {
        if (selected[i]) {
            if (!first) {
                printf(", ");
            }
            printf("%d", i);
            first = 0;
        }
    }
    printf("\n");
    
    printf("Selected activities details:\n");
    for (int i = 0; i < n; i++) {
        if (selected[i]) {
            printf("Activity %d: Start time = %d, Finish time = %d\n", 
                   i, startTimes[i], finishTimes[i]);
        }
    }
    
    free(selected);
    
    return 0;
}
