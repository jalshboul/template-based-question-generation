/**
 * Prim's Algorithm implementation in C.
 *
 * Prim's algorithm is a greedy algorithm that finds a minimum spanning tree for a weighted undirected graph.
 * It finds a subset of the edges that forms a tree that includes every vertex, where the total weight of all
 * the edges in the tree is minimized.
 *
 * Time Complexity: O(V^2) with adjacency matrix, O(E log V) with binary heap
 * Space Complexity: O(V)
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <limits.h>

// Maximum number of vertices
#define MAX_VERTICES 100

// Structure to represent a graph
typedef struct {
    int numVertices;
    int adjacencyMatrix[MAX_VERTICES][MAX_VERTICES];
} Graph;

// Create a new graph
Graph* createGraph(int numVertices) {
    Graph* graph = (Graph*)malloc(sizeof(Graph));
    graph->numVertices = numVertices;
    
    // Initialize adjacency matrix to INT_MAX (infinity)
    for (int i = 0; i < numVertices; i++) {
        for (int j = 0; j < numVertices; j++) {
            graph->adjacencyMatrix[i][j] = INT_MAX;
        }
    }
    
    return graph;
}

// Add edge between vertices
void addEdge(Graph* graph, int src, int dest, int weight) {
    // Add edge from src to dest
    graph->adjacencyMatrix[src][dest] = weight;
    
    // Add edge from dest to src (undirected graph)
    graph->adjacencyMatrix[dest][src] = weight;
}

// Find the vertex with minimum key value, from the set of vertices not yet included in MST
int minKey(int key[], bool mstSet[], int numVertices) {
    int min = INT_MAX, min_index;
    
    for (int v = 0; v < numVertices; v++) {
        if (mstSet[v] == false && key[v] < min) {
            min = key[v];
            min_index = v;
        }
    }
    
    return min_index;
}

/**
 * Find the minimum spanning tree of a graph using Prim's algorithm.
 *
 * @param graph The graph represented as an adjacency matrix
 * @param startVertex Starting vertex for the algorithm
 * @param parent Output array to store the MST
 * @return Total weight of the MST
 */
int primsAlgorithm(Graph* graph, int startVertex, int parent[]) {
    int numVertices = graph->numVertices;
    
    // Key values used to pick minimum weight edge
    int key[MAX_VERTICES];
    
    // To represent set of vertices included in MST
    bool mstSet[MAX_VERTICES];
    
    // Initialize all keys as INFINITE and mstSet[] as false
    for (int i = 0; i < numVertices; i++) {
        key[i] = INT_MAX;
        mstSet[i] = false;
    }
    
    // Always include the start vertex in MST
    // Make key 0 so that this vertex is picked as first vertex
    key[startVertex] = 0;
    parent[startVertex] = -1; // First node is always root of MST
    
    // The MST will have numVertices vertices
    for (int count = 0; count < numVertices - 1; count++) {
        // Pick the minimum key vertex from the set of vertices not yet included in MST
        int u = minKey(key, mstSet, numVertices);
        
        // Add the picked vertex to the MST Set
        mstSet[u] = true;
        
        // Update key value and parent index of the adjacent vertices of the picked vertex
        // Consider only those vertices which are not yet included in MST
        for (int v = 0; v < numVertices; v++) {
            // graph[u][v] is non-zero only for adjacent vertices of u
            // mstSet[v] is false for vertices not yet included in MST
            // Update the key only if graph[u][v] is smaller than key[v]
            if (graph->adjacencyMatrix[u][v] != INT_MAX && mstSet[v] == false && 
                graph->adjacencyMatrix[u][v] < key[v]) {
                parent[v] = u;
                key[v] = graph->adjacencyMatrix[u][v];
            }
        }
    }
    
    // Calculate total weight of MST
    int totalWeight = 0;
    for (int i = 0; i < numVertices; i++) {
        if (parent[i] != -1) {
            totalWeight += graph->adjacencyMatrix[i][parent[i]];
        }
    }
    
    return totalWeight;
}

// Free graph memory
void freeGraph(Graph* graph) {
    free(graph);
}

// Example usage
int main() {
    // Create a graph with 9 vertices
    Graph* graph = createGraph(9);
    
    // Add edges
    addEdge(graph, 0, 1, 1);
    addEdge(graph, 0, 7, 4);
    addEdge(graph, 1, 2, 3);
    addEdge(graph, 1, 7, 2);
    addEdge(graph, 2, 3, 5);
    addEdge(graph, 2, 5, 3);
    addEdge(graph, 2, 8, 6);
    addEdge(graph, 3, 4, 4);
    addEdge(graph, 3, 5, 2);
    addEdge(graph, 4, 5, 7);
    addEdge(graph, 5, 6, 6);
    addEdge(graph, 6, 7, 1);
    addEdge(graph, 6, 8, 5);
    addEdge(graph, 7, 8, 7);
    
    // Array to store constructed MST
    int parent[MAX_VERTICES];
    
    // Find minimum spanning tree
    int totalWeight = primsAlgorithm(graph, 0, parent);
    
    // Print MST edges and total weight
    printf("Edges in the minimum spanning tree:\n");
    for (int i = 1; i < graph->numVertices; i++) {
        printf("(%d, %d) with weight %d\n", parent[i], i, graph->adjacencyMatrix[i][parent[i]]);
    }
    
    printf("Total weight of MST: %d\n", totalWeight);
    
    // Free memory
    freeGraph(graph);
    
    return 0;
}
