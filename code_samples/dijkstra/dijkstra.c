/**
 * Dijkstra's Algorithm implementation in C.
 *
 * Dijkstra's algorithm is a graph search algorithm that finds the shortest path
 * between nodes in a graph. It works by visiting vertices in order of increasing
 * distance from the source.
 *
 * Time Complexity: O(V^2) with adjacency matrix, O((V+E)logV) with min-heap
 * Space Complexity: O(V)
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <limits.h>

// Maximum number of vertices
#define MAX_VERTICES 100

// Graph structure using adjacency matrix
typedef struct {
    int numVertices;
    char* vertices[MAX_VERTICES];
    int adjacencyMatrix[MAX_VERTICES][MAX_VERTICES];
} Graph;

// Create a new graph
Graph* createGraph(int numVertices) {
    Graph* graph = (Graph*)malloc(sizeof(Graph));
    graph->numVertices = numVertices;
    
    // Initialize adjacency matrix to INT_MAX (infinity)
    for (int i = 0; i < MAX_VERTICES; i++) {
        for (int j = 0; j < MAX_VERTICES; j++) {
            graph->adjacencyMatrix[i][j] = INT_MAX;
        }
        // Distance to self is 0
        graph->adjacencyMatrix[i][i] = 0;
    }
    
    return graph;
}

// Add vertex to the graph
void addVertex(Graph* graph, int index, const char* name) {
    if (index >= 0 && index < graph->numVertices) {
        graph->vertices[index] = strdup(name);
    }
}

// Add weighted edge between vertices
void addEdge(Graph* graph, int start, int end, int weight) {
    if (start >= 0 && start < graph->numVertices && 
        end >= 0 && end < graph->numVertices) {
        graph->adjacencyMatrix[start][end] = weight;
    }
}

// Find vertex index by name
int findVertexIndex(Graph* graph, const char* name) {
    for (int i = 0; i < graph->numVertices; i++) {
        if (strcmp(graph->vertices[i], name) == 0) {
            return i;
        }
    }
    return -1;
}

// Find the vertex with minimum distance value
int minDistance(int dist[], bool sptSet[], int numVertices) {
    int min = INT_MAX, min_index;
    
    for (int v = 0; v < numVertices; v++) {
        if (sptSet[v] == false && dist[v] <= min) {
            min = dist[v];
            min_index = v;
        }
    }
    
    return min_index;
}

// Dijkstra's algorithm to find shortest paths from source to all vertices
void dijkstra(Graph* graph, int src, int dist[], int pred[]) {
    int numVertices = graph->numVertices;
    
    // sptSet[i] will be true if vertex i is included in shortest path tree
    bool sptSet[MAX_VERTICES];
    
    // Initialize all distances as INFINITE and sptSet[] as false
    for (int i = 0; i < numVertices; i++) {
        dist[i] = INT_MAX;
        sptSet[i] = false;
        pred[i] = -1;  // No predecessor initially
    }
    
    // Distance of source vertex from itself is always 0
    dist[src] = 0;
    
    // Find shortest path for all vertices
    for (int count = 0; count < numVertices - 1; count++) {
        // Pick the minimum distance vertex from the set of vertices not yet processed
        int u = minDistance(dist, sptSet, numVertices);
        
        // Mark the picked vertex as processed
        sptSet[u] = true;
        
        // Update dist value of the adjacent vertices of the picked vertex
        for (int v = 0; v < numVertices; v++) {
            // Update dist[v] only if:
            // 1. There is an edge from u to v
            // 2. Vertex v is not in sptSet
            // 3. Total weight of path from src to v through u is smaller than current value of dist[v]
            if (!sptSet[v] && 
                graph->adjacencyMatrix[u][v] != INT_MAX && 
                dist[u] != INT_MAX && 
                dist[u] + graph->adjacencyMatrix[u][v] < dist[v]) {
                dist[v] = dist[u] + graph->adjacencyMatrix[u][v];
                pred[v] = u;  // Update predecessor
            }
        }
    }
}

// Print the shortest path from source to target
void printPath(Graph* graph, int pred[], int target) {
    int path[MAX_VERTICES];
    int pathLength = 0;
    
    // Store the path in reverse order
    int current = target;
    while (current != -1) {
        path[pathLength++] = current;
        current = pred[current];
    }
    
    // Print the path in correct order
    printf("Shortest path: ");
    for (int i = pathLength - 1; i >= 0; i--) {
        printf("%s", graph->vertices[path[i]]);
        if (i > 0) {
            printf(" -> ");
        }
    }
    printf("\n");
}

// Free graph memory
void freeGraph(Graph* graph) {
    for (int i = 0; i < graph->numVertices; i++) {
        free(graph->vertices[i]);
    }
    free(graph);
}

// Example usage
int main() {
    // Create a graph with 6 vertices
    Graph* graph = createGraph(6);
    
    // Add vertices
    addVertex(graph, 0, "A");
    addVertex(graph, 1, "B");
    addVertex(graph, 2, "C");
    addVertex(graph, 3, "D");
    addVertex(graph, 4, "E");
    addVertex(graph, 5, "F");
    
    // Add weighted edges
    addEdge(graph, 0, 1, 4);  // A -> B
    addEdge(graph, 0, 2, 2);  // A -> C
    addEdge(graph, 1, 0, 4);  // B -> A
    addEdge(graph, 1, 3, 2);  // B -> D
    addEdge(graph, 1, 4, 3);  // B -> E
    addEdge(graph, 2, 0, 2);  // C -> A
    addEdge(graph, 2, 3, 4);  // C -> D
    addEdge(graph, 2, 5, 5);  // C -> F
    addEdge(graph, 3, 1, 2);  // D -> B
    addEdge(graph, 3, 2, 4);  // D -> C
    addEdge(graph, 3, 4, 1);  // D -> E
    addEdge(graph, 3, 5, 7);  // D -> F
    addEdge(graph, 4, 1, 3);  // E -> B
    addEdge(graph, 4, 3, 1);  // E -> D
    addEdge(graph, 4, 5, 4);  // E -> F
    addEdge(graph, 5, 2, 5);  // F -> C
    addEdge(graph, 5, 3, 7);  // F -> D
    addEdge(graph, 5, 4, 4);  // F -> E
    
    int src = 0;  // Source vertex (A)
    int target = 5;  // Target vertex (F)
    
    // Arrays to store shortest distances and predecessors
    int dist[MAX_VERTICES];
    int pred[MAX_VERTICES];
    
    // Find shortest paths from source vertex
    dijkstra(graph, src, dist, pred);
    
    // Print shortest distances from source vertex
    printf("Shortest distances from %s:\n", graph->vertices[src]);
    for (int i = 0; i < graph->numVertices; i++) {
        if (dist[i] == INT_MAX) {
            printf("%s: Infinity\n", graph->vertices[i]);
        } else {
            printf("%s: %d\n", graph->vertices[i], dist[i]);
        }
    }
    
    // Print shortest path to target vertex
    printf("\n");
    printPath(graph, pred, target);
    printf("Distance: %d\n", dist[target]);
    
    // Free memory
    freeGraph(graph);
    
    return 0;
}
