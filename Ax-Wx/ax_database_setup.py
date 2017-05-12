# https://gis.stackexchange.com/questions/78838/how-to-convert-projected-coordinates-to-lat-lon-using-python

# x1,y1 = 1035231,360514
# x1,y1 = 1178104,857169.8
x1,y1 = 1191640.8, 669384.0

from pyproj import Proj, transform

def convert_stateplane_to_latlon(state_x, state_y, proj_in=2286, proj_out=4326):
    inProj = Proj(init='epsg:' + str(proj_in), preserve_units=True)
    outProj = Proj(init='epsg:' + str(proj_out))
    x2,y2 = transform(inProj,outProj,state_x,state_y)
    return(y2,x2)

print(convert_stateplane_to_latlon(x1,y1))
