import os
import csv
import time



from addax.data_structures.graph import Graph
from addax.utilities.dataIO import ReadGraph, WriteGraph



def ConstructGraphFromHemiBrainCSV(LOW_EDGE_THRESHOLD = 5):
    """
    Construct a graph object for the hemi brain CSV files

    @param LOW_EDGE_THRESHOLD: two neurons with fewer than this number of synapses are not connected
    """
    # start statistics
    start_time = time.time()

    neurons = set()
    edges = {}

    # open the neuron csv file
    neuron_filename = 'CSVs/HemiBrain/traced-neurons.csv'
    with open(neuron_filename, newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')

        # skip header
        next(csv_reader, None)
        for row in csv_reader:
            neuron_id = int(row[0])
            assert (not neuron_id in neurons)
            # add this neuron to the list of neurons
            neurons.add(neuron_id)

    # read the synapses by region of interest
    synapse_filename = 'CSVs/HemiBrain/traced-roi-connections.csv'
    with open(synapse_filename, newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')

        # skip header
        next(csv_reader, None)
        for row in csv_reader:
            pre_neuron_id = int(row[0])
            post_neuron_id = int(row[1])
            weight = int(row[3])

            assert (pre_neuron_id in neurons)
            assert (post_neuron_id in neurons)

            # update the connective strength between these two neurons
            if not (pre_neuron_id, post_neuron_id) in edges:
                edges[(pre_neuron_id, post_neuron_id)] = weight
            else:
                edges[(pre_neuron_id, post_neuron_id)] += weight

    # remove edges that are below a threshold, must first convert keys into a list in python 3
    pruned_edges = [(pre, post) for (pre, post), weight in edges.items() if weight < LOW_EDGE_THRESHOLD]
    for (pre, post) in pruned_edges:
        del edges[(pre, post)]

    # construct a directed graph object
    graph = Graph('hemi-brain', directed = True, colored = False)

    # add vertices with communities initially at -1
    for enumeration_index, neuron in enumerate(sorted(neurons)):
        # vertices start with  the default coloring of -1, enumeration_index of -1
        graph.AddVertex(neuron, enumeration_index, community = -1, color = -1)

    # add edges with the synaptic weights
    for (pre_neuron_id, post_neuron_id) in edges.keys():
        graph.AddEdge(pre_neuron_id, post_neuron_id, weight = edges[(pre_neuron_id, post_neuron_id)])

    # create the communities for this graph
    partitions = graph.DetectCommunities()
    for vertex, partition in partitions.items():
        graph.vertices[vertex].community = partition

    # write the hemibrain graph to disk
    if not os.path.exists('graphs'):
        os.makedirs('graphs', exist_ok = True)
    output_filename = 'graphs/hemi-brain.graph.bz2'
    WriteGraph(graph, output_filename)

    # write the condensed CSV neuron and edge files
    with open('CSVs/HemiBrain/condensed-neurons.csv', 'w') as fd:
        fd.write('Neuron ID,Community\n')
        for neuron in graph.vertices.values():
            fd.write('{},{}\n'.format(neuron.index, neuron.community))

    with open('CSVs/HemiBrain/condensed-edges.csv', 'w') as fd:
        fd.write('Pre Synaptic Neuron ID,Post Synaptic Neuron ID,Weight\n')
        for edge in graph.edges:
            fd.write('{},{},{}\n'.format(edge.source_index, edge.destination_index, edge.weight))

    # print statistics
    print ('Wrote {} in {:0.2f} seconds.'.format(output_filename, time.time() - start_time))
