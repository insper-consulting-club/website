import open 3d as o3d

pcd = o3d.io.read_point_cloud("garden.ply")
print(pcd)