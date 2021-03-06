# Image Processing API

David Souther <dsouther@seattleu.edu>
2020-02-11 Image Processing API

## Overview

An online image quick-processing system for an industrial or similar internet-of-things photo-based QA system.
This system provides an HTTP interface for cameras in an industrial setting to submit photos to a central location, and issue basic normalization commands given an on-device configuration.
On device configuration can include details on areas to crop/flip/rotate/resize the image.
Processing and storage happen in a central location, with higher capacity than on-device.
The results of the photo transforms will be available for usage eg in an ML/Image recognition pipeline for QA.
(All images PNG, because I choose so)

### Components

* Camera devices - Will be provided with a configuration including API server, necessary network information, frequency of photos, and calibration for what edit commands to dispatch.
* API Server - Implements the HTTP interface below, and monitors a message queue to track which operations have been completed.
* Processor - Coordinates image converters running in appropriate workflow order.
* Metadata Store - SQL database. See schema below.
* File Store - high-volume NAS store, available to API & Image processors.
* Image converters - Wrapper around image magic, to perform the processing of images stored on the NAS.

```
[ditaa, components, png]
+```--+   +-------------+
|Camera|<--|Configuration|
|  {io}|   |  {d}        |
+```--+   +-------------+
  |
  |
  v
+---+ operation +```-----+
|API|-#```---->|Processor|
+---+           +```-----+
 | |               |  | ^
 | |   +```-------+  | |
 | |   |       convert: :finished
 | v   v              v |
 |+```----+      +----------+
 ||Metadata|      |Converters|
 |+     {s}+      +```------+
 |+```----+        |
 |                  |
 |  +---+           |
 +->|NAS|<```------+
    |{s}|
    +---+
```

### Connectors

* Devices to API: HTTP, see details below.
* API to Metadata: SQL Connector du Jour.
* API to File: NAS Filesystem.
* API to Processor: Rabbit MQ or similar.
* Processor to Converters: Rabbit MQ.
* Image to File: NAS Filesystem.

## Communication

The main API will provide a minimal resource API, with a specific RPC for executing a list of transform operations.
Uploads will use multipart form data.
Other RPC requests will use a simple flat POST body, with one command per line.


### Resource API

* `GET /photos -> [{id}]` List of photo IDs 
* `GET /device/{device}/photos -> [{id}]` List of photos limited to a single device
* `POST /photos device#{device} file#{photo} -> /photos/{id}` Upload a photo, returns the generated ID
* `GET /photos/{id}.png -> {photo}` Download a single image. Photo must be an ID.
* `POST /photos/{id}:transform [op] -> [{opid}]` Queue a list of transformations to apply to the photo at {id}. Returns a list of {opid}s which will get filled with results.
* `GET /photos/{id}/first.png -> {photo}` Return the original, raw photo posted.
* `GET /photos/{id}/steps -> [{opid}]` Returns a list of opids which are either younger than 30 days, or are in use.
* `GET /photos/{id}/steps/{opid}.png -> {photo}` Return the photo at {opid} transform.
* `POST /photos/{id}/steps/{opid}:rebase -> /photos/{id}` Move the photo step at {opid} to be the current photo in {id}, for get and future operations

### Commands

* `flip {axis}` axis is vertical or horizontal
* `rotate {degrees}` number degrees; positive # dextral, negative # sinistral; left # -90, right # 90
* `crop {left}:{top}:{width}:{height}` Crop region of photo specifying the top-left corner and size of the crop region.
* `resize {x?}:{y?}` One of x or y must be specified. If both, sets size to both. If only one, keeps aspect ratio.
* `thumbnail` Shorthand for resize larger size to 64

#### API to convert mapping

The above API converts directly to imagemagic color and geometry commands.

```
flip horizontal -> -flop
flip vertical -> -flip
rotate -> -rotate {d}
crop l:t:w:h -> -crop {w}x{h}+{l}+{t}
resize x?:y? -> -resize {x}x{y}
grayscale -> -color gray
```

### Database

The database tracks which photos have been uploaded, and the operations that have been performed on them.

```
Photo
- ID
- Device
- Created
- Current opid
primary key (id)

Operation
- Photo ID
- Operation ID
- Previous Operation ID
- Operation Completed
- Operation Description
primary key (photo id, operation id)
```

### Filesystem

The NAS filesystem has a simple structure, storing all pngs in a folder with the photo's name, and using the opid as the image name. `first` is the original, unmodified, upload. `current` is a symlink to the most recently edited image.

```
ROOT/
  photos/
    id/
      current -> {opid}.jpg
      first.png
      {opid}.png
```

### Messages

Messages send on one of three channels.

* `operation` queues operations for the Processor.
* `convert` has operations that converters are safe to perform, that is, the operations will only be sent when the processor confirms the previous image is available.
* `finished` takes the operation that the converter has just performed, and sends it to the processor to mark as complete.

Operations have the format `photo_id opid last_opid operation argument`

## Backend

This unified system manages collection and normalization of IoT image collection for an industrial QA process.
Cameras at various locations in the system take pictures of the assembly line.
These photos are uploaded to the central file system.
The camera then uses an on-board configuration to instruct the central file system to normalize the images it generated to the appropriate constraints for recognition.
Configurations are flat text files, with the operations listed in order, one per line.

## Security & Operations

Primary security is an intranet system.
Traffic and endpoints will be unsecured within the intranet.
Operations may apply network level controls (eg internal firewalls based on device IP or Mac address) to limit communication with the API system.
The NAS should be dedicated to the image processing system, in close proximity to the image processors, and able to handle 100Mb reads/writes per second.
This assumes \~1Mb images from the camera.

## Implementation

Sample implementation is at https://github.com/DavidSouther/cpsc5200/images.
