#!/usr/bin/env python3
"""
Split large JSON findings file into smaller chunks.

This script splits a JSON file by dividing the 'children' array into chunks
that fit within a specified size limit (default 60MB), while preserving all
other top-level fields in each output file.

Usage:
    python split_json_findings.py <input_file> [--max-size-mb SIZE] [--output-dir DIR]

Example:
    python split_json_findings.py qs_explorer_result/quantum_safe_api_discovery_findings.json --max-size-mb 60
"""

import json
import sys
import os
import argparse
from pathlib import Path


def get_json_size_mb(obj):
    """Calculate the size of a JSON object in MB when serialized."""
    json_str = json.dumps(obj, indent=4)
    return len(json_str.encode('utf-8')) / (1024 * 1024)


def split_json_file(input_file, max_size_mb=60, output_dir=None):
    """
    Split a JSON file by dividing the 'children' array into chunks.
    
    Args:
        input_file: Path to the input JSON file
        max_size_mb: Maximum size per output file in MB
        output_dir: Directory for output files (default: same as input)
    """
    print(f"Reading input file: {input_file}")
    
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Validate structure
    if 'children' not in data:
        print("Error: JSON file does not contain 'children' array")
        sys.exit(1)
    
    children = data['children']
    total_children = len(children)
    print(f"Total children items: {total_children}")
    
    # Prepare output directory
    if output_dir is None:
        output_dir = os.path.dirname(input_file) or '.'
    os.makedirs(output_dir, exist_ok=True)
    
    # Get base filename without extension
    base_name = Path(input_file).stem
    
    # Create template with all fields except children
    template = {k: v for k, v in data.items() if k != 'children'}
    template['children'] = []
    
    # Calculate base size (template without children)
    base_size_mb = get_json_size_mb(template)
    print(f"Base template size: {base_size_mb:.2f} MB")
    
    # Split children into chunks
    current_chunk = []
    chunk_num = 1
    files_created = []
    
    for i, child in enumerate(children):
        # Test if adding this child would exceed the limit
        test_data = template.copy()
        test_data['children'] = current_chunk + [child]
        test_size = get_json_size_mb(test_data)
        
        if test_size > max_size_mb and current_chunk:
            # Save current chunk
            output_file = os.path.join(output_dir, f"{base_name}_part{chunk_num}.json")
            chunk_data = template.copy()
            chunk_data['children'] = current_chunk
            
            with open(output_file, 'w') as f:
                json.dump(chunk_data, f, indent=4)
            
            file_size = get_json_size_mb(chunk_data)
            print(f"Created: {output_file} ({file_size:.2f} MB, {len(current_chunk)} children)")
            files_created.append(output_file)
            
            # Start new chunk
            current_chunk = [child]
            chunk_num += 1
        else:
            current_chunk.append(child)
        
        # Progress indicator
        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1}/{total_children} children...")
    
    # Save final chunk
    if current_chunk:
        output_file = os.path.join(output_dir, f"{base_name}_part{chunk_num}.json")
        chunk_data = template.copy()
        chunk_data['children'] = current_chunk
        
        with open(output_file, 'w') as f:
            json.dump(chunk_data, f, indent=4)
        
        file_size = get_json_size_mb(chunk_data)
        print(f"Created: {output_file} ({file_size:.2f} MB, {len(current_chunk)} children)")
        files_created.append(output_file)
    
    print(f"\nSplit complete!")
    print(f"Created {len(files_created)} files:")
    for f in files_created:
        print(f"  - {f}")


def main():
    parser = argparse.ArgumentParser(
        description='Split large JSON findings file into smaller chunks',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Split with default 60MB limit
  python split_json_findings.py qs_explorer_result/quantum_safe_api_discovery_findings.json
  
  # Split with custom size limit
  python split_json_findings.py input.json --max-size-mb 50
  
  # Specify output directory
  python split_json_findings.py input.json --output-dir ./output
        """
    )
    
    parser.add_argument('input_file', help='Path to the input JSON file')
    parser.add_argument('--max-size-mb', type=float, default=60,
                        help='Maximum size per output file in MB (default: 60)')
    parser.add_argument('--output-dir', help='Output directory (default: same as input file)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file not found: {args.input_file}")
        sys.exit(1)
    
    split_json_file(args.input_file, args.max_size_mb, args.output_dir)


if __name__ == '__main__':
    main()

# Made with Bob
