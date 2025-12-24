"""
Classic Picture Frame using build123d - Swept Profile Version

This creates a traditional picture frame by sweeping a decorative
profile along the frame edges. The profile features:
- Back: Rabbet (rebate) to hold the painting/glass
- Front: Decorative poly-Bezier curve for a classic ornate look
"""
# %%
from build123d import *
from ocp_vscode import show

# Frame dimensions (all in mm)
painting_width = 200  # Width of the painting/image
painting_height = 150  # Height of the painting/image

# Frame profile dimensions
frame_width = 40  # Width of the frame molding
frame_depth = 20  # Total depth of the frame
rabbet_width = 8  # Width of the rabbet (ledge for painting)
rabbet_depth = 6  # Depth of the rabbet


def create_frame_profile() -> Face:
    """
    Create the cross-sectional profile of the frame molding.
    
    The profile is created in the XY plane, then rotated as needed.
    - X axis: width across the molding (0 = outer edge, frame_width = inner edge)
    - Y axis: height of the molding (0 = back, frame_depth = front/top)
    
    Returns:
        Face: The profile face in XY plane
    """
    with BuildSketch(Plane.XY) as profile:
        with BuildLine() as outline:
            # Profile coordinates: (x, y)
            # X: 0 = outer edge of frame, frame_width = inner edge (toward painting)
            # Y: 0 = back (against wall), frame_depth+ = front (decorative top)
            
            # === BACK SIDE (Y=0, with rabbet) ===
            # Start at outer-back corner, go toward inner edge
            l1 = Line((0, 0), (frame_width - rabbet_width, 0))
            
            # Rabbet step up
            l2 = Line(l1 @ 1, (frame_width - rabbet_width, rabbet_depth))
            
            # Rabbet ledge toward inner edge
            l3 = Line(l2 @ 1, (frame_width, rabbet_depth))
            
            # === INNER EDGE ===
            # Inner edge going up to top
            l4 = Line(l3 @ 1, (frame_width, frame_depth))
            
            # === TOP/FRONT SIDE - Decorative Bezier curve ===
            # Going from inner edge toward outer edge with decorative curve
            peak_height = frame_depth + 8  # How high the decorative peak rises
            
            # Bezier from inner to outer (X decreasing from frame_width to 0)
            bezier = Bezier(
                l4 @ 1,  # Start: inner top corner
                (frame_width * 0.85, frame_depth + 4),  # Control 1: slight rise
                (frame_width * 0.75, peak_height),  # Control 2: toward peak
                (frame_width * 0.6, peak_height),  # Peak plateau start
            )
            
            bezier2 = Bezier(
                bezier @ 1,
                (frame_width * 0.45, peak_height),  # Peak plateau end
                (frame_width * 0.4, peak_height - 5),  # Starting descent
                (frame_width * 0.2, frame_depth + 5),  # Control: descending
            )
            
            bezier3 = Bezier(
                bezier2 @ 1,
                (frame_width * 0.05, frame_depth + 1),  # Almost at outer edge
                (0, frame_depth),  # End at outer top corner
            )
            
            # === OUTER EDGE ===
            # Outer edge going down to back, closing the profile
            l5 = Line(bezier3 @ 1, (0, 0))
        
        make_face()
    
    return profile.face()

def create_picture_frame(
    width: float = painting_width + 2 * frame_width,
    height: float = painting_height + 2 * frame_width
) -> Solid:
    orientations = {
        "left": {"loc": Location((0, 0, 0), (90, 0, 0)), "len": height},  # Extrudes along +X
        "right": {"loc": Location((width, -height, 0), (90, 180, 0)), "len": height},  # Extrudes along -X
        "bottom": {"loc": Location((0, -height, 0), (90, 90, 0)), "len": width},  # Extrudes along +Y
        "top": {"loc": Location((width, 0, 0), (90, -90, 0)), "len": width},  # Extrudes along -Y
    }

    sides = []
    for side, props in orientations.items():
        length = props["len"]
        side = extrude(
            create_frame_profile(),
            amount=length,
        )
        # miter cuts at corners 45 degrees
        cut_one = Box(
            length,
            frame_depth * 2,
            length * 4,
            align=(Align.MIN, Align.CENTER, Align.CENTER)
        ).locate(Location((0,frame_depth,0), (0,45,0)))
        side = side.cut(cut_one)

        cut_two = Box(
            length,
            frame_depth * 2,
            length * 4,
            align=(Align.MIN, Align.CENTER, Align.CENTER)
        ).locate(Location((0,frame_depth,length), (0,-45,0)))
        side = side.cut(cut_two)
        
        side = side.locate(props["loc"])
        sides.append(side)
    
    # Combine all sides into one frame
    return sides[0] + sides[1] + sides[2] + sides[3]
    # return sides[0]

# Create the frame
frame = create_picture_frame()

# Display the frame
show(frame)

# %%
