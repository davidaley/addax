import bz2
import pickle
import struct



from addax.data_structures.graph import Graph



def ReadGraph(input_filename, vertices_only = False):
    """
    Read a graph data structure from disk

    @param input_filename: the filename where the graph data is stored
    @param vertices_only: boolean flag that determines if edges are read
    """
    assert (input_filename.endswith('.graph.bz2'))

    data = bz2.decompress(open(input_filename, 'rb').read())

    byte_index = 0

    # read the basic attributes for the graph
    nvertices, nedges, directed, colored, = struct.unpack('qq??', data[byte_index:byte_index + 18])
    byte_index += 18

    # read the prefix
    prefix, = struct.unpack('128s', data[byte_index:byte_index + 128])
    byte_index += 128

    prefix = prefix.decode().strip('\0')

    graph = Graph(prefix, directed, colored)

    # read all the vertices and add them to the graph
    for _ in range(nvertices):
        index, enumeration_index, community, color, = struct.unpack('qqqq', data[byte_index:byte_index + 32])
        byte_index += 32

        graph.AddVertex(index, enumeration_index, community, color)

    # if the flag to read only vertices is on, avoid reading edges
    if vertices_only: return graph

    # read all of the edges and add them to the graph
    for _ in range(nedges):
        source_index, destination_index, weight, = struct.unpack('qqd', data[byte_index:byte_index + 24])
        byte_index += 24

        graph.AddEdge(source_index, destination_index, weight)

    return graph



def ReadPrefix(input_filename):
    """
    Read the prefix of a graph data structure from disk

    @param input_filename: the filename where the graph data is stored
    """
    assert (input_filename.endswith('.graph.bz2'))

    data = bz2.decompress(open(input_filename, 'rb').read())

    byte_index = 0

    # read the basic attributes for the graph
    nvertices, nedges, directed, colored, = struct.unpack('qq??', data[byte_index:byte_index + 18])
    byte_index += 18

    # read the prefix
    prefix, = struct.unpack('128s', data[byte_index:byte_index + 128])
    byte_index += 128

    prefix = prefix.decode().strip('\0')

    return prefix



def WriteGraph(graph, output_filename):
    """
    Write a graph to disk for later I/O access

    @param graph: the graph data structure to save to disk
    @param output_filename: the location to save the graph data structure
    """
    assert (output_filename.endswith('.graph.bz2'))

    # create a new compression object
    compressor = bz2.BZ2Compressor()

    # write the basic attributes for the graph to disk
    nvertices = graph.NVertices()
    nedges = graph.NEdges()
    directed = graph.directed
    colored = graph.colored
    prefix = graph.prefix

    # create an empty byte array which we will concatenate later
    compressed_graph = []

    compressed_graph.append(compressor.compress(struct.pack('qq??', nvertices, nedges, directed, colored)))
    compressed_graph.append(compressor.compress(struct.pack('128s', prefix.encode())))

    # write all of the vertices and their attributes
    for vertex in graph.vertices.values():
        compressed_graph.append(compressor.compress(struct.pack('qqqq', vertex.index, vertex.enumeration_index, vertex.community, vertex.color)))

    # write all of the edges and their attributes
    for edge in graph.edges:
        compressed_graph.append(compressor.compress(struct.pack('qqd', edge.source_index, edge.destination_index, edge.weight)))

    # flush the data
    compressed_graph.append(compressor.flush())

    # convert the array into a binary string - faster than native implementation
    compressed_graph = b''.join(compressed_graph)

    # write the compressed string to file
    with open(output_filename, 'wb') as fd:
        fd.write(compressed_graph)



def PickleData(data, filename):
    """
    Pickle the data and write to disk

    @param data: the data to pickle
    @param filename: the location to save the pickled data
    """
    with open(filename, 'wb') as fd:
        pickle.dump(data, fd)



def ReadPickledData(filename):
    """
    Read pickled data from disk and return object

    @param filename: the location of the saved pickled data
    """
    with open(filename, 'rb') as fd:
        return pickle.load(fd)
