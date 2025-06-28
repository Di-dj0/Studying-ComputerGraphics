import pygame
import sys
import os
import numpy as np
import copy

# using the same functions from the old main.py file
from winged_edge import EdgeMesh, save_mesh_to_obj
import transformations as transform

# window configuration
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800
GUI_WIDTH = 250
VIEWPORT_WIDTH = SCREEN_WIDTH - GUI_WIDTH
BACKGROUND_COLOR = (20, 20, 30)
PANEL_COLOR = (40, 40, 50)
LINE_COLOR = (200, 200, 200)
TEXT_COLOR = (230, 230, 230)
BUTTON_COLOR = (70, 70, 90)
BUTTON_HOVER_COLOR = (100, 100, 120)
INPUT_ACTIVE_COLOR = (200, 200, 200)
INPUT_INACTIVE_COLOR = (150, 150, 150)

class Button:

    def __init__(self, rect, text, font):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.is_hovered = False

    def draw(self, surface):
        # this is used for drawing modifications to the buttons
        color = BUTTON_HOVER_COLOR if self.is_hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        
        text_surf = self.font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered
    
class InputBox:

    def __init__(self, rect, font, text=''):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.color = INPUT_INACTIVE_COLOR
        self.text = text
        self.text_surface = self.font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # validates if the user clicked in the box
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            # change the box color if so
            self.color = INPUT_ACTIVE_COLOR if self.active else INPUT_INACTIVE_COLOR
        
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                    self.color = INPUT_INACTIVE_COLOR
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                # allows only numbers, dots and slashs (for negative values)
                elif event.unicode.isdigit() or event.unicode == '.' or event.unicode == '-':
                    self.text += event.unicode
                # and then renders the new text
                self.text_surface = self.font.render(self.text, True, TEXT_COLOR)

    def draw(self, screen):
        # draw the box for the input
        screen.blit(self.text_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2, border_radius=3)

def project_orthographic(coords_3d, scale, offset):
    # we need 3d coordinates to project in the 2d space
    # so that we can show in the window
    x, y, z = coords_3d
    # the Y axis is inverted in pygame applications (-y)
    x_proj = x * scale + offset[0]
    y_proj = -y * scale + offset[1]
    return int(x_proj), int(y_proj)

def apply_transformation_to_mesh(mesh_obj, transformation_matrix):
    if not mesh_obj or transformation_matrix is None:
        return
    # this code was modified so that we can see the transformation matrix in the console
    print("\nTransformation matrix:")
    print(transformation_matrix)
    print("-----------------------\n\n")
    
    # and this is the logic for the transformation matrix coordinates extraction
    for vertex in mesh_obj.vertices.values():
        original_coord = np.array([*vertex.coord, 1.0])
        transformed_coord = transformation_matrix @ original_coord
        w = transformed_coord[3]
        if w != 0:
            vertex.coord = (transformed_coord[0] / w, transformed_coord[1] / w, transformed_coord[2] / w)

