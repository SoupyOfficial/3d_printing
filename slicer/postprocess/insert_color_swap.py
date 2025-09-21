#!/usr/bin/env python3
"""
Insert Color Swap Commands into G-code
Supports both M600 (firmware filament change) and pause-based color swaps

Usage:
    python insert_color_swap.py --input file.gcode --by layer --value 5 --mode m600
    python insert_color_swap.py --input file.gcode --by height --value 1.0 --mode pause
"""

import argparse
import sys
import os
import re
from typing import List, Tuple, Optional

class GCodeProcessor:
    def __init__(self):
        self.lines = []
        self.layer_heights = []
        self.current_height = 0.0
        self.layer_count = 0
        
    def load_gcode(self, filepath: str) -> bool:
        """Load G-code file and parse layer information"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.lines = f.readlines()
            
            print(f"Loaded {len(self.lines)} lines from {filepath}")
            self._parse_layers()
            return True
            
        except FileNotFoundError:
            print(f"ERROR: File not found: {filepath}")
            return False
        except Exception as e:
            print(f"ERROR: Failed to load file: {e}")
            return False
    
    def _parse_layers(self):
        """Parse G-code to identify layer changes and heights"""
        self.layer_heights = []
        self.current_height = 0.0
        self.layer_count = 0
        
        # Regex patterns for layer detection
        z_move_pattern = re.compile(r'^G[01]\s+.*Z([\d\.]+)', re.IGNORECASE)
        layer_comment_pattern = re.compile(r';\s*LAYER[_\s:]*(\d+)', re.IGNORECASE)
        height_comment_pattern = re.compile(r';\s*layer height[_\s:]*(\d+\.?\d*)', re.IGNORECASE)
        
        for i, line in enumerate(self.lines):
            line_stripped = line.strip()
            
            # Check for layer comments (most reliable)
            layer_match = layer_comment_pattern.search(line_stripped)
            if layer_match:
                self.layer_count = int(layer_match.group(1))
                self.layer_heights.append((self.layer_count, i, self.current_height))
                continue
            
            # Check for Z moves (as backup)
            z_match = z_move_pattern.search(line_stripped)
            if z_match:
                new_height = float(z_match.group(1))
                if new_height > self.current_height:
                    self.current_height = new_height
                    self.layer_count += 1
                    self.layer_heights.append((self.layer_count, i, self.current_height))
        
        print(f"Detected {len(self.layer_heights)} layers, max height: {self.current_height:.2f}mm")
    
    def find_insertion_point(self, target_type: str, target_value: float) -> Optional[int]:
        """Find the line number to insert color swap command"""
        if target_type == "layer":
            target_layer = int(target_value)
            for layer_num, line_idx, height in self.layer_heights:
                if layer_num >= target_layer:
                    print(f"Found insertion point: Layer {layer_num} at line {line_idx} (height: {height:.2f}mm)")
                    return line_idx
            
        elif target_type == "height":
            target_height = float(target_value)
            for layer_num, line_idx, height in self.layer_heights:
                if height >= target_height:
                    print(f"Found insertion point: Layer {layer_num} at line {line_idx} (height: {height:.2f}mm)")
                    return line_idx
        
        print(f"ERROR: Could not find insertion point for {target_type} {target_value}")
        return None
    
    def insert_color_swap(self, line_idx: int, mode: str) -> bool:
        """Insert color swap commands at specified line"""
        if mode == "m600":
            commands = self._generate_m600_commands()
        elif mode == "pause":
            commands = self._generate_pause_commands()
        else:
            print(f"ERROR: Unknown mode '{mode}'. Use 'm600' or 'pause'")
            return False
        
        # Insert commands as separate lines
        for i, cmd in enumerate(commands):
            self.lines.insert(line_idx + i, cmd + '\n')
        
        print(f"Inserted {len(commands)} color swap commands in {mode} mode")
        return True
    
    def _generate_m600_commands(self) -> List[str]:
        """Generate M600 filament change commands"""
        return [
            "; === COLOR SWAP - M600 FILAMENT CHANGE ===",
            "M600 ; Firmware filament change",
            "; Printer will:",
            ";   1. Pause and park nozzle",
            ";   2. Retract filament automatically", 
            ";   3. Wait for user to change filament",
            ";   4. Purge and resume when confirmed",
            "; === RESUME PRINTING WITH NEW COLOR ==="
        ]
    
    def _generate_pause_commands(self) -> List[str]:
        """Generate pause-based color swap commands"""
        return [
            "; === COLOR SWAP - MANUAL PAUSE ===",
            "M117 Color swap required ; Display message",
            "G91 ; Relative positioning",
            "G1 E-5 F300 ; Retract filament",
            "G1 Z5 F3000 ; Raise Z for clearance",
            "G90 ; Absolute positioning", 
            "G1 X10 Y10 F6000 ; Park nozzle",
            "M0 Change filament and press resume ; Infinite pause",
            "; Manual steps:",
            ";   1. Retract remaining filament (10-15mm)",
            ";   2. Remove old filament completely",
            ";   3. Load new filament until visible",
            ";   4. Purge until clean color (50-100mm)",
            ";   5. Press resume to continue",
            "G1 E5 F300 ; Prime extruder",
            "; === RESUME PRINTING WITH NEW COLOR ==="
        ]
    
    def save_gcode(self, filepath: str) -> bool:
        """Save modified G-code to file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(self.lines)
            
            print(f"Saved modified G-code to: {filepath}")
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to save file: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Get statistics about the G-code file"""
        return {
            'total_lines': len(self.lines),
            'layers_detected': len(self.layer_heights),
            'max_height': self.current_height,
            'estimated_print_time': self._estimate_print_time()
        }
    
    def _estimate_print_time(self) -> str:
        """Extract estimated print time from G-code comments"""
        time_pattern = re.compile(r';\s*estimated printing time.*?(\d+)h?\s*(\d+)m?\s*(\d+)?s?', re.IGNORECASE)
        
        for line in self.lines[:50]:  # Check first 50 lines for metadata
            match = time_pattern.search(line)
            if match:
                hours = int(match.group(1)) if match.group(1) else 0
                minutes = int(match.group(2)) if match.group(2) else 0
                seconds = int(match.group(3)) if match.group(3) else 0
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        return "Unknown"


def generate_output_filename(input_file: str, target_type: str, target_value: float, mode: str) -> str:
    """Generate output filename with swap parameters"""
    base, ext = os.path.splitext(input_file)
    
    if target_type == "layer":
        suffix = f"_swap_L{int(target_value)}"
    else:  # height
        suffix = f"_swap_H{target_value:.1f}mm"
    
    return f"{base}{suffix}{ext}"


def main():
    parser = argparse.ArgumentParser(
        description="Insert color swap commands into G-code files",
        epilog="""
