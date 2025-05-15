import os
import yaml
import shutil
from tqdm import tqdm

class SmallObjectFilter:
    def __init__(self, dataset_path, max_size_threshold=0.05):
        """
        Args:
            max_size_threshold: Maximum relative size (width or height) 
                               to consider as small object (0.05 = 5% of image dimension)
        """
        self.dataset_path = dataset_path
        self.threshold = max_size_threshold
        
        with open(os.path.join(dataset_path, 'data.yaml')) as f:
            self.config = yaml.safe_load(f)
    
    def filter_dataset(self, output_dir):
        """Filter dataset keeping only images with small objects"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Create output directory structure
        for split in ['train', 'val', 'test']:
            split_path = os.path.join(self.dataset_path, split)
            if not os.path.exists(split_path):
                continue
                
            # Create output subdirectories
            os.makedirs(os.path.join(output_dir, split, 'images'), exist_ok=True)
            os.makedirs(os.path.join(output_dir, split, 'labels'), exist_ok=True)
            
            # Process each image
            for img_file in tqdm(os.listdir(os.path.join(split_path, 'images'))):
                if not img_file.endswith(('.jpg', '.png', '.jpeg')):
                    continue
                
                label_file = os.path.join(split_path, 'labels', os.path.splitext(img_file)[0] + '.txt')
                if not os.path.exists(label_file):
                    continue
                
                if self.has_small_objects(label_file):
                    # Copy image and label
                    shutil.copy2(
                        os.path.join(split_path, 'images', img_file),
                        os.path.join(output_dir, split, 'images', img_file)
                    )
                    shutil.copy2(
                        os.path.join(split_path, 'labels', label_file),
                        os.path.join(output_dir, split, 'labels', os.path.basename(label_file))
                    )
    
    def has_small_objects(self, label_path):
        """Check if label file contains small objects"""
        with open(label_path) as f:
            for line in f:
                _, x, y, w, h = map(float, line.strip().split())
                if w < self.threshold and h < self.threshold:
                    return True
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, required=True, help='Input YOLO dataset path')
    parser.add_argument('--output', type=str, required=True, help='Output directory for filtered dataset')
    parser.add_argument('--threshold', type=float, default=0.05, 
                       help='Size threshold (default: 0.05 = 5% of image dimension)')
    args = parser.parse_args()
    
    filter = SmallObjectFilter(args.dataset, args.threshold)
    filter.filter_dataset(args.output)
    
    print(f"Filtered dataset with small objects saved to {args.output}")