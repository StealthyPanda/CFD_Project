
from typing import Callable
import numpy as np
from stl import mesh

Number = int | float
Vector = np.ndarray[Number]
VecOrNum = Vector | Number

def convert_to_parametric():
    pass


def get_curve(
        f : Callable[[VecOrNum], VecOrNum],
        start : float = 0, end : float = 1, N : int = 10
    ) -> tuple[np.ndarray, np.ndarray]:
    
    xs = np.linspace(start, end, N)
    ys = f(xs)
    
    return (xs, ys)


class NACA_Symmetric_Airfoil:
    def __init__(self, thickness : Number) -> None:
        self.t = thickness
    
    def __call__(self, x : VecOrNum) -> VecOrNum:
        return (5 * self.t) * (
            (0.2969 * (x**0.5)) - (0.1260 * x) - (0.3516 * (x**2)) + (0.2843 * (x**3)) - (0.1015 * (x**4))
        )

class NACA_Cambered_Airfoil:
    def __init__(self, m : Number, p : Number) -> None:
        self.m = m
        self.p = p
    
    def __call__(self, x : VecOrNum) -> VecOrNum:
        return (5 * self.t) * (
            (0.2969 * (x**0.5)) - (0.1260 * x) - (0.3516 * (x**2)) + (0.2843 * (x**3)) - (0.1015 * (x**4))
        )








class Curve:
    def __init__(self, **params) -> None:
        self.params = params
    
    def __call__(self, *args) -> VecOrNum:
        pass




def generate_surface_of_revolution(xs:Vector, ys:Vector, N:int=100):
    """
    Generate the surface of revolution by rotating a curve defined by (xs, ys)
    around the x-axis. The surface will be approximated by a set of triangles.

    Args:
        xs: 1D array of x values.
        ys: 1D array of y values corresponding to the curve height.
        N: Number of steps (angular divisions) to rotate the curve.

    Returns:
        stl_mesh: The resulting surface as an STL mesh object.
    """
    xs = np.asarray(xs)
    ys = np.asarray(ys)

    angles = np.linspace(0, 2 * np.pi, N, endpoint=False)
    
    vertices = []
    faces = []
    
    for each in range(len(xs) - 1):
        for every in range(len(angles)):
            x1, y1 = xs[each], ys[each]
            x2, y2 = xs[each + 1], ys[each + 1]
            
            angle1 = angles[every]
            angle2 = angles[(every + 1) % len(angles)]
            
            p1 = [x1, y1 * np.cos(angle1), y1 * np.sin(angle1)]
            p2 = [x1, y1 * np.cos(angle2), y1 * np.sin(angle2)]
            p3 = [x2, y2 * np.cos(angle1), y2 * np.sin(angle1)]
            p4 = [x2, y2 * np.cos(angle2), y2 * np.sin(angle2)]
            
            vlast = len(vertices)
            vertices += [p1, p2, p3, p4]
            
            faces.append([vlast, vlast + 2, vlast + 1])
            faces.append([vlast + 2, vlast + 3, vlast + 1])
    
    
    # Closing the ends
    for each in [0, -1]:
        if ys[each] != 0:
            center = [xs[each], 0, 0]
            v_index_center = len(vertices)
            vertices.append(center)

            for j in range(len(angles)):
                angle1 = angles[j]
                angle2 = angles[(j + 1) % len(angles)]
                
                p1 = [xs[each], ys[each] * np.cos(angle1), ys[each] * np.sin(angle1)]
                p2 = [xs[each], ys[each] * np.cos(angle2), ys[each] * np.sin(angle2)]
                
                v_index = len(vertices)
                vertices.append(p1)
                vertices.append(p2)
                
                faces.append([v_index_center, v_index, v_index + 1])
    
    
    
    vertices = np.array(vertices)
    faces = np.array(faces)
    
    surface_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            surface_mesh.vectors[i][j] = vertices[face[j]]
    
    
    return surface_mesh



