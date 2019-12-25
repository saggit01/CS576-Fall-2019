from matplotlib import pyplot as plt # for plotting
import ipywidgets

def plot_profiles(profiles, cluster_assignments=None, centers=None, title=None):
    """Plot a set of two dimensional profiles.

    Optionally, color the points by cluster assignment plot the cluster centers."""
    plt.figure(figsize=(4,4), dpi=150)
    
    if title: plt.title(title)
    
    x, y = list(zip(*profiles))
    plt.scatter(x, y, c=cluster_assignments, alpha=0.75)
    
    if centers:
        c_x, c_y = list(zip(*centers))
        plt.scatter(c_x, c_y, c=range(len(centers)), marker='x')
    
    plt.xlabel("gene X")
    plt.ylabel("gene Y")
    plt.show()
    
def plot_profiles_interact_hidden(profiles, cluster_assignments, centers):
    def plot(show_hidden=False):
        if show_hidden:
            plot_profiles(profiles, cluster_assignments, centers,
                          title="Observed and hidden data")
        else:
            plot_profiles(profiles, title="Observed data only")
    ipywidgets.interact(plot)

def plot_multiple_kmeans_clusterings(profiles, clusterings):
    def plot(k):
        assignments, centers = clusterings[k - 1]
        plot_profiles(profiles, assignments, centers, title="k = {}".format(k))
    ipywidgets.interact(plot, k=(1, len(clusterings)))