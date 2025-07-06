/**
 * Floyd-Warshall Algorithm implementation in C.
 *
 * Floyd-Warshall algorithm is used to find shortest paths between all pairs of vertices in a weighted graph.
 * It works by incrementally improving an estimate on the shortest path between two vertices.
 *
 * Time Complexity: O(V^3) where V is the number of vertices
 * Space Complexity: O(V^2)
 */
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>

// Maximum number of vertices
#define MAX_VERTICES 100

/**
 * Find shortest paths between all pairs of vertices in a weighted graph.
 *
 * @param graph 2D matrix where graph[i][j] is the weight of the edge from i to j,
 *              or INT_MAX if there is no direct edge
 * @param n Number of vertices
 * @param dist Output matrix for shortest distances
 * @param next Output matrix for path reconstruction
 */
void floydWarshall(int graph[MAX_VERTICES][MAX_VERTICES], int n, 
                  int dist[MAX_VERTICES][MAX_VERTICES], 
                  int next[MAX_VERTICES][MAX_VERTICES]) {
    // Initialize distance matrix as the input graph
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            dist[i][j] = graph[i][j];
            if (graph[i][j] != INT_MAX) {
                next[i][j] = j;
            } else {
                next[i][j] = -1;
            }
        }
    }
    
    // Floyd-Warshall algorithm
    for (int k = 0; k < n; k++) {
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (dist[i][k] != INT_MAX && dist[k][j] != INT_MAX) {
                    if (dist[i][j] > dist[i][k] + dist[k][j]) {
                        dist[i][j] = dist[i][k] + dist[k][j];
                        next[i][j] = next[i][k];
                    }
                }
            }
        }
    }
}

/**
 * Reconstruct the shortest path from vertex u to vertex v.
 *
 * @param next Path reconstruction matrix from floydWarshall
 * @param u Source vertex
 * @param v Target vertex
 * @param path Output array for the path
 * @return Length of the path, or -1 if no path exists
 */
int reconstructPath(int next[MAX_VERTICES][MAX_VERTICES], int u, int v, int path[MAX_VERTICES]) {
    if (next[u][v] == -1) {
        return -1; // No path exists
    }
    
    int pathLength = 0;
    path[pathLength++] = u;
    
    while (u != v) {
        u = next[u][v];
        path[pathLength++] = u;
    }
    
    return pathLength;
}

// Example usage
int main() {
    // Example graph represented as an adjacency matrix
    // INT_MAX represents no direct edge between vertices
    int graph[MAX_VERTICES][MAX_VERTICES] = {
        {0, 5, INT_MAX, 10},
        {INT_MAX, 0, 3, INT_MAX},
        {INT_MAX, INT_MAX, 0, 1},
        {INT_MAX, INT_MAX, INT_MAX, 0}
    };
    
    int n = 4; // Number of vertices
    
    // Matrices for shortest distances and path reconstruction
    int dist[MAX_VERTICES][MAX_VERTICES];
    int next[MAX_VERTICES][MAX_VERTICES];
    
    // Find shortest paths between all pairs of vertices
    floydWarshall(graph, n, dist, next);
    
    // Print shortest distances between all pairs of vertices
    printf("Shortest distances between all pairs of vertices:\n");
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (dist[i][j] == INT_MAX) {
                printf("INF\t");
            } else {
                printf("%d\t", dist[i][j]);
            }
        }
        printf("\n");
    }
    
    // Print shortest path from vertex 0 to vertex 3
    int path[MAX_VERTICES];
    int pathLength = reconstructPath(next, 0, 3, path);
    
    if (pathLength != -1) {
        printf("\nShortest path from vertex 0 to vertex 3: [");
        for (int i = 0; i < pathLength; i++) {
            printf("%d", path[i]);
            if (i < pathLength - 1) {
                printf(", ");
            }
        }
        printf("]\n");
        printf("Distance: %d\n", dist[0][3]);
    } else {
        printf("\nNo path exists from vertex 0 to vertex 3\n");
    }
    
    return 0;
}
