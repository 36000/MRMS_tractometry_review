from fury import actor, window
import numpy as np

def make_endpoint(center, radii):
    # Create an empty ROI mask with the desired shape
    endpoint_roi_mask = np.zeros((50, 50, 50))

    # Define a grid of coordinates
    y, x, z = np.ogrid[-center[0]:50-center[0], -center[1]:50-center[1], -center[2]:50-center[2]]

    # Equation for an ellipsoid (without noise)
    potato_mask = (x/radii[0])**2 + (y/radii[1])**2 + (z/radii[2])**2

    # Create a binary mask for the ellipsoid, adding some noise to give a more "potato-like" shape
    noise = np.random.normal(scale=0.1, size=potato_mask.shape)
    potato_mask = potato_mask + noise
    potato_mask = potato_mask < 1

    # Threshold the potato mask to keep it binary after adding noise
    endpoint_roi_mask[potato_mask > 0.5] = 1

    return endpoint_roi_mask

endpoint_roi_mask1 = make_endpoint(np.array([15, 15, 15]), np.array([8, 6, 5]))
endpoint_roi_mask2 = make_endpoint(np.array([45, 45, 45]), np.array([4, 4, 2]))
endpoint_roi_mask3 = make_endpoint(np.array([45, 35, 35]), np.array([2, 4, 4]))

# Function to create a unique streamline
def create_streamline(*points, num_points=100, scale=1.0):
    segments = []
    for idx in range(1, len(points)):
        segments.append(np.linspace(points[idx-1], points[idx], num_points//len(points)))
    streamline = np.concatenate(segments, axis=0)
    noise = np.random.normal(scale=scale, size=(len(streamline), 3))  # Adding some random noise

    # Create a moving average filter
    filter_size = 5
    window = np.ones(filter_size)/filter_size

    # Apply the moving average filter
    for dimidx in range(3):
        noise[:, dimidx] = np.convolve(noise[:, dimidx], window, mode='same')
    
    streamline += noise
    return streamline

# Create streamlines that go through both ROIs
e1_sz = np.sum(endpoint_roi_mask1)
e2_sz = np.sum(endpoint_roi_mask2)
e3_sz = np.sum(endpoint_roi_mask3)
streamlines_both = [create_streamline(
    np.argwhere(endpoint_roi_mask1)[np.random.randint(0, e1_sz)],
    [20, 20, 20],
    [25, 25, 25],
    [40, 40, 40],
    np.argwhere(endpoint_roi_mask2)[np.random.randint(0, e2_sz)]) for _ in range(100)]

# Create streamlines that go through only ROI 1
streamlines1 = [create_streamline(
    np.argwhere(endpoint_roi_mask1)[np.random.randint(0, e1_sz)],
    [20, 20, 20],
    [28, 28, 28],
    [36, 31, 31],
    np.argwhere(endpoint_roi_mask3)[np.random.randint(0, e3_sz)]) for _ in range(100)]

# Create streamline actors
streamline_actorb = actor.streamtube(streamlines_both, [0, 0, 1])
streamline_actor1 = actor.streamtube(streamlines1, [1, 0, 0])

# Create two ROI masks
roi_mask1 = np.zeros((50, 50, 50))
roi_mask1[22:28, 22:26, 25] = 1

roi_mask2 = np.zeros((50, 50, 50))
roi_mask2[33:37, 33:37, 35] = 1

# Create actors from the ROI data
roi_actor1 = actor.contour_from_roi(roi_mask1, color=(0, 1, 0), opacity=0.5)
roi_actor2 = actor.contour_from_roi(roi_mask2, color=(0, 1, 0), opacity=0.5)

# init scene
scene = window.Scene()
scene.background([1, 1, 1])

# Add the actors to the renderer
scene.add(roi_actor1)
scene.add(roi_actor2)
scene.add(streamline_actorb)
scene.add(streamline_actor1)

# save
window.record(scene, out_path='inclusion.png', size=(1200, 900))
scene.clear()

# Create actors from the ROI data
eroi_actor1 = actor.contour_from_roi(endpoint_roi_mask1, color=(0, 1, 0), opacity=0.5)
eroi_actor2 = actor.contour_from_roi(endpoint_roi_mask2, color=(0, 1, 0), opacity=0.5)

# init scene
scene = window.Scene()
scene.background([1, 1, 1])

# Add the actors to the renderer
scene.add(eroi_actor1)
scene.add(eroi_actor2)
scene.add(streamline_actorb)
scene.add(streamline_actor1)

# save
window.record(scene, out_path='endpoint.png', size=(1200, 900))
scene.clear()

# Create actors from the ROI data
exclusion_roi_mask1 = np.zeros((50, 50, 50))
exclusion_roi_mask1[38, 26:36, 26:36] = 1
exroi_actor1 = actor.contour_from_roi(exclusion_roi_mask1, color=(1, 0, 0), opacity=0.5)

# init scene
scene = window.Scene()
scene.background([1, 1, 1])

# Add the actors to the renderer
scene.add(exroi_actor1)
scene.add(roi_actor1)
scene.add(streamline_actorb)
scene.add(streamline_actor1)

# save
window.record(scene, out_path='exclusion.png', size=(1200, 900))
scene.clear()

# Create actors from the ROI data
region_roi_mask1 = np.zeros((50, 50, 50))
region_roi_mask1[:, 40:, :] = 1 # TODO: need diff sls for this
regroi_actor1 = actor.contour_from_roi(region_roi_mask1, color=(0, 0, 0.2), opacity=0.2)

# init scene
scene = window.Scene()
scene.background([1, 1, 1])

# Add the actors to the renderer
scene.add(regroi_actor1)
scene.add(streamline_actorb)
scene.add(streamline_actor1)

# save
window.record(scene, out_path='region.png', size=(1200, 900))
scene.clear()
