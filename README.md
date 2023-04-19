---
description: How to create, add, update and remove tags from Video and annotation objects, even for frames.
---

# **Tags on Video, its annotation objects and frames**

## **Introduction**

In this tutorial, you will learn how to create new tags and assign them, update its values or remove tags for selected annotation objects or frames (with these objects) in Video using the Supervisely SDK.

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

**Step 4.** Create, for example, dataset with this tutorial [Spatial labels on videos](https://developer.supervise.ly/getting-started/python-sdk-tutorials/spatial-labels-on-videos).

<img width="1280" src="https://user-images.githubusercontent.com/57998637/231194451-e8797293-0317-4168-a165-7bd59d5b72f3.gif">

There you see project classes after Demo initialization

<img width="1280" alt="classes" src="https://user-images.githubusercontent.com/57998637/231448142-edf8b36a-1699-4633-856c-440c7789e0f7.png">

Project tags metadata after Demo initialization. This data is empty.

<img width="1280" alt="empty_tags" src="https://user-images.githubusercontent.com/57998637/231447574-fc4002cc-3e0e-45e0-9a3c-e8c8ccd04db8.png">

Visualization in Labeling Tool before we add tags

<img width="1280" alt="initial" src="https://user-images.githubusercontent.com/57998637/232045216-93e52991-4ee4-46a8-8d06-50d47042b18f.png">

**Step 5.** Change Workspace ID in `local.env` file by copying the ID from the context menu of the workspace. Do the same for Project ID and Dataset ID .

```python
WORKSPACE_ID=82841  # ⬅️ change value
PROJECT_ID=239385  # ⬅️ change value
DATASET_ID=774629  # ⬅️ change value
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
project_meta_json = api.project.get_meta(project_id)
project_meta = sly.ProjectMeta.from_json(data=project_meta_json)

key_id_map = sly.KeyIdMap()

pcd_ep_ann_json = api.pointcloud_episode.annotation.download(dataset_id)
```

### **Create new tag metadata**

To create a new tag, you need to first define a tag metadata. This includes specifying the tag name, type, the objects to which it can be added, and the possible values. This base information will be used to create the actual tags.

```python
tag_name = "Car"
tag_values = ["car_1", "car_2"]

if not project_meta.tag_metas.has_key(tag_name):
    new_tag_meta = sly.TagMeta(
        tag_name,
        sly.TagValueType.ONEOF_STRING,
        applicable_to=sly.TagApplicableTo.OBJECTS_ONLY,
        possible_values=tag_values,
    )
```

Then recreate the source project metadata with new tag metadata.

```python
    new_tags_collection = project_meta.tag_metas.add(new_tag_meta)
    new_project_meta = sly.ProjectMeta(
        tag_metas=new_tags_collection, obj_classes=project_meta.obj_classes
    )
    api.project.update_meta(project_id, new_project_meta)
```

New tag metadatas added

<img width="1280" alt="tag_meta_created" src="https://user-images.githubusercontent.com/57998637/232045203-f9d16210-fc4d-48ed-a71e-33b0c45f1fab.png">

Right after updating the metadata, we need to obtain added metadata on the previous step to get the IDs in the next steps.

```python
    new_prject_meta_json = api.project.get_meta(project_id)
    new_project_meta = sly.ProjectMeta.from_json(data=new_prject_meta_json)
    new_tag_meta = new_project_meta.tag_metas.get(new_tag_meta.name)
```

### **Or use existing tag metadata**

If a tag with the `tag_name` already exists in the metadata, we could just use it if it fits our requirements.

```python
else:
    new_tag_meta = project_meta.tag_metas.get(tag_name)
    if sorted(new_tag_meta.possible_values) != sorted(tag_values):
        sly.logger.warning(
            f"Tag [{new_tag_meta.name}] already exists, but with another values: {new_tag_meta.possible_values}"
        )
```

In case this tag doesn't meet our requirements, it would be better to create a new one with a different name. On the other hand, we could update the tag values.

### **Create new tag with value and add to objects**

When you pass information from tag metadata using its ID to the object, a new tag is created and appended.

If you want to add a tag with value, you can define the `value` argument with possible values.

If you want to add a tag to frames, you can define the `frame_range` argument.

```python
project_objects = pcd_ep_ann_json.get("objects")
tag_frames = [0, 26]
created_tag_ids = {}

for object in project_objects:
    if object["classTitle"] == "Car":
        tag_id = api.pointcloud_episode.object.tag.add(
            new_tag_meta.sly_id, object["id"], value="car_1", frame_range=tag_frames
        )
        created_tag_ids[object["id"]] = tag_id
```

`created_tag_ids` uses to store IDs for the following operations.

Visualization in Labeling Tool with new tags

<img width="1280" alt="tad_added" src="https://user-images.githubusercontent.com/57998637/232045207-5a52b32c-c766-4219-8713-d18e7174432a.png">

You could more precisely define `tag_frames` in your dataset using the following example:

replace line number 46 of source code with this:

```python
project_frames = pcd_ep_ann_json.get("frames")
```

insert on line number 51 of source code this:

```python
        frame_range = []
        for frame in project_frames:
            for figure in frame["figures"]:
                if figure["objectId"] == object["id"]:
                    frame_range.append(frame["index"])
        frame_range = frame_range[0:1] + frame_range[-1:]
```

You will most likely need to modify this example to more accurately define the objects. It is only provided to make it faster and easier to understand where and with what information to interact.

### **Update tag value**

Also, if you need to correct tag values, you can easily do so as follows:

```python
tag_id_to_operate = created_tag_ids.get(project_objects[0]["id"])

api.pointcloud_episode.object.tag.update(tag_id_to_operate, "car_2")
```

In our example, we took the first annotated object and the tag assigned to it in the previous step.

You can use a different approach to obtain information about objects, their tags, and the values of those tags according to your goal.

<img width="1280" alt="tag_updated" src="https://user-images.githubusercontent.com/57998637/232045213-477829d1-f9ee-4a39-9551-931bc9034111.png">

### **Delete tag**

To remove a tag, all you need is its ID.

```python
api.pointcloud_episode.object.tag.remove(tag_id_to_operate)
```

<img width="1280" alt="tagg_removed" src="https://user-images.githubusercontent.com/57998637/232045214-17174d7b-f84b-433e-ae88-1930eedb451b.png">

Please note that you are only deleting the tag from the object. To remove a tag from the project (`TagMeta`), you need to use other SDK methods.