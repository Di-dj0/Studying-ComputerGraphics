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
        print(f'Processing {obj_file.name}')

        mesh = EdgeMesh()
        mesh.load_obj(obj_file)
        meshes[obj_file.name] = mesh

        print(f'   Vertices: {len(mesh.vertices)}')
        print(f'   Faces: {len(mesh.faces)}')
        print(f'   Edges: {len(mesh.edges)}')

if __name__ == "__main__":
    main()