Examples:
  %(prog)s --input bow_tie.gcode --by layer --value 5 --mode m600
  %(prog)s --input bow_tie.gcode --by height --value 1.0 --mode pause --output custom_name.gcode
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--input', '-i', required=True,
                       help='Input G-code file path')
    
    parser.add_argument('--by', choices=['layer', 'height'], required=True,
                       help='Insert by layer number or height in mm')
    
    parser.add_argument('--value', '-v', type=float, required=True,
                       help='Layer number or height value for insertion')
    
    parser.add_argument('--mode', '-m', choices=['m600', 'pause'], required=True,
                       help='Color swap mode: m600 (firmware) or pause (manual)')
    
    parser.add_argument('--output', '-o',
                       help='Output file path (auto-generated if not specified)')
    
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without modifying files')
    
    parser.add_argument('--verbose', action='store_true',
                       help='Show detailed processing information')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input):
        print(f"ERROR: Input file not found: {args.input}")
        sys.exit(1)
    
    # Generate output filename if not specified
    if not args.output:
        args.output = generate_output_filename(args.input, args.by, args.value, args.mode)
    
    # Initialize processor
    processor = GCodeProcessor()
    
    print(f"Processing G-code file: {args.input}")
    print(f"Target: {args.by} {args.value}")
    print(f"Mode: {args.mode}")
    print(f"Output: {args.output}")
    print("-" * 50)
    
    # Load and process
    if not processor.load_gcode(args.input):
        sys.exit(1)
    
    if args.verbose:
        stats = processor.get_stats()
        print(f"File statistics:")
        print(f"  Total lines: {stats['total_lines']}")
        print(f"  Layers detected: {stats['layers_detected']}")  
        print(f"  Max height: {stats['max_height']:.2f}mm")
        print(f"  Estimated time: {stats['estimated_print_time']}")
        print()
    
    # Find insertion point
    insertion_line = processor.find_insertion_point(args.by, args.value)
    if insertion_line is None:
        sys.exit(1)
    
    if args.dry_run:
        print("DRY RUN: Would insert color swap commands at line", insertion_line)
        if args.mode == "m600":
            commands = processor._generate_m600_commands()
        else:
            commands = processor._generate_pause_commands()
        
        print("Commands that would be inserted:")
        for cmd in commands:
            print(f"  {cmd}")
        
        print(f"Output would be saved to: {args.output}")
        return
    
    # Insert color swap commands
    if not processor.insert_color_swap(insertion_line, args.mode):
        sys.exit(1)
    
    # Save modified file
    if not processor.save_gcode(args.output):
        sys.exit(1)
    
    print("-" * 50)
    print("Color swap insertion completed successfully!")
    print(f"Modified G-code saved to: {args.output}")
    
    # Show final stats
    final_stats = processor.get_stats()
    print(f"Final file: {final_stats['total_lines']} lines")


if __name__ == "__main__":
    main()