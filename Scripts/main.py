import os
from pathlib import Path
from winged_edge import EdgeMesh
from winged_edge import get_face_vertices
from winged_edge import save_mesh_to_obj
import numpy as np
import transformations as T

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# code for the second assigment
def apply_transformations_to_mesh(mesh_obj, transformation_matrix):
    # Applies the given transformation matrix to all vertices of the mesh.
    if mesh_obj is None or transformation_matrix is None:
        print("Error: Mesh object or transformation matrix is not available.")
        return

    count = 0
    for vertex_id, vertex_obj in mesh_obj.vertices.items():
        original_coord = vertex_obj.coord
        
        # Homogeneous coordinates for 3D
        v_homogeneous = np.array([original_coord[0], original_coord[1], original_coord[2], 1.0])
        
        # Apply transformation: M @ v
        transformed_v_homogeneous = transformation_matrix @ v_homogeneous
        
        # Convert back to Cartesian coordinates (perspective division)
        w = transformed_v_homogeneous[3]
        if w == 0: 
            print(f"Warning: Homogeneous w component is zero for vertex {vertex_id} after transformation. Skipping update.")
            continue
        
        # Update vertex coordinate in the mesh object
        vertex_obj.coord = (
            transformed_v_homogeneous[0] / w,
            transformed_v_homogeneous[1] / w,
            transformed_v_homogeneous[2] / w
        )
        count += 1
    print(f"Transformation applied to {count} vertices.")

def handle_transformations_submenu(current_mesh_obj, selected_mesh_name_str):
    if current_mesh_obj is None:
        print("No mesh selected to transform.")
        return

    print(f"\n--- Transformation Submenu for '{selected_mesh_name_str}' ---")

    # as we are working with a sequence of transformations, we will use a list here
    transform_sequence = []

    while True:
        print("\nCurrent transformation sequence (applied in order):")
        
        if not transform_sequence:
            print("  (empty)")
        
        else:
            for i, trans in enumerate(transform_sequence):
                # Format the display of the transformation
                op_name = trans[0]
                params_str = ", ".join(map(str, trans[1:]))
                print(f"  {i+1}. {op_name}({params_str})")
        
        print("\nTransformation options:")
        print("  1. Add Translation (tx, ty, tz)")
        print("  2. Add Scaling (sx, sy, sz)")
        print("  3. Add Rotation around X-axis (angle_degrees)")
        print("  4. Add Rotation around Y-axis (angle_degrees)")
        print("  5. Add Rotation around Z-axis (angle_degrees)")
        print("  6. Clear current sequence")
        print("  7. Finalize sequence and apply to mesh")
        print("  8. Back to main menu")

        sub_option_str = input("Select transformation option: ")
        if not sub_option_str: continue

        try:
            sub_option = int(sub_option_str)

        except ValueError:
            print("Invalid option. Please enter a number.")
            continue
        
        if sub_option == 1:
            try:
                tx = float(input("Enter tx (translation along X): "))
                ty = float(input("Enter ty (translation along Y): "))
                tz = float(input("Enter tz (translation along Z): "))
                transform_sequence.append(('translate', tx, ty, tz))
                print("Translation added to sequence.")
            except ValueError:
                print("Invalid input for translation values. Please enter numbers.")
        
        elif sub_option == 2:
            try:
                sx = float(input("Enter sx (scaling factor for X): "))
                sy = float(input("Enter sy (scaling factor for Y): "))
                sz = float(input("Enter sz (scaling factor for Z): "))
                if sx == 0 or sy == 0 or sz == 0:
                    print("Warning: Scaling factor of zero can make the object disappear or degenerate.")
                transform_sequence.append(('scale', sx, sy, sz))
                print("Scaling added to sequence.")
            except ValueError:
                print("Invalid input for scaling factors. Please enter numbers.")

        elif sub_option == 3:
            try:
                angle = float(input("Enter rotation angle around X-axis (degrees): "))
                transform_sequence.append(('rotateX', angle))
                print("RotationX added to sequence.")
            except ValueError:
                print("Invalid input for angle. Please enter a number.")
        
        elif sub_option == 4:
            try:
                angle = float(input("Enter rotation angle around Y-axis (degrees): "))
                transform_sequence.append(('rotateY', angle))
                print("RotationY added to sequence.")
            except ValueError:
                print("Invalid input for angle. Please enter a number.")

        elif sub_option == 5:
            try:
                angle = float(input("Enter rotation angle around Z-axis (degrees): "))
                transform_sequence.append(('rotateZ', angle))
                print("RotationZ added to sequence.")
            except ValueError:
                print("Invalid input for angle. Please enter a number.")
        
        elif sub_option == 6:
            transform_sequence = []
            print("Transformation sequence cleared.")

        elif sub_option == 7:
            if not transform_sequence:
                print("No transformations in the sequence to apply.")
            else:
                print("Building composite transformation matrix...")
                try:
                    # All transformations are 3D for .obj files
                    composite_matrix = T.build_transformation_matrix(transform_sequence, dim=3)
                    print("Composite Transformation Matrix:\n", composite_matrix)
                    
                    apply_transformations_to_mesh(current_mesh_obj, composite_matrix)
                    print(f"Object '{selected_mesh_name_str}' has been transformed.")
                    print("The transformation is now part of the current object's vertex data.")
                    
                    # Clear sequence after applying
                    transform_sequence = []
                except Exception as e:
                    print(f"An error occurred during transformation: {e}")
            break 

        elif sub_option == 8:
            print("Returning to main menu. Current transformation sequence (if any) discarded.")
            break
        
        else:
            print("Invalid transformation option. Please try again.")
        
        if sub_option not in [7, 8]: 
             input("\nPress Enter to continue with transformations...")
             clear()


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
              \n6: - Apply Transformations to Object\
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

            case 6:
                handle_transformations_submenu(current_mesh, selected_mesh_name)
                save_mesh_to_obj(current_mesh, selected_mesh_name)

            case 0:
                break

            case default:
                print('Invalid option.')


if __name__ == '__main__':
    main()