# google-takeout-photos-cleanup
Cleans up the messy output from exporting photos via Google Takeout!

Currently does the following actions:
- Identifies all files to keep
  - Skips JSON files, files with blacklisted hyphen segments (ex. "-edited", which seems to be a lower quality copy), and files with a file count number where there is a matching file without the number (ex. drop 20230817122243(1).jpeg if 0230817122243.jpeg exists)
- Uses the JSON files to set the DateTime in the EXIF for images
  - For .gif files, it sets the creationDate on the actual file
  - If the JSON doesn't exist, it's probably a download, so it re-uses the last timestamp
- Copies all files to keep to an output directory

Remaining work
- Support nested folders
- Change the behavior to not modify the EXIF/dates on the original files, only the ones copied into the output

# Development
## Using the virtual environment
### Creation
The standard way to create an environment is 'python3 -m venv {path}'.
I used 'venv' as the path by specifying './venv'
### Activation
Activate with 'source {path}/bin/activate'
> Remember to 'pip install -r requirements.txt'
### Deactivation
'deactivate'

# References
- [PIL ExifTags](https://pillow.readthedocs.io/en/stable/reference/ExifTags.html#module-PIL.ExifTags) for working with EXIF

# Example Google Takeout JSON file
``` json
{
  "title": "IMG_20140830_193932281.jpg",
  "description": "",
  "imageViews": "82",
  "creationTime": {
    "timestamp": "1460229348",
    "formatted": "Apr 9, 2016, 7:15:48 PM UTC"
  },
  "photoTakenTime": {
    "timestamp": "1409598797",
    "formatted": "Sep 1, 2014, 7:13:17 PM UTC"
  },
  "geoData": {
    "latitude": 0.0,
    "longitude": 0.0,
    "altitude": 0.0,
    "latitudeSpan": 0.0,
    "longitudeSpan": 0.0
  },
  "geoDataExif": {
    "latitude": 0.0,
    "longitude": 0.0,
    "altitude": 0.0,
    "latitudeSpan": 0.0,
    "longitudeSpan": 0.0
  },
  "people": [<REDACTED>],
  "url": "https://photos.google.com/photo/<REDACTED>",
  "googlePhotosOrigin": {
    "mobileUpload": {
      "deviceType": "ANDROID_PHONE"
    }
  }
}
```
