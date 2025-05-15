import os
import shutil
import random
from glob import glob
from pathlib import Path
import cv2
import yaml
from datetime import datetime
import hashlib

class DatasetMerger:
    def __init__(self, config):
        self.input_folders = config['input_folders']
        self.output_base = config['output_base']
        self.split_ratio = config['split_ratio']
        self.target_size = config['target_size']
        self.class_names = config['class_names']
        
        # Create timestamped output folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_folder = os.path.join(self.output_base, f"dataset_{timestamp}")
        
    def run(self):
        # Step 1: Collect and validate all image-label pairs
        all_pairs = self.collect_pairs()
        
        # Step 2: Remove duplicates
        unique_pairs = self.remove_duplicates(all_pairs)
        print(f"Found {len(all_pairs)} pairs, {len(unique_pairs)} after removing duplicates")
        
        # Step 3: Split dataset
        splits = self.split_dataset(unique_pairs)
        
        # Step 4: Process and save splits
        self.process_splits(splits)
        
        # Step 5: Create data.yaml
        self.create_yaml()
        
        print(f"✅ Dataset created at: {self.output_folder}")

    def collect_pairs(self):
        """Collect all valid (image, label) pairs from input folders"""
        image_extensions = ['.jpg', '.jpeg', '.png']
        all_pairs = []
        
        for folder in self.input_folders:
            image_dir = os.path.join(folder, 'images')
            label_dir = os.path.join(folder, 'labels')
            
            if not os.path.exists(image_dir) or not os.path.exists(label_dir):
                print(f"⚠️ Missing images/labels folder in {folder}")
                continue
                
            for ext in image_extensions:
                for img_path in glob(os.path.join(image_dir, f'*{ext}')):
                    label_path = os.path.join(label_dir, Path(img_path).stem + '.txt')
                    if os.path.exists(label_path):
                        all_pairs.append((img_path, label_path))
                    else:
                        print(f"⚠️ Missing label for {img_path}")
        
        return all_pairs

    def remove_duplicates(self, pairs):
        """Remove duplicate images using MD5 hashing"""
        unique_hashes = set()
        unique_pairs = []
        
        for img_path, label_path in pairs:
            with open(img_path, 'rb') as f:
                img_hash = hashlib.md5(f.read()).hexdigest()
                
            if img_hash not in unique_hashes:
                unique_hashes.add(img_hash)
                unique_pairs.append((img_path, label_path))
            else:
                print(f"⚠️ Removed duplicate: {img_path}")
        
        return unique_pairs

    def split_dataset(self, pairs):
        """Split dataset according to ratios"""
        random.shuffle(pairs)
        total = len(pairs)
        train_end = int(total * self.split_ratio[0])
        val_end = train_end + int(total * self.split_ratio[1])
        
        return {
            'train': pairs[:train_end],
            'val': pairs[train_end:val_end],
            'test': pairs[val_end:]
        }

    def process_splits(self, splits):
        """Process and save each split"""
        for split_name, pairs in splits.items():
            img_out_dir = os.path.join(self.output_folder, split_name, 'images')
            lbl_out_dir = os.path.join(self.output_folder, split_name, 'labels')
            
            os.makedirs(img_out_dir, exist_ok=True)
            os.makedirs(lbl_out_dir, exist_ok=True)
            
            print(f"Processing {split_name} set ({len(pairs)} samples)")
            
            for img_path, lbl_path in pairs:
                # Process image
                img = cv2.imread(img_path)
                if img is None:
                    print(f"⚠️ Failed to read image: {img_path}")
                    continue
                    
                resized = cv2.resize(img, self.target_size, interpolation=cv2.INTER_LINEAR)
                img_filename = os.path.basename(img_path)
                img_out_path = os.path.join(img_out_dir, img_filename)
                cv2.imwrite(img_out_path, resized)
                
                # Process label (copy as-is)
                lbl_filename = os.path.basename(lbl_path)
                shutil.copy(lbl_path, os.path.join(lbl_out_dir, lbl_filename))

    def create_yaml(self):
        """Create YOLO dataset config file"""
        data = {
            'train': os.path.join('.', 'train', 'images'),
            'val': os.path.join('.', 'val', 'images'),
            'test': os.path.join('.', 'test', 'images'),
            'nc': len(self.class_names),
            'names': self.class_names
        }
        
        with open(os.path.join(self.output_folder, 'data.yaml'), 'w') as f:
            yaml.dump(data, f, sort_keys=False)

if __name__ == "__main__":
    config = {
        'input_folders': [
            r"C:\Users\harsh\OneDrive\Desktop\Drexel\Volunteert\animal_dataset\test",
            r"C:\Users\harsh\OneDrive\Desktop\Drexel\Volunteert\animal_dataset\train",
            r"C:\Users\harsh\OneDrive\Desktop\Drexel\Volunteert\animal_dataset\val",
            r"C:\Users\harsh\OneDrive\Desktop\Drexel\Volunteert\squirrel2.v8i.yolov8\train"
        ],
        'output_base': r"C:\Users\harsh\OneDrive\Desktop\Drexel\Volunteert",
        'split_ratio': (0.7, 0.2, 0.1),  # train, val, test
        'target_size': (640, 640),
        'class_names': ['snake', 'raccoon', 'squirrel']  # Update with your classes
    }
    
    merger = DatasetMerger(config)
    merger.run()