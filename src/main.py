import os
import supervisely as sly
from dotenv import load_dotenv

load_dotenv("local.env")
load_dotenv(os.path.expanduser("~/supervisely.env"))
api = sly.Api.from_env()


project_id = sly.env.project_id()
dataset_id = sly.env.dataset_id()

vide_ids = api.video.get_list(dataset_id)

project_meta_json = api.project.get_meta(project_id)
project_meta = sly.ProjectMeta.from_json(data=project_meta_json)

key_id_map = sly.KeyIdMap()

video_ann_json = api.video.annotation.download(vide_ids[0].id)


def refresh_meta(project_meta, new_tag_meta, tag_name):
    if not project_meta.tag_metas.has_key(tag_name):
        new_tags_collection = project_meta.tag_metas.add(new_tag_meta)
        project_meta = sly.ProjectMeta(
            tag_metas=new_tags_collection, obj_classes=project_meta.obj_classes
        )
        api.project.update_meta(project_id, project_meta)
        new_prject_meta_json = api.project.get_meta(project_id)
        project_meta = sly.ProjectMeta.from_json(data=new_prject_meta_json)
        new_tag_meta = project_meta.tag_metas.get(new_tag_meta.name)
    else:
        tag_values = new_tag_meta.possible_values
        new_tag_meta = project_meta.tag_metas.get(tag_name)
        if tag_values:
            if sorted(new_tag_meta.possible_values) != sorted(tag_values):
                sly.logger.warning(
                    f"Tag [{new_tag_meta.name}] already exists, but with another values: {new_tag_meta.possible_values}"
                )
    return new_tag_meta, project_meta


########## video ##########

video_tag_meta = sly.TagMeta(
    name="fruits",
    value_type=sly.TagValueType.ANY_NUMBER,
    applicable_to=sly.TagApplicableTo.ALL,
)

new_tag_meta, project_meta = refresh_meta(project_meta, video_tag_meta, video_tag_meta.name)

api.video.tag.add_tag(new_tag_meta.sly_id, vide_ids[0].id, value=3)

tag_info = api.video.tag.add_tag(new_tag_meta.sly_id, vide_ids[0].id, value=2, frame_range=[2, 6])

api.video.tag.update_value(tag_id=tag_info["id"], tag_value=1)

api.video.tag.update_frame_range(tag_info["id"], [3, 5])

api.video.tag.remove_from_video(tag_info["id"])


########## annotated objects ########

object_tag_meta = sly.TagMeta(
    name="orange",
    value_type=sly.TagValueType.ONEOF_STRING,
    applicable_to=sly.TagApplicableTo.OBJECTS_ONLY,
    possible_values=["small", "big"],
)

new_tag_meta, _ = refresh_meta(project_meta, object_tag_meta, object_tag_meta.name)

project_objects = video_ann_json.get("objects")

created_tag_ids = {}
for object in project_objects:
    if object["classTitle"] == "orange":
        tag_id = api.video.object.tag.add(
            new_tag_meta.sly_id, object["id"], value="big", frame_range=[2, 6]
        )
        api.video.object.tag.add(new_tag_meta.sly_id, object["id"], value="small")
        created_tag_ids[object["id"]] = tag_id

orange_ids = [object["id"] for object in project_objects if object["classTitle"] == "orange"]

tag_id_to_operate = created_tag_ids.get(orange_ids[0])

api.video.object.tag.update_value(tag_id_to_operate, "small")

api.video.object.tag.update_frame_range(tag_id_to_operate, [3, 5])

api.video.object.tag.remove(tag_id_to_operate)
