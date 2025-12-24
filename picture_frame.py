"""
Classic Picture Frame using build123d

This creates a traditional picture frame with:
- Decorative molding profile
- Rabbet (rebate) to hold the painting/glass
- Mitered corners
"""
# %%
from build123d import *
from ocp_vscode import show

# Frame dimensions (all in mm)
# These define the opening size for the painting
painting_width = 200  # Width of the painting/image
painting_height = 150  # Height of the painting/image

# Frame profile dimensions
frame_width = 40  # Width of the frame molding
frame_depth = 20  # Total depth of the frame
rabbet_width = 8  # Width of the rabbet (ledge for painting)
rabbet_depth = 6  # Depth of the rabbet

# Decorative profile parameters
outer_curve_radius = 5  # Radius of outer decorative curve
inner_step = 3  # Height of inner decorative step


def create_picture_frame(
    width: float = painting_width,
    height: float = painting_height
) -> Part:
    """
    Create a complete picture frame.
    
    The approach: Create the outer shape, then subtract the inner opening
    and add the decorative profile details.
    
    Args:
        width: Inner width (painting width)
        height: Inner height (painting height)
    
    Returns:
        The complete picture frame as a Part
    """
    
    # Outer dimensions
    outer_width = width + 2 * frame_width
    outer_height = height + 2 * frame_width
    
    with BuildPart() as frame:
        # Create the main frame body as a box
        Box(outer_width, outer_height, frame_depth, 
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        
        # Cut out the center opening (painting area)
        with BuildSketch(Plane.XY.offset(frame_depth)) as opening:
            Rectangle(width, height)
        extrude(amount=-frame_depth, mode=Mode.SUBTRACT)
        
        # Cut the rabbet (ledge for holding the painting/glass)
        # This is a step on the back side of the frame
        rabbet_opening_width = width + 2 * rabbet_width
        rabbet_opening_height = height + 2 * rabbet_width
        with BuildSketch(Plane.XY) as rabbet:
            Rectangle(rabbet_opening_width, rabbet_opening_height)
        extrude(amount=rabbet_depth, mode=Mode.SUBTRACT)
        
        # Add decorative profile to the top surface
        # Chamfer/round the outer top edges for the classic frame look
        
        # Get the top outer edges (the 4 edges on top face at the outer perimeter)
        top_face = frame.faces().sort_by(Axis.Z).last
        outer_edges = top_face.edges().filter_by(
            lambda e: abs(e.center().X) > width/2 + frame_width/2 - 1 or 
                      abs(e.center().Y) > height/2 + frame_width/2 - 1
        )
        
        # Fillet the outer top edges for a rounded decorative look
        if len(outer_edges) > 0:
            fillet(outer_edges, radius=outer_curve_radius)
        
        # Chamfer the inner top edges (transition into the frame face)
        inner_top_edges = top_face.edges().filter_by(
            lambda e: abs(e.center().X) < width/2 + 1 and 
                      abs(e.center().Y) < height/2 + 1
        )
        
        # Add a slight chamfer on the inner edge
        if len(inner_top_edges) > 0:
            chamfer(inner_top_edges, length=inner_step)
    
    return frame.part


# Create the frame
frame = create_picture_frame()

# Display the frame
show(frame)

# Export to STEP file for use in other CAD software
export_step(frame, "picture_frame.step")
print(f"Frame created successfully!")
print(f"  Painting opening: {painting_width}mm x {painting_height}mm")
print(f"  Frame width: {frame_width}mm")
print(f"  Overall size: {painting_width + 2*frame_width}mm x {painting_height + 2*frame_width}mm")

# %%
