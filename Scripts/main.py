import os
from pathlib import Path
from winged_edge import EdgeMesh 

def get_face_vertices(face, mesh_obj):
    vertices = []
    if not face.edge:
        return vertices

    start_edge = face.edge
    current_edge = start_edge
    
    # security limit for edges in a face
    MAX_EDGES_PER_FACE = 256 
    if hasattr(mesh_obj, 'edges') and isinstance(mesh_obj.edges, dict) and mesh_obj.edges:
        MAX_EDGES_PER_FACE = len(mesh_obj.edges) + 1

    for _ in range(MAX_EDGES_PER_FACE):
        if not current_edge: 
            break
        
        if current_edge.left_face == face:
            vertices.append(current_edge.vertex_start)
            next_e = current_edge.next_left
        
        elif current_edge.right_face == face: 
            vertices.append(current_edge.vertex_end)
            next_e = current_edge.next_right
        
        else:
            break 

        if not next_e:
            break 
            
        current_edge = next_e
        if current_edge == start_edge:
            break 
    else:
        pass

    return vertices

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    # using resolve() now
    script_dir = Path(__file__).resolve().parent
    possible_objects_dirs = [
        script_dir.parent / 'Objects', 
        script_dir / 'Objects',   
        Path('../Objects').resolve()
    ]
    
    objects_dir = None
    for D_path in possible_objects_dirs:
        if D_path.exists() and D_path.is_dir():
            objects_dir = D_path
            break
    
    if not objects_dir:
        print("Dir 'Objects' not found.")
        user_path = input("Please input the full path for the directory with the .obj files: ")
        objects_dir = Path(user_path)

    if not (objects_dir.exists() and objects_dir.is_dir()):
        print(f"The path '{objects_dir.resolve()}' is not a valid path.\nClosing app.")
        return

    obj_files = list(objects_dir.glob('*.obj'))

    if not obj_files:
        print(f'No .obj file found in {objects_dir.resolve()}')
        return
    
    meshes = {}
    for obj_file in obj_files:
        mesh_instance = EdgeMesh()
        try:
            mesh_instance.load_obj(obj_file) 
            meshes[obj_file.name] = mesh_instance
            print(f"Loaded '{obj_file.name}'. Vertices: {len(mesh_instance.vertices)}, Faces: {len(mesh_instance.faces)}, Edges: {len(mesh_instance.edges)}")
        except Exception as e:
            print(f"Error loading {obj_file.name}: {e}")
            # if more info is needed, we can use the code below
            # import traceback
            # traceback.print_exc()

    file_names = list(meshes.keys())
    if not file_names:
        print("No mesh was successfully built.")
        return

    print('\nFound objects:')
    for i, name in enumerate(file_names, start=1):
        print(f'{i}: {name}')
    
    current_mesh = None
    selected_mesh_name = ""
    while current_mesh is None:
        try:
            selection_input_str = input('Choose one of the objects: ')
            
            if not selection_input_str: 
                return 
            
            selection = int(selection_input_str)
            
            if 1 <= selection <= len(file_names):
                selected_mesh_name = file_names[selection - 1]
                current_mesh = meshes[selected_mesh_name]
                print(f"Object '{selected_mesh_name}' selected.")
                print(f"Vertices: 1-{len(current_mesh.vertices)}, Faces: 1-{len(current_mesh.faces)}, Edges: {len(current_mesh.edges)}")
            
            else:
                print('Not a valid option.')
        except ValueError:
            print('Entrada inválida. Por favor, insira um número.')
        
        except IndexError:
             print('Seleção fora do intervalo. Por favor, tente novamente.')

    while True:
        print(f'\nUsing {selected_mesh_name}')
        print('Avaliable actions:\
              \n1: - Faces that share the same vertex\
              \n2: - Edges that share the same vertex\
              \n3: - Faces that share the same edge\
              \n4: - Edges from a face\
              \n5: - Faces adjacent to a face\
              \n\
              \n0: - close')
        
        option_str = input('Selecione a opção: ')
        
        if not option_str: 
            continue 

        try:
            option = int(option_str)
        except ValueError:
            print("Invalid option.")
            clear() 
            continue

        clear() 

        match(option):

            case 1: 
                try:
                    v_id_input = int(input('Vertex ID: '))
                    
                    if v_id_input not in current_mesh.vertices:
                        print(f"Vertex ID {v_id_input} not found in '{selected_mesh_name}'.")
                        print(f"IDs available: 1 to {len(current_mesh.vertices)}.")
                    
                    else:
                        found_faces = []
                        for f_id, f_obj in current_mesh.faces.items():
                            vertices_da_face = get_face_vertices(f_obj, current_mesh) 
                            if v_id_input in vertices_da_face:
                                found_faces.append(f_id)
                        print(f'Faces that share the same Vertex {v_id_input}:', found_faces) 
                
                except ValueError:
                    print("Vertex ID invalid.")
                
            case 2:
                try:
                    v_id_input = int(input('Vertex ID: '))

                    if v_id_input not in current_mesh.vertices:
                        print(f"Vertex ID {v_id_input} not found in '{selected_mesh_name}'.")
                        print(f"IDs available: 1 to {len(current_mesh.vertices)}.")
                    
                    else:
                        edges_found = [key for key in current_mesh.edges.keys() if v_id_input in key]
                        print(f'Edges conected by the Vertex {v_id_input}: ', edges_found)

                except ValueError:
                    print("Vertex ID invalid.")

            case 3:
                try:
                    v1_input = int(input('Starter Vertex ID'))
                    v2_input = int(input('End Vertex ID'))

                    if v1_input not in current_mesh.vertices or v2_input not in current_mesh.vertices:
                        print(f"One or both Vertex ({v1_input}, {v2_input}) not found in '{selected_mesh_name}'.")
                        print(f"IDs available: 1 to {len(current_mesh.vertices)}.")

                    elif v1_input == v2_input:
                        print("IDs must be different")

                    else:
                        key = tuple(sorted((v1_input, v2_input)))
                        edge = current_mesh.edges.get(key)
                        
                        if edge:
                            faces_found = []
                            if edge.left_face: faces_found.append(edge.left_face.index)
                            if edge.right_face: faces_found.append(edge.right_face.index)
                            print(f'Faces that share the edge ({v1_input}-{v2_input}): ', faces_found)
                        
                        else:
                            print(f'Edge ({v1_input}-{v2_input}) not found.')

                except ValueError:
                    print("Vertex ID invalid.")

            case 4:
                try:
                    f_id_input = int(input('Face ID: '))
                    face = current_mesh.faces.get(f_id_input)

                    if not face:
                        print(f"Face {f_id_input} not found in '{selected_mesh_name}'.")
                        print(f"Available Face IDs : 1 to {len(current_mesh.faces)}.")
                    
                    else:
                        edges_found = []
                        
                        if not face.edge:
                            print(f'Face {f_id_input} doesn\'t have edges or is malformed.')
                        
                        else:
                            start_edge_face = face.edge
                            current_edge_face = start_edge_face
                            iter_limit_face = len(current_mesh.edges) + 1 if current_mesh.edges else 256
                            
                            for _ in range(iter_limit_face): 
                                
                                if not current_edge_face: 
                                    break 
                                
                                key_edge = tuple(sorted((current_edge_face.vertex_start, current_edge_face.vertex_end)))
                                edges_found.append(key_edge)
                                
                                if current_edge_face.left_face == face:
                                    current_edge_face = current_edge_face.next_left
                                elif current_edge_face.right_face == face: 
                                    current_edge_face = current_edge_face.next_right
                                else: 
                                    break
                                
                                if not current_edge_face or current_edge_face == start_edge_face: 
                                    break
                            else: 
                                # limit
                                pass
                        print(f'Arestas na face {f_id_input}: ', edges_found)
                except ValueError:
                    print("Invalid Face ID.")
            
            case 5:
                try:
                    f_id_input = int(input('Face ID: '))
                    face = current_mesh.faces.get(f_id_input)

                    if not face:
                        print(f"Face {f_id_input} not found in '{selected_mesh_name}'.")
                        print(f"Available Face IDs : 1 to {len(current_mesh.faces)}.")

                    else:
                        adj_faces = set()
                        
                        if not face.edge:
                            print(f'Face {f_id_input} doesn\'t have edges or is malformed.')
                        
                        else:
                            start_edge_adj = face.edge
                            current_edge_adj = start_edge_adj
                            iter_limit_adj = len(current_mesh.edges) + 1 if current_mesh.edges else 256
                            for _ in range(iter_limit_adj):
                                if not current_edge_adj: 
                                    break
                                
                                neighbor_face_obj = None
                                if current_edge_adj.left_face == face: 
                                    neighbor_face_obj = current_edge_adj.right_face
                                
                                elif current_edge_adj.right_face == face: 
                                    neighbor_face_obj = current_edge_adj.left_face
                                
                                if neighbor_face_obj: 
                                    adj_faces.add(neighbor_face_obj.index)
                                
                                if current_edge_adj.left_face == face: 
                                    current_edge_adj = current_edge_adj.next_left
                                
                                elif current_edge_adj.right_face == face: 
                                    current_edge_adj = current_edge_adj.next_right
                                
                                else: 
                                    break
                                
                                if not current_edge_adj or current_edge_adj == start_edge_adj: 
                                    break
                            
                            else: 
                                pass
                        
                        print(f'Adjacent Faces to Face {f_id_input}:', list(adj_faces))
                except ValueError:
                    print("Invalid Face ID")

            case 0:
                break

            case default:
                print('Invalid option.')


if __name__ == '__main__':
    main()