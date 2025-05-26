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
    def __init__(self):
        self.vertices = {}
        self.edges = {}
        self.faces = {}
    
    def load_obj(self, filename):
        self.vertices.clear()
        self.edges.clear()
        self.faces.clear()

        file_vertex_id_counter = 1
        parsed_vertices = {}

        with open(filename) as f:
            lines = f.readlines()

        for line in lines:
            if line.startswith('v '):
                parts = line.strip().split()
                if len(parts) >= 4:
                    x, y, z = parts[1], parts[2], parts[3]
                    current_v_id = file_vertex_id_counter
                    self.vertices[current_v_id] = Vertex(current_v_id, (float(x), float(y), float(z)))
                    parsed_vertices[current_v_id] = self.vertices[current_v_id] # Guardar referência se necessário
                    file_vertex_id_counter += 1
                else: print(f"Warning: ignored edge: {line.strip()}")
        
        face_id_counter = 1

        for line in lines:
            if line.startswith('f '):
                current_face_obj = Face(face_id_counter)
                
                try:
                    face_vertex_ids_in_obj_order = [int(p.split('/')[0]) for p in line.strip().split()[1:]]
                except ValueError:
                    print(f"Warning: malformed edge or id not in the vertex object: {line.strip()}")
                    continue

                num_verts_in_face = len(face_vertex_ids_in_obj_order)

                if num_verts_in_face < 3:
                    print(f"Warning: Face {face_id_counter} with {num_verts_in_face} vertexes, ignored.")
                    continue

                self.faces[face_id_counter] = current_face_obj
                
                ordered_canonical_edges_for_face = []
                edge_orientations_relative_to_face = []

                for i in range(num_verts_in_face):
                    v_start_face = face_vertex_ids_in_obj_order[i]
                    v_end_face = face_vertex_ids_in_obj_order[(i + 1) % num_verts_in_face]

                    if v_start_face not in self.vertices or v_end_face not in self.vertices:
                        print(f"Warning: Face {face_id_counter} uses the vertex {v_start_face} or the vertex {v_end_face} which doesn't exists.")
                        if current_face_obj.index in self.faces:
                             # if already in the list, we remove it
                             del self.faces[current_face_obj.index]
                        ordered_canonical_edges_for_face = []
                        break

                    edge_key = tuple(sorted((v_start_face, v_end_face)))

                    canonical_edge = self.edges.get(edge_key)
                    if not canonical_edge:
                        canonical_edge = Edge(edge_key[0], edge_key[1])
                        self.edges[edge_key] = canonical_edge
                    
                    ordered_canonical_edges_for_face.append(canonical_edge)

                    # If canonical_edge.vertex_start == v_start_face, the orientation
                    # (v_start_face -> v_end_face) is alingned with the orientation for canonical_edge.
                    # so the face is left to the canonical_edge.
                    is_aligned_with_canonical = (canonical_edge.vertex_start == v_start_face)
                    edge_orientations_relative_to_face.append(is_aligned_with_canonical)

                    if is_aligned_with_canonical:
                        if canonical_edge.left_face is None:
                            canonical_edge.left_face = current_face_obj

                    else: 
                        # face edge is opposite from the canonical_edge, meaning that is the face to the right.
                        if canonical_edge.right_face is None:
                            canonical_edge.right_face = current_face_obj
                        
                # check for possible errors
                if not ordered_canonical_edges_for_face:
                    face_id_counter +=1 
                    continue


                # define face.edge as the first edge
                if ordered_canonical_edges_for_face:
                    current_face_obj.edge = ordered_canonical_edges_for_face[0]

                # configure pointers next and prev to the face cycle
                # there was an error with this logic (was using next_left in the wrong place)
                for i in range(num_verts_in_face):
                    edge_c = ordered_canonical_edges_for_face[i]
                    edge_p = ordered_canonical_edges_for_face[(i - 1 + num_verts_in_face) % num_verts_in_face]
                    
                    c_is_aligned = edge_orientations_relative_to_face[i]
                    p_is_aligned = edge_orientations_relative_to_face[(i - 1 + num_verts_in_face) % num_verts_in_face]

                    # now we check if the previous is alingned with the canonical face
                    if p_is_aligned:
                        edge_p.next_left = edge_c
                    else: 
                        edge_p.next_right = edge_c
                    
                    if c_is_aligned: 
                        edge_c.prev_left = edge_p
                    else: 
                        edge_c.prev_right = edge_p
                
                face_id_counter += 1