def main():
    # start pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Obj Visualizer")
    clock = pygame.time.Clock()
    font_small = pygame.font.SysFont("Arial", 16)
    font_large = pygame.font.SysFont("Arial", 20, bold=True)
    font_label = pygame.font.SysFont("Arial", 18, bold=True)

    # start the reading for .obj files in /Objects
    obj_path = None
    mesh = None
    
    # search and list every .obj file
    try:
        objects_dir = "Objects"
        if not os.path.isdir(objects_dir):
            print(f"Error: Directory '{objects_dir}' not found.\nClosing")
            pygame.quit()
            sys.exit()

        # create a list with every file in the directory that ends with .;bj
        obj_files = [f for f 
                    in os.listdir(objects_dir) 
                    if f.endswith('.obj')]

        if not obj_files:
            print(f"No .obj file was found in '{objects_dir}'.\nClosing")
            pygame.quit()
            sys.exit()

        # if files were found, we ask for a selection
        print("Please choose one file to visualize")
        for i, filename in enumerate(obj_files):
            print(f"  {i + 1}: {filename}")

        while True:
            try:
                choice = int(input("Input the number for the file "))
                if 1 <= choice <= len(obj_files):
                    chosen_file = obj_files[choice - 1]
                    obj_path = os.path.join(objects_dir, chosen_file)
                    break
                else:
                    print("Wrong value, please input a value in the list.")
            except ValueError:
                print("Please use only numbers.")

    except Exception as e:
        print(f"There was an error while trying to load {e}")
        pygame.quit()
        sys.exit()

    # if an object was successfully choosed
    try:
        mesh = EdgeMesh()
        mesh.load_obj(obj_path)
        # we create a copy of the original mesh for the "reset" option
        original_mesh = copy.deepcopy(mesh) 
        print(f"Mesh '{obj_path}' loaded. Starting GUI.")
    except Exception as e:
        print(f"There was an error loading '{obj_path}': {e}")
        pygame.quit()
        sys.exit()

    # here we create the buttons and input boxes lists in the GUI
    input_boxes = {}
    buttons = {}
    start_x, y_pos = SCREEN_WIDTH - GUI_WIDTH + 15, 50
    input_w, input_h = 100, 30
    label_w = 40

    # for every section we create a new screen.blit() with the respected title:
    
    # translation
    y_pos += 20
    screen.blit(font_label.render("Translation", True, TEXT_COLOR), (start_x, y_pos))
    y_pos += 30
    for i, axis in enumerate(['X', 'Y', 'Z']):
        screen.blit(font_small.render(f"{axis}:", True, TEXT_COLOR), (start_x, y_pos + 5))
        box = InputBox((start_x + label_w, y_pos, input_w, input_h), font_small, '0.0')
        input_boxes[f'translate_{axis.lower()}'] = box
        y_pos += 40
    buttons['translate'] = Button((start_x, y_pos, 220, 35), "Apply translation", font_small)
    y_pos += 60

    # rotation
    screen.blit(font_label.render("Rotation (in degrees)", True, TEXT_COLOR), (start_x, y_pos))
    y_pos += 30
    for i, axis in enumerate(['X', 'Y', 'Z']):
        screen.blit(font_small.render(f"Axis {axis}:", True, TEXT_COLOR), (start_x, y_pos + 5))
        box = InputBox((start_x + label_w + 20, y_pos, input_w, input_h), font_small, '0.0')
        input_boxes[f'rotate_{axis.lower()}'] = box
        y_pos += 40
    buttons['rotate'] = Button((start_x, y_pos, 220, 35), "Apply rotation", font_small)
    y_pos += 60

    # scale
    screen.blit(font_label.render("Scale", True, TEXT_COLOR), (start_x, y_pos))
    y_pos += 30
    for i, axis in enumerate(['X', 'Y', 'Z']):
        screen.blit(font_small.render(f"Axis {axis}:", True, TEXT_COLOR), (start_x, y_pos + 5))
        box = InputBox((start_x + label_w, y_pos, input_w, input_h), font_small, '1.0')
        input_boxes[f'scale_{axis.lower()}'] = box
        y_pos += 40
    buttons['scale'] = Button((start_x, y_pos, 220, 35), "Apply scale", font_small)

    # control buttons
    reset_btn = Button((start_x, SCREEN_HEIGHT - 110, 220, 35), "Reset position", font_small)
    save_btn = Button((start_x, SCREEN_HEIGHT - 60, 220, 35), "Save to .obj", font_small)

    # main loop
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        # event manager for clicks and inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # check for clicks in the input_boxes
            for box in input_boxes.values():
                box.handle_event(event)
            
            # logic behind the apply buttons
            if buttons['translate'].is_clicked(event):
                try:
                    tx = float(input_boxes['translate_x'].text or 0.0)
                    ty = float(input_boxes['translate_y'].text or 0.0)
                    tz = float(input_boxes['translate_z'].text or 0.0)
                    matrix = transform.build_transformation_matrix([('translate', tx, ty, tz)])
                    apply_transformation_to_mesh(mesh, matrix)
                except ValueError:
                    print("Error: invalid value. Use only numbers.")

            if buttons['rotate'].is_clicked(event):
                try:
                    # rotations are apply one by one in this logic
                    rx = float(input_boxes['rotate_x'].text or 0.0)
                    ry = float(input_boxes['rotate_y'].text or 0.0)
                    rz = float(input_boxes['rotate_z'].text or 0.0)
                    
                    transforms = []
                    if rx != 0: transforms.append(('rotateX', rx))
                    if ry != 0: transforms.append(('rotateY', ry))
                    if rz != 0: transforms.append(('rotateZ', rz))

                    if transforms:
                        matrix = transform.build_transformation_matrix(transforms)
                        apply_transformation_to_mesh(mesh, matrix)

                except ValueError:
                    print("Error: invalid value. Use only numbers.")

            if buttons['scale'].is_clicked(event):
                try:
                    sx = float(input_boxes['scale_x'].text or 1.0)
                    sy = float(input_boxes['scale_y'].text or 1.0)
                    sz = float(input_boxes['scale_z'].text or 1.0)
                    matrix = transform.build_transformation_matrix([('scale', sx, sy, sz)])
                    apply_transformation_to_mesh(mesh, matrix)
                except ValueError:
                    print("Error: invalid value. Use only numbers.")

            # this checks for control buttons usage
            if reset_btn.is_clicked(event):
                mesh = copy.deepcopy(original_mesh)
                print("Reseted.")

            if save_btn.is_clicked(event):
                try:
                    save_mesh_to_obj(mesh, obj_path)
                    print(f"Saved in '{obj_path}'")
                except Exception as e:
                    print(f"Error while saving: {e}")

        # screen.fill is used to create the start screen
        screen.fill(BACKGROUND_COLOR)
        pygame.draw.rect(screen, PANEL_COLOR, (SCREEN_WIDTH - GUI_WIDTH, 0, GUI_WIDTH, SCREEN_HEIGHT))
        
        # draw every section name
        y_pos_draw = 50
        y_pos_draw += 20
        screen.blit(font_label.render("Translation", True, TEXT_COLOR), (start_x, y_pos_draw))
        y_pos_draw += 150
        screen.blit(font_label.render("Rotation (degrees)", True, TEXT_COLOR), (start_x, y_pos_draw))
        y_pos_draw += 180
        screen.blit(font_label.render("Scale", True, TEXT_COLOR), (start_x, y_pos_draw))
        
        # draw every box and button
        for box in input_boxes.values():
            box.draw(screen)
        for btn in buttons.values():
            btn.check_hover(mouse_pos)
            btn.draw(screen)
        # draw the control buttons
        reset_btn.check_hover(mouse_pos)
        reset_btn.draw(screen)
        save_btn.check_hover(mouse_pos)
        save_btn.draw(screen)

        # and here we translate the 3d object to a 2d viewport
        projection_offset = (VIEWPORT_WIDTH / 2, SCREEN_HEIGHT / 2)
        for edge in mesh.edges.values():
            v_start_coords = mesh.vertices[edge.vertex_start].coord
            v_end_coords = mesh.vertices[edge.vertex_end].coord
            p_start = project_orthographic(v_start_coords, 200, projection_offset)
            p_end = project_orthographic(v_end_coords, 200, projection_offset)
            pygame.draw.line(screen, LINE_COLOR, p_start, p_end, 1)

        # this step is used to update the screen at 60 hertz
        # and probably theres a better way to do it 
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()