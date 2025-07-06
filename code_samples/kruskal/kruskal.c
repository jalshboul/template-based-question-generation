/**
 * Kruskal's Algorithm implementation in C.
 *
 * Kruskal's algorithm is a minimum spanning tree algorithm that finds an edge of the least possible weight
 * that connects any two trees in the forest. It is a greedy algorithm that builds the spanning tree by
 * adding edges one by one in order of increasing weight.
 *
 * Time Complexity: O(E log E) where E is the number of edges
 * Space Complexity: O(V + E) where V is the number of vertices
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

// Edge structure to represent a weighted edge in the graph
typedef struct {
    int src, dest, weight;
} Edge;

// Structure for Disjoint Set (Union-Find) data structure
typedef struct {
    int* parent;
    int* rank;
    int size;
} DisjointSet;

// Function to create a new edge
Edge createEdge(int src, int dest, int weight) {
    Edge edge;
    edge.src = src;
    edge.dest = dest;
    edge.weight = weight;
    return edge;
}

// Function to create a disjoint set
DisjointSet* createDisjointSet(int n) {
    DisjointSet* ds = (DisjointSet*)malloc(sizeof(DisjointSet));
    ds->size = n;
    ds->parent = (int*)malloc(n * sizeof(int));
    ds->rank = (int*)malloc(n * sizeof(int));
    
    // Initialize each element as a separate set
    for (int i = 0; i < n; i++) {
        ds->parent[i] = i;
        ds->rank[i] = 0;
    }
    
    return ds;
}

// Find the representative (root) of the set containing element x
// Uses path compression for efficiency
int find(DisjointSet* ds, int x) {
    if (ds->parent[x] != x) {
        ds->parent[x] = find(ds, ds->parent[x]);  // Path compression
    }
    return ds->parent[x];
}

// Union of two sets containing elements x and y
// Uses union by rank for efficiency
void unionSets(DisjointSet* ds, int x, int y) {
    int rootX = find(ds, x);
    int rootY = find(ds, y);
    
    if (rootX == rootY) {
        return;
    }
    
    // Union by rank
    if (ds->rank[rootX] < ds->rank[rootY]) {
        ds->parent[rootX] = rootY;
    } else if (ds->rank[rootX] > ds->rank[rootY]) {
        ds->parent[rootY] = rootX;
    } else {
        ds->parent[rootY] = rootX;
        ds->rank[rootX]++;
    }
}

// Free memory allocated for disjoint set
void freeDisjointSet(DisjointSet* ds) {
    free(ds->parent);
    free(ds->rank);
    free(ds);
}

// Comparison function for qsort
int compareEdges(const void* a, const void* b) {
    return ((Edge*)a)->weight - ((Edge*)b)->weight;
}

/**
 * Find the minimum spanning tree of a graph using Kruskal's algorithm.
 *
 * @param edges Array of edges in the graph
 * @param numEdges Number of edges in the graph
 * @param numVertices Number of vertices in the graph
 * @param mst Output array to store MST edges
 * @return Number of edges in the MST
 */
int kruskal(Edge* edges, int numEdges, int numVertices, Edge* mst) {
    // Sort edges by weight
    qsort(edges, numEdges, sizeof(Edge), compareEdges);
    
    // Initialize disjoint set
    DisjointSet* ds = createDisjointSet(numVertices);
    
    int mstSize = 0;
    
    // Process edges in order of increasing weight
    for (int i = 0; i < numEdges; i++) {
        Edge currentEdge = edges[i];
        
        // If including this edge doesn't form a cycle
        if (find(ds, currentEdge.src) != find(ds, currentEdge.dest)) {
            // Include this edge in MST
            mst[mstSize++] = currentEdge;
            unionSets(ds, currentEdge.src, currentEdge.dest);
        }
    }
    
    // Free memory
    freeDisjointSet(ds);
    
    return mstSize;
}

// Example usage
int main() {
    // Example graph represented as an array of edges
    Edge edges[] = {
        {0, 1, 1},
        {0, 7, 4},
        {1, 2, 3},
        {1, 7, 2},
        {2, 3, 5},
        {2, 8, 6},
        {2, 5, 3},
        {3, 4, 4},
        {3, 5, 2},
        {4, 5, 7},
        {5, 6, 6},
        {6, 7, 1},
        {6, 8, 5},
        {7, 8, 7}
    };
    
    int numEdges = sizeof(edges) / sizeof(edges[0]);
    int numVertices = 9;  // 0 to 8
    
    // Array to store MST edges (at most numVertices-1 edges)
    Edge mst[numVertices - 1];
    
    // Find minimum spanning tree
    int mstSize = kruskal(edges, numEdges, numVertices, mst);
    
    // Print MST edges and total weight
    printf("Edges in the minimum spanning tree:\n");
    int totalWeight = 0;
    for (int i = 0; i < mstSize; i++) {
        printf("(%d, %d) with weight %d\n", mst[i].src, mst[i].dest, mst[i].weight);
        totalWeight += mst[i].weight;
    }
    
    printf("Total weight of MST: %d\n", totalWeight);
    
    return 0;
}
