import os
from pathlib import Path
from winged_edge import EdgeMesh

def main():
    # this code takes the 'Trabalho' directory to work as a root dir
    root_dir = Path(__file__).resolve().parent.parent
    objects_dir = root_dir/'Objects'

    if not objects_dir.exists() or not objects_dir.is_dir():
        print(f'Directory not found in {objects_dir}')
        return
    
    # grab every .obj file from the objects directory
    obj_files = list(objects_dir.glob('*.obj'))

    if not obj_files:
        print(f'No .obj file was found in {objects_dir}')
        return
    
    meshes = {}

    for obj_file in obj_files:
        mesh = EdgeMesh()
        mesh.load_obj(obj_file)
        meshes[obj_file.name] = mesh

        print(f'Loaded {obj_file.name}')

    # now we start the code for the user interaction
    file_names = list(meshes.keys())
    print('Available objects:')
    for i, name in enumerate(file_names, start=1):
        print(f'{i}: {name}')
    selection = int(input('Choose one of the available objects: '))
    mesh = meshes[file_names[selection - 1]]

    # main loop
    while True:
        print('\nAvailable functions:\
              \n1: - Faces with the same vertex\
              \n2: - Edges with the same vertex\
              \n3: - Faces with the same edges\
              \n4: - Edges in a Face\
              \n5: - Faces adjacent to a face\
              \n0: - Leave')
        
        option = int(input('Select the option: '))

        clear()

        match(option):
            case 1:
                v_id = int(input('Vertex id: '))
                # faces have all values for faces that have the same v_id
                faces = [f.index for f in mesh.faces.values() if v_id in get_face_vertices(f, mesh)]
                print('Faces that share the same vertex:', faces)
                
            case 2:
                v_id = int(input('Vertex id: '))
                edges = [key for key, e in mesh.edges.items() if v_id in key]
                print('Edges connected by the same vertex: ', edges)

            case 3:
                v1 = int(input('Vertex start id: '))
                v2 = int(input('Vertex end id: '))
                key = min(v1, v2), max(v1, v2)
                edge = mesh.edges.get(key)

                if edge:
                    faces = []
                    if edge.left_face: faces.append(edge.left_face.index)
                    if edge.right_face: faces.append(edge.right_face.index)
                    print('Faces that share the same edge: ', faces)
                else:
                    print('Edge not found')

            case 4:
                f_id = int(input('Face id: '))
                face = mesh.faces.get(f_id)

                if face:
                    edges = []
                    start = face.edge
                    current = start

                    while current:
                        key = (min(current.vertex_start, current.vertex_end),
                               max(current.vertex_start, current.vertex_end))
                        edges.append(key)
                        current = current.next_left if current.left_face == face else current.nex_right
                        
                        if current == start:
                            break
                    
                    print('Face edges: ', edges)
                else:
                    print('Face id not found')
                
            case 5:
                f_id = int(input('Face id: '))
                face = mesh.faces.get(f_id)

                if face:
                    # for option 5, we return a set of adjacent faces
                    adj = set()
                    start = face.edge
                    current = start

                    while current:
                        # here we try to find a neighbor face to the face id
                        neighbor = current.right_face if current.left_face == face else current.left_face
                        
                        if neighbor:
                            adj.add(neighbor.index)
                        
                        current = current.next_left if current.left_face == face else current.next_right

                        if current == start:
                            break
                    
                    print('Adjacent faces:', list(adj))
                else:
                    print('Face id not found')

            case 0:
                break

            case default:
                print('Invalid option')

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# create an auxiliar function to clean up the code
def get_face_vertices(face, mesh):
    vertices = []
    start = face.edge
    current = start

    while current:
        # here we check if we need to run the edge in clockwise or counter-clockwise
        if current.left_face == face:
            vertices.append(current.vertex_start)
            current = current.next_left
        else:
            vertices.append(current.vertex_end)
            current = current.next_right
        # and if we end up at the start, we found all vertices
        if current == start:
            break
    
    return vertices

if __name__ == '__main__':
    main()