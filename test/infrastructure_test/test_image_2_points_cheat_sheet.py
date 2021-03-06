import numpy as np
from math import tan, atan


class TestPointGetter(object):
    def __init__(self):
        self.centre_distance = 9.0
        self.base_distance = 9.0
        self.camera_focal_length = 3.0 #1.0
        self.laser_distance = 9.31977282411 # 125

        self.sensor_size_x = 3.0 #0.750
        self.sensor_size_y = 3.0 #0.562
        self.resolution_x = 3.0 #640
        self.resolution_y = 3.0 #480

        self.half_sensor_x = self.sensor_size_x / 2.0
        self.half_sensor_y = self.sensor_size_y / 2.0
        self.pixel_size_x = self.sensor_size_x / self.resolution_x
        self.pixel_size_y = self.sensor_size_y / self.resolution_y
        self.half_pixel_x = self.pixel_size_x / 2.0
        self.half_pixel_y = self.pixel_size_y / 2.0
        self.laser_rad = atan(self.base_distance / self.laser_distance)   # Laser Intersection Angle x/z plane

        self.print_setup()

        results = []
        # for pixel_y in range(self.resolution_y):
            # for pixel_x in range(self.resolution_x):
                # results.append(self.get_point(pixel_x, pixel_y))
        print("(Pix X, Pix Y) => (     Pos X,      Pos Y) [  Cam X dg    Cam Y dg] =>      X    ,     Y    ,     Z     ")
        results.append(self.get_point(0, 0))
        results.append(self.get_point(1, 0))
        results.append(self.get_point(2, 0))


        print("")
        print self.get_formatted_float_list(results)


    def get_point(self, pixel_y, pixel_x):
        pos_x = ((pixel_x / float(self.resolution_x)) * self.sensor_size_x) - self.half_sensor_x + self.half_pixel_x
        pos_y = (((self.resolution_y - pixel_y) / float(self.resolution_y)) * self.sensor_size_y) - self.half_sensor_y - self.half_pixel_y

        camera_x_rad = atan(-pos_x / self.camera_focal_length)   #Camera Ray Angle x/z place
        camera_y_rad = atan(pos_y / self.camera_focal_length)   #Camera Ray Angle x/y plane
        # laser_rad = self.laser_rad if pos_x > 0 else np.pi - self.laser_rad

        z1 = (self.laser_distance * tan(self.laser_rad))/(tan(camera_x_rad) + tan(self.laser_rad))
        z0 = self.laser_distance - z1

        z = self.centre_distance - z1
        x = -tan(self.laser_rad) * z0
        y = tan(camera_y_rad) * z1

        # print("{: 8.3f}, {: 8.3f}".format(z0, z1))
       
        print("({: 5}, {: 5}) => ({: 10.5f}, {: 10.5f}) [{: 10.5f}, {: 10.5f}] => {: 10.5f},{: 10.5f},{: 10.5f}".format(pixel_x, pixel_y, pos_x, pos_y, np.rad2deg(camera_x_rad), np.rad2deg(camera_y_rad), x, y, z))

        return [x, y, z]

    def get_formatted_float_list(self, alist, aformat="{: 8.3f}", inner=False):
        if type(alist) != list:
            return (aformat + ", ").format(alist)
        string = "["
        for item in alist:
            string += self.get_formatted_float_list(item, aformat=aformat, inner=True)
        string += "]"
        if inner:
            string += ",\n"
        return string

    def print_setup(self):
        print("half_sensor_x:    {: 10.5f} mm".format(self.half_sensor_x))
        print("half_sensor_y:    {: 10.5f} mm".format(self.half_sensor_y))
        print("pixel_size_x:     {: 10.5f} mm".format(self.pixel_size_x))
        print("pixel_size_y:     {: 10.5f} mm".format(self.pixel_size_y))
        print("half_pixel_x:     {: 10.5f} mm".format(self.half_pixel_x))
        print("half_pixel_y:     {: 10.5f} mm".format(self.half_pixel_y))
        print("laser_rad:        {: 10.5f} rad or {: 10.5f} deg".format(self.laser_rad, np.rad2deg(self.laser_rad)))
        print("")

if __name__ == "__main__":
    TestPointGetter()