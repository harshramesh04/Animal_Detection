import os
import cv2
import yaml
from tqdm import tqdm
import shutil

class AnnotationValidator:
    def __init__(self, dataset_path, min_object_size=0.02):
        self.dataset_path = dataset_path
        self.min_object_size = min_object_size  # Relative size threshold (2% of image area)
        
        # Load dataset config
        with open(os.path.join(dataset_path, 'data.yaml')) as f:
            self.config = yaml.safe_load(f)
        
        self.class_names = self.config['names']
        
    def validate_dataset(self, output_dir=None):
        """Validate all images in dataset"""
        splits = ['train', 'val', 'test'] if not output_dir else ['']
        issues = {'missing_annotations': [], 'small_objects': []}
        
        for split in splits:
            split_path = os.path.join(self.dataset_path, split) if split else self.dataset_path
            images_dir = os.path.join(split_path, 'images')
            labels_dir = os.path.join(split_path, 'labels')
            
            for img_file in tqdm(os.listdir(images_dir), desc=f"Validating {split or 'dataset'}"):
                if not img_file.endswith(('.jpg', '.png', '.jpeg')):
                    continue
                
                # Check annotation file exists
                label_file = os.path.join(labels_dir, os.path.splitext(img_file)[0] + '.txt')
                if not os.path.exists(label_file):
                    issues['missing_annotations'].append(os.path.join(split, 'images', img_file))
                    continue
                
                # Check object sizes
                img_path = os.path.join(images_dir, img_file)
                small_objs = self.check_small_objects(img_path, label_file)
                if small_objs:
                    issues['small_objects'].append({
                        'image': os.path.join(split, 'images', img_file),
                        'small_objects': small_objs
                    })
        
        # Save problematic files if output directory specified
        if output_dir:
            self.save_problematic_files(issues, output_dir)
            
        return issues
    
    def check_small_objects(self, img_path, label_path):
        """Check for objects smaller than threshold"""
        img = cv2.imread(img_path)
        h, w = img.shape[:2]
        small_objects = []
        
        with open(label_path) as f:
            for line in f:
                cls, x, y, bw, bh = map(float, line.strip().split())
                # Convert to absolute pixels
                abs_w = bw * w
                abs_h = bh * h
                area = abs_w * abs_h
                
                # Check if object is too small
                if area < (self.min_object_size * w * h):
                    small_objects.append({
                        'class': self.class_names[int(cls)],
                        'size': (abs_w, abs_h),
                        'relative_size': (bw, bh)
                    })
        
        return small_objects
    
    def save_problematic_files(self, issues, output_dir):
        """Save problematic files to separate folders"""
        os.makedirs(os.path.join(output_dir, 'missing_annotations'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'small_objects'), exist_ok=True)
        
        # Copy files with missing annotations
        for img_path in issues['missing_annotations']:
            src = os.path.join(self.dataset_path, img_path)
            dst = os.path.join(output_dir, 'missing_annotations', os.path.basename(img_path))
            shutil.copy2(src, dst)
        
        # Copy files with small objects
        for item in issues['small_objects']:
            src = os.path.join(self.dataset_path, item['image'])
            dst = os.path.join(output_dir, 'small_objects', os.path.basename(item['image']))
            shutil.copy2(src, dst)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, required=True, help='Path to YOLO dataset')
    parser.add_argument('--output', type=str, help='Output directory for problematic files')
    parser.add_argument('--min-size', type=float, default=0.02, 
                       help='Minimum object size as fraction of image area (default: 0.02)')
    args = parser.parse_args()
    
    validator = AnnotationValidator(args.dataset, args.min_size)
    issues = validator.validate_dataset(args.output)
    
    print("\nValidation Results:")
    print(f"- Images with missing annotations: {len(issues['missing_annotations'])}")
    print(f"- Images with small objects: {len(issues['small_objects'])}")