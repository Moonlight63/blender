/*
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 *
 * The Original Code is Copyright (C) 2014 Blender Foundation.
 * All rights reserved.
 */

/** \file
 * \ingroup bke
 */

#pragma once

#include "BKE_customdata.h"

#ifdef __cplusplus
extern "C" {
#endif

struct Depsgraph;
struct Object;
struct ReportList;
struct Scene;
struct SpaceTransform;

/* Warning, those def are stored in files (TransferData modifier), *DO NOT* modify those values. */
enum {
  DT_TYPE_MDEFORMVERT = 1 << 0,
  DT_TYPE_SHAPEKEY = 1 << 1,
  DT_TYPE_SKIN = 1 << 2,
  DT_TYPE_BWEIGHT_VERT = 1 << 3,

  DT_TYPE_SHARP_EDGE = 1 << 8,
  DT_TYPE_SEAM = 1 << 9,
  DT_TYPE_CREASE = 1 << 10,
  DT_TYPE_BWEIGHT_EDGE = 1 << 11,
  DT_TYPE_FREESTYLE_EDGE = 1 << 12,

  DT_TYPE_VCOL = 1 << 16,
  DT_TYPE_LNOR = 1 << 17,

  DT_TYPE_UV = 1 << 24,
  DT_TYPE_SHARP_FACE = 1 << 25,
  DT_TYPE_FREESTYLE_FACE = 1 << 26,
#define DT_TYPE_MAX 27

  DT_TYPE_VERT_ALL = DT_TYPE_MDEFORMVERT | DT_TYPE_SHAPEKEY | DT_TYPE_SKIN | DT_TYPE_BWEIGHT_VERT,
  DT_TYPE_EDGE_ALL = DT_TYPE_SHARP_EDGE | DT_TYPE_SEAM | DT_TYPE_CREASE | DT_TYPE_BWEIGHT_EDGE |
                     DT_TYPE_FREESTYLE_EDGE,
  DT_TYPE_LOOP_ALL = DT_TYPE_VCOL | DT_TYPE_LNOR | DT_TYPE_UV,
  DT_TYPE_POLY_ALL = DT_TYPE_UV | DT_TYPE_SHARP_FACE | DT_TYPE_FREESTYLE_FACE,
};

void BKE_object_data_transfer_dttypes_to_cdmask(const int dtdata_types,
                                                struct CustomData_MeshMasks *r_data_masks);
bool BKE_object_data_transfer_get_dttypes_capacity(const int dtdata_types,
                                                   bool *r_advanced_mixing,
                                                   bool *r_threshold);
int BKE_object_data_transfer_get_dttypes_item_types(const int dtdata_types);

int BKE_object_data_transfer_dttype_to_cdtype(const int dtdata_type);
int BKE_object_data_transfer_dttype_to_srcdst_index(const int dtdata_type);

#define DT_DATATYPE_IS_VERT(_dt) \
  ELEM(_dt, DT_TYPE_MDEFORMVERT, DT_TYPE_SHAPEKEY, DT_TYPE_SKIN, DT_TYPE_BWEIGHT_VERT)
#define DT_DATATYPE_IS_EDGE(_dt) \
  ELEM(_dt, \
       DT_TYPE_CREASE, \
       DT_TYPE_SHARP_EDGE, \
       DT_TYPE_SEAM, \
       DT_TYPE_BWEIGHT_EDGE, \
       DT_TYPE_FREESTYLE_EDGE)
#define DT_DATATYPE_IS_LOOP(_dt) ELEM(_dt, DT_TYPE_UV, DT_TYPE_VCOL, DT_TYPE_LNOR)
#define DT_DATATYPE_IS_POLY(_dt) ELEM(_dt, DT_TYPE_UV, DT_TYPE_SHARP_FACE, DT_TYPE_FREESTYLE_FACE)

#define DT_DATATYPE_IS_MULTILAYERS(_dt) \
  ELEM(_dt, DT_TYPE_MDEFORMVERT, DT_TYPE_SHAPEKEY, DT_TYPE_VCOL, DT_TYPE_UV)

enum {
  DT_MULTILAYER_INDEX_INVALID = -1,
  DT_MULTILAYER_INDEX_MDEFORMVERT = 0,
  DT_MULTILAYER_INDEX_SHAPEKEY = 1,
  DT_MULTILAYER_INDEX_VCOL = 2,
  DT_MULTILAYER_INDEX_UV = 3,
  DT_MULTILAYER_INDEX_MAX = 4,
};

/* Below we keep positive values for real layers idx (generated dynamically). */

/* How to select data layers, for types supporting multi-layers.
 * Here too, some options are highly dependent on type of transferred data! */
enum {
  DT_LAYERS_ACTIVE_SRC = -1,
  DT_LAYERS_ALL_SRC = -2,
  /* Datatype-specific. */
  DT_LAYERS_VGROUP_SRC = 1 << 8,
  DT_LAYERS_VGROUP_SRC_BONE_SELECT = -(DT_LAYERS_VGROUP_SRC | 1),
  DT_LAYERS_VGROUP_SRC_BONE_DEFORM = -(DT_LAYERS_VGROUP_SRC | 2),
  /* Other types-related modes... */
};

/* How to map a source layer to a destination layer, for types supporting multi-layers.
 * Note: if no matching layer can be found, it will be created. */
enum {
  DT_LAYERS_ACTIVE_DST = -1, /* Only for DT_LAYERS_FROMSEL_ACTIVE. */
  DT_LAYERS_NAME_DST = -2,
  DT_LAYERS_INDEX_DST = -3,
#if 0 /* TODO */
  DT_LAYERS_CREATE_DST = -4, /* Never replace existing data in dst, always create new layers. */
#endif
};

void BKE_object_data_transfer_layout(struct Depsgraph *depsgraph,
                                     struct Scene *scene,
                                     struct Object *ob_src,
                                     struct Object *ob_dst,
                                     const int data_types,
                                     const bool use_delete,
                                     const int fromlayers_select[DT_MULTILAYER_INDEX_MAX],
                                     const int tolayers_select[DT_MULTILAYER_INDEX_MAX]);

bool BKE_object_data_transfer_mesh(struct Depsgraph *depsgraph,
                                   struct Scene *scene,
                                   struct Object *ob_src,
                                   struct Object *ob_dst,
                                   const int data_types,
                                   const bool use_create,
                                   const int map_vert_mode,
                                   const int map_edge_mode,
                                   const int map_loop_mode,
                                   const int map_poly_mode,
                                   struct SpaceTransform *space_transform,
                                   const bool auto_transform,
                                   const float max_distance,
                                   const float ray_radius,
                                   const float islands_handling_precision,
                                   const int fromlayers_select[DT_MULTILAYER_INDEX_MAX],
                                   const int tolayers_select[DT_MULTILAYER_INDEX_MAX],
                                   const int mix_mode,
                                   const float mix_factor,
                                   const char *vgroup_name,
                                   const bool invert_vgroup,
                                   struct ReportList *reports);
bool BKE_object_data_transfer_ex(struct Depsgraph *depsgraph,
                                 struct Scene *scene,
                                 struct Object *ob_src,
                                 struct Object *ob_dst,
                                 struct Mesh *me_dst,
                                 const int data_types,
                                 bool use_create,
                                 const int map_vert_mode,
                                 const int map_edge_mode,
                                 const int map_loop_mode,
                                 const int map_poly_mode,
                                 struct SpaceTransform *space_transform,
                                 const bool auto_transform,
                                 const float max_distance,
                                 const float ray_radius,
                                 const float islands_handling_precision,
                                 const int fromlayers_select[DT_MULTILAYER_INDEX_MAX],
                                 const int tolayers_select[DT_MULTILAYER_INDEX_MAX],
                                 const int mix_mode,
                                 const float mix_factor,
                                 const char *vgroup_name,
                                 const bool invert_vgroup,
                                 struct ReportList *reports);

#ifdef __cplusplus
}
#endif
