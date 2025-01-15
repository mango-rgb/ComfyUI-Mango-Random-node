import os
import random
import torch
from PIL import Image, ImageOps
import numpy as np
import cv2
import time


class RandomFilePathNode:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory_path": ("STRING", {"default": ""}),
            },
        }

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")

    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_random_file_path"
    CATEGORY = "🥭 芒果节点/文件"

    def get_random_file_path(self, directory_path: str) -> str:
        if not os.path.isdir(directory_path):
            raise NotADirectoryError(
                f"'{directory_path}' is not a valid directory path.")

        files = []

        # Walk through the directory tree
        for root, dirs, files_in_dir in os.walk(directory_path):
            for file_name in files_in_dir:
                # Build full path to the file
                full_file_path = os.path.join(root, file_name)
                # Check if the file has a valid extension
                files.append(full_file_path)

        if not files:
            raise FileNotFoundError(
                f"No files found in directory: {directory_path}")

        path = random.choice(files)
        return (path,)


class RandomImagePathNode:
    def __init__(self):
        self.current_seed = 0
        self.current_index = 0

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory_path": ("STRING", {"default": ""}),
                "sort_mode": (["完全随机" , "顺序循环"],),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
        }

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")

    RETURN_TYPES = ("IMAGE", "MASK", "STRING")
    RETURN_NAMES = ("image", "mask", "text_content")
    FUNCTION = "get_random_image_path"
    CATEGORY = "🥭 芒果节点/文件"

    def get_random_image_path(self, directory_path, sort_mode, seed) -> tuple:
        if not os.path.isdir(directory_path):
            raise NotADirectoryError(
                f"'{directory_path}' is not a valid directory path.")

        valid_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp")
        files = []

        for root, dirs, files_in_dir in os.walk(directory_path):
            for file_name in files_in_dir:
                full_file_path = os.path.join(root, file_name)
                if file_name.lower().endswith(valid_extensions):
                    files.append(full_file_path)

        if not files:
            raise FileNotFoundError(
                f"No image files found in directory: {directory_path}")

        # 根据排序模式选择文件
        elif sort_mode == "顺序循环":
            files.sort(key=lambda x: os.path.basename(x).lower())
            path = files[self.current_index]
            self.current_index = (self.current_index + 1) % len(files)
        else:  # 完全随机模式
            path = random.choice(files)

        image = Image.open(path)
        image = ImageOps.exif_transpose(image)
        
        # 处理alpha通道
        if image.mode == 'RGBA':
            rgb = image.convert('RGB')
            alpha = image.split()[3]
            
            image = np.array(rgb).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]
            
            mask = np.array(alpha).astype(np.float32) / 255.0
            mask = torch.from_numpy(mask)[None,]
        else:
            image = image.convert('RGB')
            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]
            
            mask = torch.ones((1, image.shape[2], image.shape[3]), dtype=torch.float32)

        # 获取对应的txt文件内容
        txt_path = os.path.splitext(path)[0] + '.txt'
        text_content = ""
        try:
            if os.path.exists(txt_path):
                with open(txt_path, 'r', encoding='utf-8') as f:
                    text_content = f.read().strip()
            else:
                text_content = "No corresponding text file found"
        except Exception as e:
            text_content = f"Error reading text file: {str(e)}"

        return (image, mask, text_content)


video_extensions = ('webm', 'mp4', 'mkv', 'gif')


class RandomVideoPathNode:
    def __init__(self):
        self.current_seed = 0
        self.current_index = 0

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory_path": ("STRING", {"default": ""}),
                "sort_mode": (["完全随机", "顺序循环"],),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
        }

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")

    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("images", "path", "text_content")
    FUNCTION = "get_random_video_path"
    CATEGORY = "🥭 芒果节点/文件"

    def get_random_video_path(self, directory_path, sort_mode, seed) -> tuple:
        if not os.path.isdir(directory_path):
            raise NotADirectoryError(
                f"'{directory_path}' is not a valid directory path.")

        files = []
        for root, dirs, files_in_dir in os.walk(directory_path):
            for file_name in files_in_dir:
                full_file_path = os.path.join(root, file_name)
                if file_name.lower().endswith(video_extensions):
                    files.append(full_file_path)

        if not files:
            raise FileNotFoundError(
                f"No video files found in directory: {directory_path}")

        # 根据排序模式选择文件
        if sort_mode == "顺序循环":
            files.sort(key=lambda x: os.path.basename(x).lower())
            path = files[self.current_index]
            self.current_index = (self.current_index + 1) % len(files)
        else:  # 完全随机模式
            random.seed(seed)
            path = random.choice(files)

        images = FrameGenerator(path)

        # 获取对应的txt文件内容
        txt_path = os.path.splitext(path)[0] + '.txt'
        text_content = ""
        try:
            if os.path.exists(txt_path):
                with open(txt_path, 'r', encoding='utf-8') as f:
                    text_content = f.read().strip()
            else:
                text_content = "No corresponding text file found"
        except Exception as e:
            text_content = f"Error reading text file: {str(e)}"

        return (images, path, text_content)


def get_video_frames(video_path):
    video_cap = cv2.VideoCapture(video_path)

    if not video_cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")

    frames = []
    while True:
        ret, frame = video_cap.read()
        if not ret:
            break
        frames.append(frame)

    video_cap.release()
    return frames


class FrameGenerator:
    def __init__(self, video_path):
        self.video_path = video_path
        self.frames = self._load_frames()

    def _load_frames(self):
        video_cap = cv2.VideoCapture(self.video_path)
        if not video_cap.isOpened():
            raise ValueError(f"Could not open video file: {self.video_path}")

        frames = []
        while True:
            ret, frame = video_cap.read()
            if not ret:
                break

            # Convert frame from BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert frame to a torch tensor and normalize it
            frame_tensor = torch.from_numpy(frame).float() / 255.0

            frames.append(frame_tensor)

        video_cap.release()
        return frames

    def __len__(self):
        return len(self.frames)

    def __getitem__(self, index):
        return self.frames[index]

    def __iter__(self):
        return iter(self.frames)


NODE_CLASS_MAPPINGS = {
    "Random Video Path": RandomVideoPathNode,
    "Random Image Path": RandomImagePathNode,
    "Random File Path": RandomFilePathNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Random Video Path": "随机视频 🥭",
    "Random Image Path": "随机图片 🥭",
    "Random File Path": "随机文件 🥭",
}