def extrude_curve(xs:Vector, ys:Vector, thickness:Number):
    """
    Extrude a 2D closed-loop curve in the 3rd dimension to form a 3D surface.
    
    Args:
        xs: 1D array of x values for the 2D loop.
        ys: 1D array of y values for the 2D loop.
        thickness: the amount to extrude by. (Symmetric extrusion in both directions.)
        
    Returns:
        stl_mesh: The resulting extruded surface as an STL mesh object.
    """
    xs = np.asarray(xs)
    ys = np.asarray(ys)
    
    num_points = len(xs)
    
    vertices = []
    faces = []
    z_min = -thickness / 2
    z_max =  thickness / 2
    
    for i in range(num_points):
        vertices.append([xs[i], ys[i], z_min])
        vertices.append([xs[i], ys[i], z_max])
    
    for i in range(num_points):
        lower1 = i * 2          
        upper1 = lower1 + 1     
        lower2 = (i * 2 + 2) % (2 * num_points)  
        upper2 = lower2 + 1 
        
        faces.append([lower1, upper1, lower2])
        faces.append([upper1, upper2, lower2])
    
    for i in range(1, num_points - 1):
        faces.append([0, i * 2, (i + 1) * 2])
        faces.append([1, (i + 1) * 2 + 1, i * 2 + 1])
    
    vertices = np.array(vertices)
    faces = np.array(faces)
    
    extruded_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            extruded_mesh.vectors[i][j] = vertices[face[j]]
            
    # extruded_mesh.rotate(axis=(0, 1, 0), theta=np.pi/2)
    # extruded_mesh.rotate(axis=(0, 0, 1), theta=np.pi/2)
    extruded_mesh.rotate(axis=(1, 0, 0), theta=-np.pi/2)
    
    return extruded_mesh



def save_stl_file(surface_mesh, filename="surface_of_revolution.stl"):
    """
    Save the given surface mesh to an STL file.
    
    Args:
        surface_mesh: The mesh object to save.
        filename: The name of the STL file.
    """
    surface_mesh.save(filename)
    print(f"STL file saved as {filename}")


from math import radians
def rotate_extruded_curve(extruded_mesh, angle_of_attack: float):
    """
    Rotate the extruded mesh to change the angle of attack without translation.
    
    Args:
        extruded_mesh: The extruded STL mesh object to rotate.
        angle_of_attack: The desired angle of attack in degrees.
    """
    # Convert the angle from degrees to radians
    angle_in_radians = radians(angle_of_attack)

    # Calculate the centroid
    centroid = extruded_mesh.get_mass_properties()[1]
    
    # Ensure that the centroid is precisely at (0, 0, 0)
    if not np.allclose(centroid, [0, 0, 0]):
        # Step 1: Translate to the origin
        extruded_mesh.translate(-centroid)
    
    # Step 2: Rotate around the y-axis
    extruded_mesh.rotate(axis=(0, 1, 0), theta=angle_in_radians)
    
    # Step 3: Translate back to the centroid
    if not np.allclose(centroid, [0, 0, 0]):
        extruded_mesh.translate(centroid)

    return extruded_mesh





if __name__ == '__main__':
    import matplotlib.pyplot as plt
    
    airfoil = NACA_Symmetric_Airfoil(0.1)
    # airfoil_x = np.linspace(0, 1, 20)
    
    
    xs = np.linspace(0, 1, 50)
    xs = (np.logspace(1, 0, 50, endpoint=True) / 10) - 0.1
    # ys = 0.2 * np.exp(-((((xs * 2) - 1) * 2)**2))
    airfoil_curve = airfoil(xs)
    
    airfoil_curve = np.concatenate((airfoil_curve, -airfoil_curve[::-1]))
    xs = np.concatenate((xs, xs[::-1]))
    # xs = np.linspace(0, 1, 20)
    # ys = xs ** 0.5
    
    # xs = airfoil_x
    # ys = airfoil_curve
    plt.plot(xs, airfoil_curve,'.-')
    plt.grid()
    plt.show()
    # exit(0)
    
    # round_surface = generate_surface_of_revolution(xs, ys, 20)
    # round_surface.vectors += [0, 0, 1]
    extruded = extrude_curve(xs, airfoil_curve, 1)
    angles = [45, 50, 55, 60, 65, 70]
    for i, each in enumerate(angles):
        newob = mesh.Mesh(np.copy(extruded.data))
        newob.rotate(axis=(0, 1, 0), theta=-(each / 180.0) * np.pi)
        newob.vectors += [0, 0, 1]
        save_stl_file(newob, f'models/ext_sym_airfoil{each}.stl')
    
    

