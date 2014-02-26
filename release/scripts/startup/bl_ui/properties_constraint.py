# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>
import bpy
from bpy.types import Panel


class ConstraintButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "constraint"

    def draw_constraint(self, context, con):
        layout = self.layout

        box = layout.template_constraint(con)

        if box:
            # match enum type to our functions, avoids a lookup table.
            getattr(self, con.type)(context, box, con)
            
            if con.type not in {'RIGID_BODY_JOINT', 'NULL'} and not con.is_bepuik:
                box.prop(con, "influence")

    def space_template(self, layout, con, target=True, owner=True):
        if target or owner:

            split = layout.split(percentage=0.2)

            split.label(text="Space:")
            row = split.row()

            if target:
                row.prop(con, "target_space", text="")

            if target and owner:
                row.label(icon='ARROW_LEFTRIGHT')

            if owner:
                row.prop(con, "owner_space", text="")

    def target_template(self, layout, con, subtargets=True):
        layout.prop(con, "target")  # XXX limiting settings for only 'curves' or some type of object

        if con.target and subtargets:
            if con.target.type == 'ARMATURE':
                layout.prop_search(con, "subtarget", con.target.data, "bones", text="Bone")

                if hasattr(con, "head_tail"):
                    row = layout.row()
                    row.label(text="Head/Tail:")
                    row.prop(con, "head_tail", text="")
            elif con.target.type in {'MESH', 'LATTICE'}:
                layout.prop_search(con, "subtarget", con.target, "vertex_groups", text="Vertex Group")
    
    def bepuik_template_connection(self, layout, con):
        layout = layout.row(align=True)
        layout = layout.split(.5)
        target = con.connection_target
        
        layout.prop(con, "connection_target")  

        if target:
            if con.connection_target.type == 'ARMATURE':
                layout.prop_search(con, "connection_subtarget", target.data, "bones",text="")

            
                
    def bepuik_template_axis(self, layout, con, axis, subtargets=True):
        target_id = '%s_target' % axis
        subtarget_id = '%s_subtarget' % axis
        target = getattr(con,target_id)
        
        layout = layout.row(align=True)
        layout = layout.split(.5)
        
        layout.prop(con,target_id)
        
        if target and subtargets:
            if target.type == 'ARMATURE':
                layout = layout.split(.75)
                layout.prop_search(con, subtarget_id, target.data, "bones",text="")
                
                
            layout.prop(con, axis, text = "")
                    
    def bepuik_template_location(self, layout, con, location, subtargets=True):
        target_id = '%s_target' % location
        subtarget_id = '%s_subtarget' % location
        head_tail_id = '%s_head_tail' % location
        target = getattr(con,target_id)
        
        layout = layout.row(align = True)
        layout = layout.split(.5)
        layout.prop(con,target_id)
        
        if target and subtargets:
            if target.type == 'ARMATURE':
                layout = layout.split(.75)
                layout.prop_search(con, subtarget_id, target.data, "bones",text="")
                
                if getattr(con,subtarget_id):
                    layout.prop(con, head_tail_id, text="")
                                
    def ik_template(self, layout, con):
        # only used for iTaSC
        layout.prop(con, "pole_target")

        if con.pole_target and con.pole_target.type == 'ARMATURE':
            layout.prop_search(con, "pole_subtarget", con.pole_target.data, "bones", text="Bone")

        if con.pole_target:
            row = layout.row()
            row.label()
            row.prop(con, "pole_angle")

        split = layout.split(percentage=0.33)
        col = split.column()
        col.prop(con, "use_tail")
        col.prop(con, "use_stretch")

        col = split.column()
        col.prop(con, "chain_count")

    def CHILD_OF(self, context, layout, con):
        self.target_template(layout, con)

        split = layout.split()

        col = split.column()
        col.label(text="Location:")
        col.prop(con, "use_location_x", text="X")
        col.prop(con, "use_location_y", text="Y")
        col.prop(con, "use_location_z", text="Z")

        col = split.column()
        col.label(text="Rotation:")
        col.prop(con, "use_rotation_x", text="X")
        col.prop(con, "use_rotation_y", text="Y")
        col.prop(con, "use_rotation_z", text="Z")

        col = split.column()
        col.label(text="Scale:")
        col.prop(con, "use_scale_x", text="X")
        col.prop(con, "use_scale_y", text="Y")
        col.prop(con, "use_scale_z", text="Z")

        row = layout.row()
        row.operator("constraint.childof_set_inverse")
        row.operator("constraint.childof_clear_inverse")

    def TRACK_TO(self, context, layout, con):
        self.target_template(layout, con)

        row = layout.row()
        row.label(text="To:")
        row.prop(con, "track_axis", expand=True)

        row = layout.row()
        row.prop(con, "up_axis", text="Up")
        row.prop(con, "use_target_z")

        self.space_template(layout, con)

    def IK(self, context, layout, con):
        if context.object.pose.ik_solver == 'ITASC':
            layout.prop(con, "ik_type")
            getattr(self, 'IK_' + con.ik_type)(context, layout, con)
        else:
            # Standard IK constraint
            self.target_template(layout, con)
            layout.prop(con, "pole_target")

            if con.pole_target and con.pole_target.type == 'ARMATURE':
                layout.prop_search(con, "pole_subtarget", con.pole_target.data, "bones", text="Bone")

            if con.pole_target:
                row = layout.row()
                row.prop(con, "pole_angle")
                row.label()

            split = layout.split()
            col = split.column()
            col.prop(con, "iterations")
            col.prop(con, "chain_count")

            col = split.column()
            col.prop(con, "use_tail")
            col.prop(con, "use_stretch")

            layout.label(text="Weight:")

            split = layout.split()
            col = split.column()
            row = col.row(align=True)
            row.prop(con, "use_location", text="")
            sub = row.row(align=True)
            sub.active = con.use_location
            sub.prop(con, "weight", text="Position", slider=True)

            col = split.column()
            row = col.row(align=True)
            row.prop(con, "use_rotation", text="")
            sub = row.row(align=True)
            sub.active = con.use_rotation
            sub.prop(con, "orient_weight", text="Rotation", slider=True)

    def IK_COPY_POSE(self, context, layout, con):
        self.target_template(layout, con)
        self.ik_template(layout, con)

        row = layout.row()
        row.label(text="Axis Ref:")
        row.prop(con, "reference_axis", expand=True)
        split = layout.split(percentage=0.33)
        split.row().prop(con, "use_location")
        row = split.row()
        row.prop(con, "weight", text="Weight", slider=True)
        row.active = con.use_location
        split = layout.split(percentage=0.33)
        row = split.row()
        row.label(text="Lock:")
        row = split.row()
        row.prop(con, "lock_location_x", text="X")
        row.prop(con, "lock_location_y", text="Y")
        row.prop(con, "lock_location_z", text="Z")
        split.active = con.use_location

        split = layout.split(percentage=0.33)
        split.row().prop(con, "use_rotation")
        row = split.row()
        row.prop(con, "orient_weight", text="Weight", slider=True)
        row.active = con.use_rotation
        split = layout.split(percentage=0.33)
        row = split.row()
        row.label(text="Lock:")
        row = split.row()
        row.prop(con, "lock_rotation_x", text="X")
        row.prop(con, "lock_rotation_y", text="Y")
        row.prop(con, "lock_rotation_z", text="Z")
        split.active = con.use_rotation

    def IK_DISTANCE(self, context, layout, con):
        self.target_template(layout, con)
        self.ik_template(layout, con)

        layout.prop(con, "limit_mode")

        row = layout.row()
        row.prop(con, "weight", text="Weight", slider=True)
        row.prop(con, "distance", text="Distance", slider=True)

    def FOLLOW_PATH(self, context, layout, con):
        self.target_template(layout, con)
        layout.operator("constraint.followpath_path_animate", text="Animate Path", icon='ANIM_DATA')

        split = layout.split()

        col = split.column()
        col.prop(con, "use_curve_follow")
        col.prop(con, "use_curve_radius")

        col = split.column()
        col.prop(con, "use_fixed_location")
        if con.use_fixed_location:
            col.prop(con, "offset_factor", text="Offset")
        else:
            col.prop(con, "offset")

        row = layout.row()
        row.label(text="Forward:")
        row.prop(con, "forward_axis", expand=True)

        row = layout.row()
        row.prop(con, "up_axis", text="Up")
        row.label()

    def LIMIT_ROTATION(self, context, layout, con):
        split = layout.split()

        col = split.column(align=True)
        col.prop(con, "use_limit_x")
        sub = col.column(align=True)
        sub.active = con.use_limit_x
        sub.prop(con, "min_x", text="Min")
        sub.prop(con, "max_x", text="Max")

        col = split.column(align=True)
        col.prop(con, "use_limit_y")
        sub = col.column(align=True)
        sub.active = con.use_limit_y
        sub.prop(con, "min_y", text="Min")
        sub.prop(con, "max_y", text="Max")

        col = split.column(align=True)
        col.prop(con, "use_limit_z")
        sub = col.column(align=True)
        sub.active = con.use_limit_z
        sub.prop(con, "min_z", text="Min")
        sub.prop(con, "max_z", text="Max")

        layout.prop(con, "use_transform_limit")

        row = layout.row()
        row.label(text="Convert:")
        row.prop(con, "owner_space", text="")

    def LIMIT_LOCATION(self, context, layout, con):
        split = layout.split()

        col = split.column()
        col.prop(con, "use_min_x")
        sub = col.column()
        sub.active = con.use_min_x
        sub.prop(con, "min_x", text="")
        col.prop(con, "use_max_x")
        sub = col.column()
        sub.active = con.use_max_x
        sub.prop(con, "max_x", text="")

        col = split.column()
        col.prop(con, "use_min_y")
        sub = col.column()
        sub.active = con.use_min_y
        sub.prop(con, "min_y", text="")
        col.prop(con, "use_max_y")
        sub = col.column()
        sub.active = con.use_max_y
        sub.prop(con, "max_y", text="")

        col = split.column()
        col.prop(con, "use_min_z")
        sub = col.column()
        sub.active = con.use_min_z
        sub.prop(con, "min_z", text="")
        col.prop(con, "use_max_z")
        sub = col.column()
        sub.active = con.use_max_z
        sub.prop(con, "max_z", text="")

        row = layout.row()
        row.prop(con, "use_transform_limit")
        row.label()

        row = layout.row()
        row.label(text="Convert:")
        row.prop(con, "owner_space", text="")

    def LIMIT_SCALE(self, context, layout, con):
        split = layout.split()

        col = split.column()
        col.prop(con, "use_min_x")
        sub = col.column()
        sub.active = con.use_min_x
        sub.prop(con, "min_x", text="")
        col.prop(con, "use_max_x")
        sub = col.column()
        sub.active = con.use_max_x
        sub.prop(con, "max_x", text="")

        col = split.column()
        col.prop(con, "use_min_y")
        sub = col.column()
        sub.active = con.use_min_y
        sub.prop(con, "min_y", text="")
        col.prop(con, "use_max_y")
        sub = col.column()
        sub.active = con.use_max_y
        sub.prop(con, "max_y", text="")

        col = split.column()
        col.prop(con, "use_min_z")
        sub = col.column()
        sub.active = con.use_min_z
        sub.prop(con, "min_z", text="")
        col.prop(con, "use_max_z")
        sub = col.column()
        sub.active = con.use_max_z
        sub.prop(con, "max_z", text="")

        row = layout.row()
        row.prop(con, "use_transform_limit")
        row.label()

        row = layout.row()
        row.label(text="Convert:")
        row.prop(con, "owner_space", text="")

    def COPY_ROTATION(self, context, layout, con):
        self.target_template(layout, con)

        split = layout.split()

        col = split.column()
        col.prop(con, "use_x", text="X")
        sub = col.column()
        sub.active = con.use_x
        sub.prop(con, "invert_x", text="Invert")

        col = split.column()
        col.prop(con, "use_y", text="Y")
        sub = col.column()
        sub.active = con.use_y
        sub.prop(con, "invert_y", text="Invert")

        col = split.column()
        col.prop(con, "use_z", text="Z")
        sub = col.column()
        sub.active = con.use_z
        sub.prop(con, "invert_z", text="Invert")

        layout.prop(con, "use_offset")

        self.space_template(layout, con)

    def COPY_LOCATION(self, context, layout, con):
        self.target_template(layout, con)

        split = layout.split()

        col = split.column()
        col.prop(con, "use_x", text="X")
        sub = col.column()
        sub.active = con.use_x
        sub.prop(con, "invert_x", text="Invert")

        col = split.column()
        col.prop(con, "use_y", text="Y")
        sub = col.column()
        sub.active = con.use_y
        sub.prop(con, "invert_y", text="Invert")

        col = split.column()
        col.prop(con, "use_z", text="Z")
        sub = col.column()
        sub.active = con.use_z
        sub.prop(con, "invert_z", text="Invert")

        layout.prop(con, "use_offset")

        self.space_template(layout, con)

    def COPY_SCALE(self, context, layout, con):
        self.target_template(layout, con)

        row = layout.row(align=True)
        row.prop(con, "use_x", text="X")
        row.prop(con, "use_y", text="Y")
        row.prop(con, "use_z", text="Z")

        layout.prop(con, "use_offset")

        self.space_template(layout, con)

    def MAINTAIN_VOLUME(self, context, layout, con):

        row = layout.row()
        row.label(text="Free:")
        row.prop(con, "free_axis", expand=True)

        layout.prop(con, "volume")

        row = layout.row()
        row.label(text="Convert:")
        row.prop(con, "owner_space", text="")

    def COPY_TRANSFORMS(self, context, layout, con):
        self.target_template(layout, con)

        self.space_template(layout, con)

    #def SCRIPT(self, context, layout, con):

    def ACTION(self, context, layout, con):
        self.target_template(layout, con)

        split = layout.split()

        col = split.column()
        col.label(text="From Target:")
        col.prop(con, "transform_channel", text="")
        col.prop(con, "target_space", text="")

        col = split.column()
        col.label(text="To Action:")
        col.prop(con, "action", text="")
        col.prop(con, "use_bone_object_action")

        split = layout.split()

        col = split.column(align=True)
        col.label(text="Target Range:")
        col.prop(con, "min", text="Min")
        col.prop(con, "max", text="Max")

        col = split.column(align=True)
        col.label(text="Action Range:")
        col.prop(con, "frame_start", text="Start")
        col.prop(con, "frame_end", text="End")

    def LOCKED_TRACK(self, context, layout, con):
        self.target_template(layout, con)

        row = layout.row()
        row.label(text="To:")
        row.prop(con, "track_axis", expand=True)

        row = layout.row()
        row.label(text="Lock:")
        row.prop(con, "lock_axis", expand=True)

    def LIMIT_DISTANCE(self, context, layout, con):
        self.target_template(layout, con)

        col = layout.column(align=True)
        col.prop(con, "distance")
        col.operator("constraint.limitdistance_reset")

        row = layout.row()
        row.label(text="Clamp Region:")
        row.prop(con, "limit_mode", text="")

        row = layout.row()
        row.prop(con, "use_transform_limit")
        row.label()

        self.space_template(layout, con)

    def STRETCH_TO(self, context, layout, con):
        self.target_template(layout, con)

        row = layout.row()
        row.prop(con, "rest_length", text="Rest Length")
        row.operator("constraint.stretchto_reset", text="Reset")

        layout.prop(con, "bulge", text="Volume Variation")

        row = layout.row()
        row.label(text="Volume:")
        row.prop(con, "volume", expand=True)

        row.label(text="Plane:")
        row.prop(con, "keep_axis", expand=True)

    def FLOOR(self, context, layout, con):
        self.target_template(layout, con)

        row = layout.row()
        row.prop(con, "use_sticky")
        row.prop(con, "use_rotation")

        layout.prop(con, "offset")

        row = layout.row()
        row.label(text="Min/Max:")
        row.prop(con, "floor_location", expand=True)

        self.space_template(layout, con)

    def RIGID_BODY_JOINT(self, context, layout, con):
        self.target_template(layout, con, subtargets=False)

        layout.prop(con, "pivot_type")
        layout.prop(con, "child")

        row = layout.row()
        row.prop(con, "use_linked_collision", text="Linked Collision")
        row.prop(con, "show_pivot", text="Display Pivot")

        split = layout.split()

        col = split.column(align=True)
        col.label(text="Pivot:")
        col.prop(con, "pivot_x", text="X")
        col.prop(con, "pivot_y", text="Y")
        col.prop(con, "pivot_z", text="Z")

        col = split.column(align=True)
        col.label(text="Axis:")
        col.prop(con, "axis_x", text="X")
        col.prop(con, "axis_y", text="Y")
        col.prop(con, "axis_z", text="Z")

        if con.pivot_type == 'CONE_TWIST':
            layout.label(text="Limits:")
            split = layout.split()

            col = split.column()
            col.prop(con, "use_angular_limit_x", text="Angle X")
            sub = col.column()
            sub.active = con.use_angular_limit_x
            sub.prop(con, "limit_angle_max_x", text="")

            col = split.column()
            col.prop(con, "use_angular_limit_y", text="Angle Y")
            sub = col.column()
            sub.active = con.use_angular_limit_y
            sub.prop(con, "limit_angle_max_y", text="")

            col = split.column()
            col.prop(con, "use_angular_limit_z", text="Angle Z")
            sub = col.column()
            sub.active = con.use_angular_limit_z
            sub.prop(con, "limit_angle_max_z", text="")

        elif con.pivot_type == 'GENERIC_6_DOF':
            layout.label(text="Limits:")
            split = layout.split()

            col = split.column(align=True)
            col.prop(con, "use_limit_x", text="X")
            sub = col.column(align=True)
            sub.active = con.use_limit_x
            sub.prop(con, "limit_min_x", text="Min")
            sub.prop(con, "limit_max_x", text="Max")

            col = split.column(align=True)
            col.prop(con, "use_limit_y", text="Y")
            sub = col.column(align=True)
            sub.active = con.use_limit_y
            sub.prop(con, "limit_min_y", text="Min")
            sub.prop(con, "limit_max_y", text="Max")

            col = split.column(align=True)
            col.prop(con, "use_limit_z", text="Z")
            sub = col.column(align=True)
            sub.active = con.use_limit_z
            sub.prop(con, "limit_min_z", text="Min")
            sub.prop(con, "limit_max_z", text="Max")

            split = layout.split()

            col = split.column(align=True)
            col.prop(con, "use_angular_limit_x", text="Angle X")
            sub = col.column(align=True)
            sub.active = con.use_angular_limit_x
            sub.prop(con, "limit_angle_min_x", text="Min")
            sub.prop(con, "limit_angle_max_x", text="Max")

            col = split.column(align=True)
            col.prop(con, "use_angular_limit_y", text="Angle Y")
            sub = col.column(align=True)
            sub.active = con.use_angular_limit_y
            sub.prop(con, "limit_angle_min_y", text="Min")
            sub.prop(con, "limit_angle_max_y", text="Max")

            col = split.column(align=True)
            col.prop(con, "use_angular_limit_z", text="Angle Z")
            sub = col.column(align=True)
            sub.active = con.use_angular_limit_z
            sub.prop(con, "limit_angle_min_z", text="Min")
            sub.prop(con, "limit_angle_max_z", text="Max")

        elif con.pivot_type == 'HINGE':
            layout.label(text="Limits:")
            split = layout.split()

            row = split.row(align=True)
            col = row.column()
            col.prop(con, "use_angular_limit_x", text="Angle X")

            col = row.column()
            col.active = con.use_angular_limit_x
            col.prop(con, "limit_angle_min_x", text="Min")
            col = row.column()
            col.active = con.use_angular_limit_x
            col.prop(con, "limit_angle_max_x", text="Max")

    def CLAMP_TO(self, context, layout, con):
        self.target_template(layout, con)

        row = layout.row()
        row.label(text="Main Axis:")
        row.prop(con, "main_axis", expand=True)

        layout.prop(con, "use_cyclic")

    def TRANSFORM(self, context, layout, con):
        self.target_template(layout, con)

        layout.prop(con, "use_motion_extrapolate", text="Extrapolate")

        col = layout.column()
        col.row().label(text="Source:")
        col.row().prop(con, "map_from", expand=True)

        split = layout.split()

        sub = split.column(align=True)
        sub.label(text="X:")
        sub.prop(con, "from_min_x", text="Min")
        sub.prop(con, "from_max_x", text="Max")

        sub = split.column(align=True)
        sub.label(text="Y:")
        sub.prop(con, "from_min_y", text="Min")
        sub.prop(con, "from_max_y", text="Max")

        sub = split.column(align=True)
        sub.label(text="Z:")
        sub.prop(con, "from_min_z", text="Min")
        sub.prop(con, "from_max_z", text="Max")

        col = layout.column()
        row = col.row()
        row.label(text="Source to Destination Mapping:")

        # note: chr(187) is the ASCII arrow ( >> ). Blender Text Editor can't
        # open it. Thus we are using the hard-coded value instead.
        row = col.row()
        row.prop(con, "map_to_x_from", expand=False, text="")
        row.label(text=" %s    X" % chr(187))

        row = col.row()
        row.prop(con, "map_to_y_from", expand=False, text="")
        row.label(text=" %s    Y" % chr(187))

        row = col.row()
        row.prop(con, "map_to_z_from", expand=False, text="")
        row.label(text=" %s    Z" % chr(187))

        split = layout.split()

        col = split.column()
        col.label(text="Destination:")
        col.row().prop(con, "map_to", expand=True)

        split = layout.split()

        col = split.column()
        col.label(text="X:")

        sub = col.column(align=True)
        sub.prop(con, "to_min_x", text="Min")
        sub.prop(con, "to_max_x", text="Max")

        col = split.column()
        col.label(text="Y:")

        sub = col.column(align=True)
        sub.prop(con, "to_min_y", text="Min")
        sub.prop(con, "to_max_y", text="Max")

        col = split.column()
        col.label(text="Z:")

        sub = col.column(align=True)
        sub.prop(con, "to_min_z", text="Min")
        sub.prop(con, "to_max_z", text="Max")

        self.space_template(layout, con)

    def SHRINKWRAP(self, context, layout, con):
        self.target_template(layout, con, False)

        layout.prop(con, "distance")
        layout.prop(con, "shrinkwrap_type")

        if con.shrinkwrap_type == 'PROJECT':
            row = layout.row(align=True)
            row.prop(con, "project_axis", expand=True)
            split = layout.split(percentage=0.4)
            split.label(text="Axis Space:")
            rowsub = split.row()
            rowsub.prop(con, "project_axis_space", text="")
            layout.prop(con, "project_limit")

    def DAMPED_TRACK(self, context, layout, con):
        self.target_template(layout, con)

        row = layout.row()
        row.label(text="To:")
        row.prop(con, "track_axis", expand=True)

    def SPLINE_IK(self, context, layout, con):
        self.target_template(layout, con)

        col = layout.column()
        col.label(text="Spline Fitting:")
        col.prop(con, "chain_count")
        col.prop(con, "use_even_divisions")
        col.prop(con, "use_chain_offset")

        col = layout.column()
        col.label(text="Chain Scaling:")
        col.prop(con, "use_y_stretch")
        col.prop(con, "xz_scale_mode")
        col.prop(con, "use_curve_radius")

    def PIVOT(self, context, layout, con):
        self.target_template(layout, con)

        if con.target:
            col = layout.column()
            col.prop(con, "offset", text="Pivot Offset")
        else:
            col = layout.column()
            col.prop(con, "use_relative_location")
            if con.use_relative_location:
                col.prop(con, "offset", text="Relative Pivot Point")
            else:
                col.prop(con, "offset", text="Absolute Pivot Point")

        col = layout.column()
        col.prop(con, "rotation_range", text="Pivot When")

    @staticmethod
    def _getConstraintClip(context, con):
        if not con.use_active_clip:
            return con.clip
        else:
            return context.scene.active_clip

    def FOLLOW_TRACK(self, context, layout, con):
        clip = self._getConstraintClip(context, con)

        row = layout.row()
        row.prop(con, "use_active_clip")
        row.prop(con, "use_3d_position")

        col = layout.column()

        if not con.use_active_clip:
            col.prop(con, "clip")

        row = col.row()
        row.prop(con, "frame_method", expand=True)

        if clip:
            tracking = clip.tracking

            col.prop_search(con, "object", tracking, "objects", icon='OBJECT_DATA')

            tracking_object = tracking.objects.get(con.object, tracking.objects[0])

            col.prop_search(con, "track", tracking_object, "tracks", icon='ANIM_DATA')

        col.prop(con, "camera")

        row = col.row()
        row.active = not con.use_3d_position
        row.prop(con, "depth_object")

        layout.operator("clip.constraint_to_fcurve")

    def CAMERA_SOLVER(self, context, layout, con):
        layout.prop(con, "use_active_clip")

        if not con.use_active_clip:
            layout.prop(con, "clip")

        layout.operator("clip.constraint_to_fcurve")

    def OBJECT_SOLVER(self, context, layout, con):
        clip = self._getConstraintClip(context, con)

        layout.prop(con, "use_active_clip")

        if not con.use_active_clip:
            layout.prop(con, "clip")

        if clip:
            layout.prop_search(con, "object", clip.tracking, "objects", icon='OBJECT_DATA')

        layout.prop(con, "camera")

        row = layout.row()
        row.operator("constraint.objectsolver_set_inverse")
        row.operator("constraint.objectsolver_clear_inverse")

        layout.operator("clip.constraint_to_fcurve")
    
    def connection_a_label(self,layout):
        ob = bpy.context.object
        obname = ""
        pchanname = ""
        if ob:
            if hasattr(ob,"name"):
                obname = ob.name
                
        if bpy.context.active_pose_bone:
            pchanname = bpy.context.active_pose_bone.name
        
        layout.label("Target A:  %s : %s" % (obname,pchanname))
         
    def BEPUIK_ANGULAR_JOINT(self, context, layout, con):
        self.bepuik_template_connection(layout, con)
        layout.prop(con,'bepuik_rigidity')
        
    def BEPUIK_BALL_SOCKET_JOINT(self,context,layout,con):
        self.connection_a_label(layout)
        self.bepuik_template_location(layout, con, "anchor")
        self.bepuik_template_connection(layout, con)
        layout.prop(con,'bepuik_rigidity')
        
    def BEPUIK_DISTANCE_JOINT(self,context,layout,con):
        col = layout.column(align=True)
        self.connection_a_label(col)
        self.bepuik_template_location(col, con, "anchor_a")
        layout.separator();col = layout.column(align=True)
        self.bepuik_template_connection(col, con)
        self.bepuik_template_location(col, con, "anchor_b")
        layout.prop(con,'bepuik_rigidity')
        
    def BEPUIK_DISTANCE_LIMIT(self,context,layout,con):
        col = layout.column(align=True)
        self.connection_a_label(col)
        self.bepuik_template_location(col, con, "anchor_a")
        layout.separator();col = layout.column(align=True)
        self.bepuik_template_connection(col, con)
        self.bepuik_template_location(col, con, "anchor_b")
        layout.prop(con,"min_distance")
        layout.prop(con,"max_distance")
        layout.prop(con,'bepuik_rigidity')

    def BEPUIK_LINEAR_AXIS_LIMIT(self,context,layout,con):
        col = layout.column(align=True)
        self.connection_a_label(col)
        self.bepuik_template_location(col, con, "line_anchor")
        self.bepuik_template_axis(col, con, "line_direction")
        layout.separator();col = layout.column(align=True)
        self.bepuik_template_connection(col, con)
        self.bepuik_template_location(col, con, "anchor_b")
        layout.prop(con,"min_distance")
        layout.prop(con,"max_distance")
        layout.prop(con,'bepuik_rigidity')
    
    def BEPUIK_POINT_ON_LINE_JOINT(self,context,layout,con):
        col = layout.column(align=True)
        self.connection_a_label(col)
        self.bepuik_template_location(col, con, "line_anchor")
        self.bepuik_template_axis(col, con, "line_direction")
        layout.separator();col = layout.column(align=True)
        self.bepuik_template_connection(col, con)
        self.bepuik_template_location(col, con, "anchor_b")
        layout.prop(con,'bepuik_rigidity')
        
    def BEPUIK_POINT_ON_PLANE_JOINT(self,context,layout,con):
        col = layout.column(align=True)
        self.connection_a_label(col)
        self.bepuik_template_location(col, con, "plane_anchor")
        self.bepuik_template_axis(col, con, "plane_normal")
        layout.separator();col = layout.column(align=True)
        self.bepuik_template_connection(col, con)
        self.bepuik_template_location(col, con, "anchor_b")
        layout.prop(con,'bepuik_rigidity')

    def BEPUIK_REVOLUTE_JOINT(self,context,layout,con):
        self.connection_a_label(layout)
        self.bepuik_template_connection(layout, con)
        self.bepuik_template_axis(layout, con, "free_axis")
        layout.prop(con,'bepuik_rigidity')

    def BEPUIK_SWING_LIMIT(self,context,layout,con):
        col = layout.column(align=True)
        self.connection_a_label(col)
        self.bepuik_template_axis(col, con, "axis_a")
        layout.separator();col = layout.column(align=True)
        self.bepuik_template_connection(col, con)
        self.bepuik_template_axis(col, con, "axis_b")
        layout.prop(con,"max_swing")
        layout.prop(con,'bepuik_rigidity')
        
    def BEPUIK_SWIVEL_HINGE_JOINT(self,context,layout,con):
        col = layout.column(align=True)
        self.connection_a_label(col)
        self.bepuik_template_axis(col, con, "hinge_axis")
        layout.separator();col = layout.column(align=True)
        self.bepuik_template_connection(con, con)
        self.bepuik_template_axis(con, con, "twist_axis")        
        layout.prop(con,'bepuik_rigidity')
        
    def BEPUIK_TWIST_JOINT(self,context,layout,con):
        col = layout.column(align=True)
        self.connection_a_label(col)
        self.bepuik_template_axis(col, con, "axis_a")
        layout.separator();col = layout.column(align=True)
        self.bepuik_template_connection(col, con)
        self.bepuik_template_axis(col, con, "axis_b")
        layout.prop(con,'bepuik_rigidity')
        
    def BEPUIK_TWIST_LIMIT(self,context,layout,con):
        col = layout.column(align=True)
        self.connection_a_label(col)
        self.bepuik_template_axis(col, con, "axis_a")
        self.bepuik_template_axis(col, con, "measurement_axis_a")
        layout.separator();col = layout.column(align=True)
        self.bepuik_template_connection(col, con)
        self.bepuik_template_axis(col, con, "axis_b")
        self.bepuik_template_axis(col, con, "measurement_axis_b")
        layout.separator();col = layout.column(align=True)
        layout.prop(con,"max_twist")
        layout.prop(con,'bepuik_rigidity')
        
        
    def BEPUIK_CONTROL(self,context,layout,con):
        self.bepuik_template_connection(layout,con)
        layout.prop(con,"use_hard_rigidity")
        layout.prop(con,"bepuik_rigidity",text="Position Rigidity")
        layout.prop(con,"orientation_rigidity")
        layout.prop(con,"pulled_point")


        
    def SCRIPT(self, context, layout, con):
        layout.label("Blender 2.6 doesn't support python constraints yet")


class OBJECT_PT_constraints(ConstraintButtonsPanel, Panel):
    bl_label = "Object Constraints"
    bl_context = "constraint"
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        return (context.object)

    def draw(self, context):
        layout = self.layout

        obj = context.object

        if obj.type == 'ARMATURE' and obj.mode in {'EDIT', 'POSE'}:
            box = layout.box()
            box.alert = True
            box.label(icon='INFO', text="See Bone Constraints tab to Add Constraints to active bone")
        else:
            layout.operator_menu_enum("object.constraint_add", "type", text="Add Object Constraint")

        for con in obj.constraints:
            self.draw_constraint(context, con)


class BONE_PT_constraints(ConstraintButtonsPanel, Panel):
    bl_label = "Bone Constraints"
    bl_context = "bone_constraint"
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        return (context.pose_bone)

    def draw(self, context):
        layout = self.layout

        layout.operator_menu_enum("pose.constraint_add", "type", text="Add Bone Constraint")

        for con in context.pose_bone.constraints:
            self.draw_constraint(context, con)

if __name__ == "__main__":  # only for live edit.
    bpy.utils.register_module(__name__)
