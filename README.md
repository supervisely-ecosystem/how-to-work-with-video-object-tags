---
description: How to create, add, update and remove tags from Video and its annotation objects.
---

# **Tags on Video, its annotation objects and frames**

## **Introduction**

In this tutorial, you will learn how to create new tags for Video, its annotation objects or frames and assign them, update its values or remove at all using the Supervisely SDK.

Supervisely supports different types of tags:

- NONE
- ANY_NUMBER
- ANY_STRING
- ONEOF_STRING

And could be applied to:

- ALL
- IMAGES_ONLY
- OBJECTS_ONLY

You can find all the information about those types in the [Tags in Annotations](https://developer.supervise.ly/api-references/supervisely-annotation-json-format/tags) section and [SDK](https://supervisely.readthedocs.io/en/latest/sdk/supervisely.annotation.tag_meta.TagMeta.html) documentation.

You can learn more about working with Video using [Supervisely SDK](https://developer.supervise.ly/getting-started/python-sdk-tutorials/video) and what [Annotations for Video](https://developer.supervise.ly/api-references/supervisely-annotation-json-format/individual-video-annotations) are.

{% hint style="info" %}
Everything you need to reproduce [this tutorial is on GitHub](https://github.com/supervisely-ecosystem/how-to-work-with-video-object-tags): source code, Visual Studio Code configuration, and a shell script for creating virtual env.
{% endhint %}

## **How to debug this tutorial**

**Step 1.** Prepare `~/supervisely.env` file with credentials. [Learn more here.](../basics-of-authentication.md#use-.env-file-recommended)

**Step 2.** Clone [repository](https://github.com/supervisely-ecosystem/how-to-work-with-video-object-tags) with source code and create [Virtual Environment](https://docs.python.org/3/library/venv.html).

```bash
git clone https://github.com/supervisely-ecosystem/how-to-work-with-video-object-tags
cd how-to-work-with-video-object-tags
./create_venv.sh
```

**Step 3.** Open repository directory in Visual Studio Code.

```bash
code -r .
```

**Step 4.** Create dataset, for example, using this tutorial [Spatial labels on videos](https://developer.supervise.ly/getting-started/python-sdk-tutorials/spatial-labels-on-videos).

There you see project classes after project initialization

Project tags metadata after its initialization. This data is empty.

Visualization in Labeling Tool before we add tags

**Step 5.** Change Workspace ID in `local.env` file by copying the ID from the context menu of the workspace. Do the same for Project ID and Dataset ID .

```python
WORKSPACE_ID=82841  # ⬅️ change value
PROJECT_ID=240755  # ⬅️ change value
DATASET_ID=778169  # ⬅️ change value
```

<img  width="600" src="https://user-images.githubusercontent.com/57998637/231221251-3dfc1a56-b851-4542-be5b-d82b2ef14176.gif">

**Step 6.** Start debugging `src/main.py`

<img width="1280" src="https://user-images.githubusercontent.com/57998637/232045498-33bf1d2a-eb07-40c1-8319-9b2197e92c1a.gif">

## **Python Code**

### **Import libraries**

```python
import os
import supervisely as sly
from dotenv import load_dotenv
```

### **Init API client**

Init `api` for communicating with Supervisely Instance. First, we load environment variables with credentials, Project and Dataset IDs:

```python
load_dotenv("local.env")
load_dotenv(os.path.expanduser("~/supervisely.env"))
api = sly.Api.from_env()
```

With next lines we will get values from `local.env`.

```python
project_id = sly.env.project_id()
dataset_id = sly.env.dataset_id()
```

By using these IDs, we can retrieve the project metadata and annotations, and define the values needed for the following operations.

```python
video_ids = api.video.get_list(dataset_id)
project_meta_json = api.project.get_meta(project_id)
project_meta = sly.ProjectMeta.from_json(data=project_meta_json)
video_ann_json = api.video.annotation.download(video_ids[0].id)
```

### **Define function to work with metadata**

In this function described recreation of the source project metadata with new tag metadata. Right after updating the metadata, we need to obtain added metadata on the previous step to get the IDs in the next steps. If a tag with the `tag_name` already exists in the metadata, we could just use it if it fits our requirements. In case this tag doesn't meet our requirements, it would be better to create a new one with a different name. On the other hand, we could update the tag values.

```python
def refresh_meta(project_meta, new_tag_meta):
    if not project_meta.tag_metas.has_key(new_tag_meta.name):
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
        new_tag_meta = project_meta.tag_metas.get(new_tag_meta.name)
        if tag_values:
            if sorted(new_tag_meta.possible_values) != sorted(tag_values):
                sly.logger.warning(
                    f"Tag [{new_tag_meta.name}] already exists, but with another values: {new_tag_meta.possible_values}"
                )
    return new_tag_meta, project_meta
```

### **Create new tag metadata for video**

```python
video_tag_meta = sly.TagMeta(
    name="fruits",
    value_type=sly.TagValueType.ANY_NUMBER,
    applicable_to=sly.TagApplicableTo.ALL,
)
```

### **Create new tag for video and its frames**

When you pass information from tag metadata using its ID to the object, a new tag is created and appended.

If you want to add a tag with value, you can define the `value` argument with possible values.

If you want to add a tag to frames, you can define the `frame_range` argument.

```python
new_tag_meta, project_meta = refresh_meta(project_meta, video_tag_meta)

api.video.tag.add_tag(new_tag_meta.sly_id, video_ids[0].id, value=3)

tag_info = api.video.tag.add_tag(new_tag_meta.sly_id, video_ids[0].id, value=2, frame_range=[2, 6])
```

Visualization in Labeling Tool with new tags

### **Update tag value**

Also, if you need to correct tag values, you can easily do so as follows:

```python
api.video.tag.update_value(tag_id=tag_info["id"], tag_value=1)

api.video.tag.update_frame_range(tag_info["id"], [3, 5])
```

### **Delete tag**

To remove a tag, all you need is its ID.

```python
api.video.tag.remove_from_video(tag_info["id"])
```

Please note that you are only deleting the tag from the object. To remove a tag from the project (`TagMeta`), you need to use other SDK methods.

### **Create new tag metadatas for annotation objects in video**

```python
orange_object_tag_meta = sly.TagMeta(
    name="orange",
    value_type=sly.TagValueType.ONEOF_STRING,
    applicable_to=sly.TagApplicableTo.OBJECTS_ONLY,
    possible_values=["small", "big"],
)

kiwi_object_tag_meta = sly.TagMeta(
    name="kiwi",
    value_type=sly.TagValueType.ONEOF_STRING,
    applicable_to=sly.TagApplicableTo.OBJECTS_ONLY,
    possible_values=["medium", "small"],
)

orange_new_tag_meta, project_meta = refresh_meta(project_meta, orange_object_tag_meta)

kiwi_new_tag_meta, _ = refresh_meta(project_meta, kiwi_object_tag_meta)
```

### **Create new tag for annotation object and frames with this object**

When you pass information from tag metadata using its ID to the object, a new tag is created and appended.

If you want to add a tag with value, you can define the `value` argument with possible values.

If you want to add a tag to frames, you can define the `frame_range` argument.

```python
project_objects = video_ann_json.get("objects")
created_tag_ids = {}
for object in project_objects:
    if object["classTitle"] == "orange":
        tag_id = api.video.object.tag.add(
            orange_new_tag_meta.sly_id, object["id"], value="big", frame_range=[2, 6]
        )
        created_tag_ids[object["id"]] = tag_id
    elif object["classTitle"] == "kiwi":
        api.video.object.tag.add(kiwi_new_tag_meta.sly_id, object["id"], value="medium")

orange_ids = [object["id"] for object in project_objects if object["classTitle"] == "orange"]

```

Visualization in Labeling Tool with new tags

### **Update tag value and frame rates for annotation object**

Also, if you need to correct tag values, you can easily do so as follows:

```python
tag_id_to_operate = created_tag_ids.get(orange_ids[0])

api.video.object.tag.update_value(tag_id_to_operate, "small")

api.video.object.tag.update_frame_range(tag_id_to_operate, [3, 5])
```

### **Delete tag from annotation object**

The same as for the video all you need is its ID.

```python
api.video.object.tag.remove(tag_id_to_operate)
```
