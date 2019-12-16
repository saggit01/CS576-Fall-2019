import random
import math
import itertools
import sys

def cluster_kmeans(profiles, k, initial_f=None, max_iterations=None, num_runs=1):
    """Runs the K-means algorithm, returning the final cluster assignments and centers.
    
    Args:
        profiles: a list of profiles (vectors), with each profile represented as tuple
        k: the number of clusters to find
        initial_f: the initial cluster centers (optional)
        max_iterations: the maximum number of iterations for the algorithm
        num_runs: # of runs of the algorithm with random intializations
    Returns:
        A tuple (C, f), where C is a list with C[i] giving the index of the cluster to
        which profile i is assigned, and f is a list of cluster centers (tuples) (e.g., f[j] 
        is the cluster center for cluster j).
    """
    best_C, best_f, best_score = None, None, float("inf")
    for run in range(num_runs):
        # iterate until termination
        for C, f in cluster_kmeans_iterator(profiles, k, initial_f, max_iterations):
            pass
        score = within_cluster_scatter(profiles, C, f)
        if score < best_score:
            best_C, best_f, best_score = C, f, score

    return best_C, best_f

def cluster_kmeans_iterator(profiles, k, initial_f=None, max_iterations=None):
    """An iterator over the results the K-means algorithm after each of its iterations.
    
    The arguments and yielded values are the same as for cluster_kmeans.
    """
    
    # randomly select k of the input profiles as centers if initial_f not given
    f = initial_f if initial_f else random.sample(profiles, k)
    
    # keep track of the last cluster assignments
    last_C = None
    
    for iteration in itertools.count(1):
        # stop if we have reached the maximum number of iterations
        if max_iterations is not None and iteration > max_iterations:
            print("Warning: max iterations reached", file=sys.stderr)
            break
        
        # (re)compute closest cluster for each profile
        C = [closest_center(profile, f) for profile in profiles]
        # terminate if the cluster assignments do not change
        if C == last_C: break

        # (re)compute cluster centers
        # create lists of profiles assigned to each cluster
        clusters = group_by_cluster_assignment(profiles, C, k)
        # if a cluster has no points assigned to it, use its last center
        f = [mean_profile(cluster) if cluster else f[i] for i, cluster in enumerate(clusters)]
        
        # yield the current results for possible inspection
        yield C, f
        last_C = C

def group_by_cluster_assignment(objects, assignments, k):
    """Returns a list of lists of the objects assigned to each cluster."""
    clusters = [[] for i in range(k)]
    for obj, cluster_index in zip(objects, assignments):
        clusters[cluster_index].append(obj)
    return clusters

def squared_euclidean_distance(p1, p2):
    """The square of the Euclidean distances between two profiles."""
    return sum((e1 - e2)**2 for e1, e2 in zip(p1, p2))

def euclidean_distance(p1, p2):
    """The Euclidean distance between two profiles."""
    return math.sqrt(squared_euclidean_distance(p1, p2))

def closest_center(profile, centers):
    """Returns the index of the cluster center that is closest to profile.
    
    If multiple centers are equally close, the smallest index is returned.
    Args:
        profile: a tuple representing the query profile
        centers: a list of tuples representing the centers of each cluster.
    Returns:
        The index of the center that is closest (in Euclidean distance) to the query profile."""
    distances = [squared_euclidean_distance(profile, center) for center in centers]
    return distances.index(min(distances))

def mean_profile(profiles):
    """Computes the center (mean) of a cluster of the given profiles.
    
    Args:
        profiles: a list of profiles (tuples)
    Returns:
        a tuple representing the mean of the profiles."""
    n = len(profiles)
    return tuple(s / n for s in map(sum, zip(*profiles)))

def within_cluster_scatter(profiles, cluster_assignments, centers):
    """Computes the within-cluster scatter for a given clustering."""
    return sum(squared_euclidean_distance(p, centers[cluster_index])
               for p, cluster_index in zip(profiles, cluster_assignments))