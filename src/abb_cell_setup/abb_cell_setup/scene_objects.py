import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Pose
from moveit_msgs.msg import PlanningScene, CollisionObject
from shape_msgs.msg import SolidPrimitive


class SceneObjects(Node):
    def __init__(self):
        super().__init__("scene_objects")
        self.publisher = self.create_publisher(PlanningScene, "/planning_scene", 10)
        self.timer = self.create_timer(2.0, self.publish_scene_once)
        self.published = False

    def make_box(self, object_id, frame_id, x, y, z, sx, sy, sz):
        obj = CollisionObject()
        obj.header.frame_id = frame_id
        obj.id = object_id

        primitive = SolidPrimitive()
        primitive.type = SolidPrimitive.BOX
        primitive.dimensions = [sx, sy, sz]

        pose = Pose()
        pose.orientation.w = 1.0
        pose.position.x = x
        pose.position.y = y
        pose.position.z = z

        obj.primitives.append(primitive)
        obj.primitive_poses.append(pose)
        obj.operation = CollisionObject.ADD
        return obj

    def publish_scene_once(self):
        if self.published:
            return

        scene = PlanningScene()
        scene.is_diff = True

        frame_id = "base_link"

        scene.world.collision_objects.append(
            self.make_box("work_table", frame_id, 0.70, 0.00, -0.05, 1.20, 1.20, 0.10)
        )

        scene.world.collision_objects.append(
            self.make_box("pallet", frame_id, 0.55, -0.35, 0.05, 0.40, 0.30, 0.10)
        )

        pickup_positions = [
            (0.45, 0.25, 0.10),
            (0.55, 0.25, 0.10),
            (0.45, 0.15, 0.10),
            (0.55, 0.15, 0.10),
        ]

        for i, (x, y, z) in enumerate(pickup_positions, start=1):
            scene.world.collision_objects.append(
                self.make_box(f"pickup_box_{i}", frame_id, x, y, z, 0.05, 0.05, 0.10)
            )

        placed_positions = [
            (0.50, -0.38, 0.15),
            (0.56, -0.38, 0.15),
            (0.50, -0.30, 0.15),
            (0.56, -0.30, 0.15),
        ]

        for i, (x, y, z) in enumerate(placed_positions, start=1):
            scene.world.collision_objects.append(
                self.make_box(f"place_box_{i}", frame_id, x, y, z, 0.05, 0.05, 0.10)
            )

        self.publisher.publish(scene)
        self.get_logger().info("Published palletizing scene to /planning_scene")
        self.published = True


def main():
    rclpy.init()
    node = SceneObjects()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
