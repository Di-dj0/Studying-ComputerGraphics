import numpy as np
import math

def get_translation_matrix(tx, ty, tz=None):
    # if tz is None, returns a 2D translation matrix (3x3 homogeneous).
    # otherwise, returns a 3D translation matrix (4x4 homogeneous).
    # the same is applied to the functions below
    if tz is None: # 2D
        return np.array([
            [1, 0, tx],
            [0, 1, ty],
            [0, 0, 1]
        ], dtype=float)
    else: # 3D
        return np.array([
            [1, 0, 0, tx],
            [0, 1, 0, ty],
            [0, 0, 1, tz],
            [0, 0, 0, 1]
        ], dtype=float)

def get_scaling_matrix(sx, sy, sz=None):
    if sz is None: # 2D
        return np.array([
            [sx, 0,  0],
            [0,  sy, 0],
            [0,  0,  1]
        ], dtype=float)
    else: # 3D
        return np.array([
            [sx, 0,  0,  0],
            [0,  sy, 0,  0],
            [0,  0,  sz, 0],
            [0,  0,  0,  1]
        ], dtype=float)

def get_rotation_matrix_2d(angle_degrees):
    # Returns a 2D rotation matrix (3x3 homogeneous) for rotation around the origin.
    angle_rad = math.radians(angle_degrees)
    c = math.cos(angle_rad)
    s = math.sin(angle_rad)
    return np.array([
        [c, -s, 0],
        [s,  c, 0],
        [0,  0, 1]
    ], dtype=float)

def get_rotation_matrix_3d(axis, angle_degrees):
    # Returns a 3D rotation matrix (4x4 homogeneous) around a specified axis ('x', 'y', or 'z').
    angle_rad = math.radians(angle_degrees)
    c = math.cos(angle_rad)
    s = math.sin(angle_rad)

    if axis.lower() == 'x':
        return np.array([
            [1, 0,  0, 0],
            [0, c, -s, 0],
            [0, s,  c, 0],
            [0, 0,  0, 1]
        ], dtype=float)
    elif axis.lower() == 'y':
        return np.array([
            [c, 0, s, 0],
            [0, 1, 0, 0],
            [-s,0, c, 0],
            [0, 0, 0, 1]
        ], dtype=float)
    elif axis.lower() == 'z':
        return np.array([
            [c, -s, 0, 0],
            [s,  c, 0, 0],
            [0,  0, 1, 0],
            [0,  0, 0, 1]
        ], dtype=float)
    else:
        raise ValueError("Invalid rotation axis. Must be 'x', 'y', or 'z'.")

def build_transformation_matrix(transform_sequence, dim=3):
    if dim == 3:
        # Start with a 4x4 identity matrix for 3D
        composite_matrix = np.identity(4, dtype=float)
    elif dim == 2:
        # Start with a 3x3 identity matrix for 2D
        composite_matrix = np.identity(3, dtype=float)
    else:
        raise ValueError("Dimension must be 2 or 3.")

    for transform in transform_sequence:
        if not isinstance(transform, tuple) or not transform:
            raise ValueError(f"Each transformation must be a non-empty tuple. Got: {transform}")
        
        operation = transform[0].lower()
        params = transform[1:]
        
        current_transform_matrix = None

        if dim == 3:
            if operation == 'translate':
                if len(params) != 3:
                    raise ValueError(f"Translate 3D expects 3 parameters (tx, ty, tz), got {len(params)} for {transform}")
                
                current_transform_matrix = get_translation_matrix(params[0], params[1], params[2])
            
            elif operation == 'scale':
                if len(params) != 3:
                    raise ValueError(f"Scale 3D expects 3 parameters (sx, sy, sz), got {len(params)} for {transform}")
                
                current_transform_matrix = get_scaling_matrix(params[0], params[1], params[2])
            
            elif operation == 'rotatex':
                if len(params) != 1:
                    raise ValueError(f"RotateX expects 1 parameter (angle_degrees), got {len(params)} for {transform}")
                
                current_transform_matrix = get_rotation_matrix_3d('x', params[0])
            
            elif operation == 'rotatey':
                if len(params) != 1:
                    raise ValueError(f"RotateY expects 1 parameter (angle_degrees), got {len(params)} for {transform}")
                
                current_transform_matrix = get_rotation_matrix_3d('y', params[0])
            
            elif operation == 'rotatez':
                if len(params) != 1:
                    raise ValueError(f"RotateZ expects 1 parameter (angle_degrees), got {len(params)} for {transform}")
                
                current_transform_matrix = get_rotation_matrix_3d('z', params[0])
            
            else:
                raise ValueError(f"Unknown 3D transformation operation: '{operation}' in {transform}")
        
        elif dim == 2:
            if operation == 'translate':
                if len(params) != 2:
                    raise ValueError(f"Translate 2D expects 2 parameters (tx, ty), got {len(params)} for {transform}")
                
                current_transform_matrix = get_translation_matrix(params[0], params[1]) # tz is None
            
            elif operation == 'scale':
                if len(params) != 2:
                    raise ValueError(f"Scale 2D expects 2 parameters (sx, sy), got {len(params)} for {transform}")
                
                current_transform_matrix = get_scaling_matrix(params[0], params[1]) # sz is None
            
            elif operation == 'rotate': # 2D rotation
                if len(params) != 1:
                    raise ValueError(f"Rotate 2D expects 1 parameter (angle_degrees), got {len(params)} for {transform}")
                
                current_transform_matrix = get_rotation_matrix_2d(params[0])
            
            else:
                raise ValueError(f"Unknown 2D transformation operation: '{operation}' in {transform}")

        if current_transform_matrix is not None:
            # To apply T1, then T2, then T3,
            # we do composite_matrix = current_transform_matrix @ composite_matrix
            composite_matrix = current_transform_matrix @ composite_matrix

    return composite_matrix