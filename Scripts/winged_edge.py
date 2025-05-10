class Edge:
    def __init__(self, vertex_start, vertex_end):
        self.vertex_start = vertex_start
        self.vertex_end = vertex_end
        self.left_face = None
        self.right_face = None
        self.next_left = None
        self.prev_left = None
        self.next_right = None
        self.prev_right = None

class Vertex:
    def __init__(self, index, coord):
        self.index = index
        self.coord = coord
        self.edge = None

class Face:
    def __init__(self, index):
        self.index = index
        self.edge = None

class EdgeMesh:
    # we use a mesh to work with the .obj file
    def __init__(self):
        self.vertices = {}
        self.edges = {}
        self.faces = {}
    
    def load_obj(self, filename):
        with open(filename) as f:
            lines = f.readlines()

        vertex_id = 1
        face_id = 1

        for line in lines:
            if line.startswith('v '):
                # we read the line and separate the values for the coordinates
                _, x, y, z = line.strip().split()
                self.vertices[vertex_id] = Vertex(vertex_id, (float(x), float(y), float(z)) )
                vertex_id += 1

        for line in lines:
            if line.startswith('f '):
                # we start the function creating an object Face
                face = Face(face_id)
                self.faces[face_id] = face
                # here we split the string with '//' and take the first value
                # and we do this for every string found in the line split that starts with 'f '
                indices = [int(p.split('/')[0]) for p in line.strip().split()[1:]]
                n = len(indices)
                prev_edge = None

                for i in range(n):
                    # for every vertex we need to do this circle way of checking if
                    # the vertex is inside the range for indices
                    v1, v2 = indices[i], indices[(i + 1) % n]
                    # and we check which edge will add to the object
                    key = (min(v1, v2), max(v1, v2))

                    if key not in self.edges:
                        edge = Edge(v1, v2)
                        self.edges[key] = edge
                    else:
                        edge = self.edges[key]

                    if edge.vertex_start == v1:
                        # here we validate if a left face is already in the object data
                        # and if not, we add the face we just created to that
                        edge.left_face = face if edge.left_face is None else edge.left_face
                    else:
                        # if its not the start_vertex, than we are working with the right face
                        edge.right_face = face if edge.right_face is None else edge.right_face
                        
                    if prev_edge:
                        # and here we do the same thing but for the edges
                        if edge.vertex_start == v1:
                            edge.prev_left = prev_edge
                            prev_edge.nex_left = edge
                        else: 
                            edge.prev_right = prev_edge
                            prev_edge.next_right = edge
                    
                    prev_edge = edge
                face.edge = prev_edge
                face_id += 1