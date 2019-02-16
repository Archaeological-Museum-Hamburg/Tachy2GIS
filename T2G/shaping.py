import shapefile

SHAPEFILE_NAME = 'elstorf_plane_01_3_perlin_z_3D'
QUAD_POINTS = [(552336.8718728457, 5921146.249944764), (552338.4739378484, 5921146.909618589), (552339.5524521966, 5921144.920126102), (552337.0812931075, 5921144.145271134), (552336.8718728457, 5921146.249944764)]
QUAD_ZS = [1.312, 1.2856, 1.3221, 1.28955, 1.384]


def copy_shapefile(file_name):
    with shapefile.Reader(file_name) as reader:
        fields = reader.fields
        shapes = reader.shapes()
        records = reader.records()

    with shapefile.Writer(file_name + '_copy') as writer:
        writer.fields = fields
        for shape, record in zip(shapes, records):
            writer.shape(shape)
            writer.record(*record)


def add_shape(file_name, parts, field_data):
    with shapefile.Reader(file_name) as reader:
        fields = reader.fields
        shapes = reader.shapes()
        records = reader.records()
        shape_type = reader.shapeType
        shape_type_name = reader.shapeTypeName

    with shapefile.Writer(file_name) as writer:
        writer.fields = fields
        for shape, record in zip(shapes, records):
            writer.shape(shape)
            writer.record(*record)
        if shape_type == shapefile.POINT:
            writer.point(*parts[0])
        if shape_type == shapefile.POINTZ:
            writer.pointz(*parts[0])
        if shape_type == shapefile.POLYLINE:
            writer.line(parts)
        if shape_type == shapefile.POLYLINEZ:
            writer.linez(parts)
        if shape_type == shapefile.POLYGON:
            parts[0].append(parts[0][0])
            writer.poly(parts)
        if shape_type == shapefile.POLYGONZ:
            parts[0].append(parts[0][0])
            writer.polyz(parts)
        else:
            raise ValueError('Incompatible shape type: ' + shape_type_name)
        writer.record(*field_data)


if __name__=='__main__':
    parts = [[[point[0], point[1], z] for point, z in zip(QUAD_POINTS, QUAD_ZS)]]
    records = [1]
    add_shape(SHAPEFILE_NAME, parts, records)

