from OCP.STEPCAFControl import STEPCAFControl_Reader

from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString

from OCP.XCAFApp import XCAFApp_Application
from OCP.XCAFDoc import XCAFDoc_DocumentTool

from OCP.TDF import TDF_LabelSequence

from OCP.TopLoc import TopLoc_Location

import numpy as np



def location_to_matrix(location):

    trsf = location.Transformation()

    t = trsf.TranslationPart()


    return np.array(
        [
            [
                trsf.Value(1,1),
                trsf.Value(1,2),
                trsf.Value(1,3),
                t.X()
            ],

            [
                trsf.Value(2,1),
                trsf.Value(2,2),
                trsf.Value(2,3),
                t.Y()
            ],

            [
                trsf.Value(3,1),
                trsf.Value(3,2),
                trsf.Value(3,3),
                t.Z()
            ],

            [
                0,
                0,
                0,
                1
            ]
        ]
    )



def get_name(label):

    try:
        return label.GetLabelName()

    except:
        return "unknown"



def traverse(
        shape_tool,
        label,
        parent_matrix,
        parts
):


    local_location = (
        shape_tool.GetLocation_s(label)
    )


    local_matrix = (
        location_to_matrix(
            local_location
        )
    )


    global_matrix = (
        parent_matrix @ local_matrix
    )


    # Prüfen ob echtes Bauteil

    shape = shape_tool.GetShape_s(label)


    children = TDF_LabelSequence()


    has_children = shape_tool.GetComponents_s(
        label,
        children
    )


    # Nur echte Bauteile speichern
    # Baugruppen überspringen

    if (
        not has_children
        and not shape.IsNull()
    ):

        parts.append(
            {
                "name": get_name(label),

                "shape": shape,

                "location": global_matrix
            }
        )

    # Unterteile suchen

    for i in range(
        1,
        children.Length()+1
    ):

        traverse(
            shape_tool,
            children.Value(i),
            global_matrix,
            parts
        )



def load_step_assembly(filename):


    app = (
        XCAFApp_Application
        .GetApplication_s()
    )


    doc = TDocStd_Document(
        TCollection_ExtendedString(
            "STEP"
        )
    )


    reader = STEPCAFControl_Reader()

    reader.SetNameMode(True)


    status = reader.ReadFile(
        filename
    )


    if not status:
        raise Exception(
            "STEP konnte nicht geladen werden"
        )


    reader.Transfer(doc)


    shape_tool = (
        XCAFDoc_DocumentTool
        .ShapeTool_s(
            doc.Main()
        )
    )


    roots = TDF_LabelSequence()


    shape_tool.GetFreeShapes(
        roots
    )


    parts=[]


    identity=np.eye(4)


    for i in range(
        1,
        roots.Length()+1
    ):


        traverse(
            shape_tool,
            roots.Value(i),
            identity,
            parts
        )


    return parts