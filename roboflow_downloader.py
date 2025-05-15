# roboflow_downloader.py
import os
from roboflow import Roboflow
from pathlib import Path

class RoboflowDownloader:
    def __init__(self, api_key: str):
        self.rf = Roboflow(api_key=api_key)

    def download_dataset(
        self,
        workspace: str,
        project: str,
        version: int,
        class_name: str,
        format: str = "yolov8",
        output_dir: str = None
    ) -> None:
        output_dir = Path(output_dir or f"{class_name}_images")
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"[Roboflow] Downloading '{class_name}' from {workspace}/{project} v{version}...")
        try:
            project_obj = self.rf.workspace(workspace).project(project)
            project_obj.version(version).download(format=format, location=str(output_dir))
            print(f"[Roboflow] ✅ Downloaded '{class_name}' dataset to: {output_dir}")
        except Exception as e:
            print(f"[Roboflow] ❌ Failed to download '{class_name}': {e}")