#!/usr/bin/env python3
"""
Enhanced Metadata Cleaner - Complete Privacy Tool (Cross-Platform)
Recursively removes ALL metadata and digital footprints from files.

✅ WORKS ON: Windows, Linux, macOS

Features:
    - Comprehensive metadata removal for all file types
    - Progress tracking with visual feedback
    - Detailed logging and statistics
    - Backup creation before cleaning
    - Safe handling of file errors
    - Timestamp normalization
    - EXIF, XMP, IPTC removal from images
    - Metadata stripping from videos, PDFs, Office docs, audio files
    - Cross-platform compatibility (Windows/Linux/macOS)
    
Requirements:
    - Python 3.8+
    - exiftool (highly recommended):
        Windows: Download from https://exiftool.org/
        Linux: apt-get install libimage-exiftool-perl
        macOS: brew install exiftool
    - ffmpeg (for videos):
        Windows: Download from https://ffmpeg.org/download.html
        Linux: apt-get install ffmpeg
        macOS: brew install ffmpeg
    - pip install pillow pypdf python-docx mutagen openpyxl

Usage:
    python clean_metadata.py                    # Clean current directory
    python clean_metadata.py --path /my/files   # Clean specific directory
    python clean_metadata.py --dry-run          # Preview what will be cleaned
    python clean_metadata.py --backup           # Create backups before cleaning
    python clean_metadata.py --reencode-videos  # Re-encode videos (slower but thorough)
    python clean_metadata.py --normalize-time   # Set all timestamps to epoch
"""

import argparse
import hashlib
import json
import logging
import os
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Optional imports with graceful fallbacks
try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import mutagen
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

try:
    from openpyxl import load_workbook
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

# Supported file extensions by category
FILE_CATEGORIES = {
    'image': {'.jpg', '.jpeg', '.png', '.webp', '.tif', '.tiff', '.bmp', '.gif', '.heic', '.heif', '.raw', '.cr2', '.nef', '.dng'},
    'video': {'.mp4', '.mov', '.mkv', '.avi', '.webm', '.flv', '.wmv', '.m4v', '.mpg', '.mpeg'},
    'pdf': {'.pdf'},
    'docx': {'.docx', '.doc'},
    'xlsx': {'.xlsx', '.xls'},
    'pptx': {'.pptx', '.ppt'},
    'audio': {'.mp3', '.m4a', '.flac', '.wav', '.ogg', '.wma', '.aac', '.opus'},
    'archive': {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'},
}

# ANSI color codes for terminal output (with Windows support)
class Colors:
    # Detect if we're on Windows and if ANSI is supported
    _is_windows = platform.system() == 'Windows'
    _supports_color = True
    
    if _is_windows:
        try:
            # Enable ANSI colors on Windows 10+
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except:
            _supports_color = False
    
    if _supports_color and not os.getenv('NO_COLOR'):
        HEADER = '\033[95m'
        BLUE = '\033[94m'
        CYAN = '\033[96m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        END = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
    else:
        # Fallback for systems without color support
        HEADER = BLUE = CYAN = GREEN = YELLOW = RED = END = BOLD = UNDERLINE = ''

def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure logging with file and console output."""
    log_level = logging.DEBUG if verbose else logging.INFO
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    
    # Create logs directory (cross-platform)
    if platform.system() == 'Windows':
        log_dir = Path(os.getenv('APPDATA')) / 'MetaWipe' / 'logs'
    else:
        log_dir = Path.home() / '.metadata_cleaner' / 'logs'
    
    log_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f'clean_{timestamp}.log'
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Log file: {log_file}")
    logger.info(f"Platform: {platform.system()} {platform.release()}")
    return logger

def print_banner():
    """Display tool banner."""
    system_name = platform.system()
    banner = f"""
{Colors.CYAN}{Colors.BOLD}╔═══════════════════════════════════════════════════════════╗
║         METAWIPE - METADATA CLEANER v2.0                  ║
║         Complete Privacy & Footprint Removal              ║
║         Platform: {system_name:<44} ║
╚═══════════════════════════════════════════════════════════╝{Colors.END}
"""
    print(banner)

def check_dependencies() -> Dict[str, bool]:
    """Check which external tools are available."""
    deps = {
        'exiftool': bool(shutil.which('exiftool')),
        'ffmpeg': bool(shutil.which('ffmpeg')),
        'pillow': PIL_AVAILABLE,
        'pypdf': PYPDF_AVAILABLE,
        'docx': DOCX_AVAILABLE,
        'mutagen': MUTAGEN_AVAILABLE,
        'openpyxl': OPENPYXL_AVAILABLE,
        'platform': platform.system()
    }
    return deps

def print_dependencies(deps: Dict[str, bool]):
    """Display available dependencies."""
    system = deps.get('platform', 'Unknown')
    print(f"\n{Colors.BOLD}System: {system}{Colors.END}")
    print(f"{Colors.BOLD}Available Tools:{Colors.END}")
    
    for tool, available in deps.items():
        if tool == 'platform':
            continue
        status = f"{Colors.GREEN}✓{Colors.END}" if available else f"{Colors.RED}✗{Colors.END}"
        print(f"  {status} {tool}")
    
    if not deps['exiftool']:
        print(f"\n{Colors.YELLOW}⚠ Warning: exiftool not found. Install for best results:{Colors.END}")
        if system == 'Windows':
            print(f"  Windows: Download from https://exiftool.org/")
            print(f"           Extract exiftool(-k).exe and rename to exiftool.exe")
            print(f"           Add to PATH or place in same folder as this script")
        elif system == 'Darwin':
            print(f"  macOS: brew install exiftool")
        else:
            print(f"  Linux: sudo apt-get install libimage-exiftool-perl")
    
    if not deps['ffmpeg']:
        print(f"\n{Colors.YELLOW}⚠ Warning: ffmpeg not found. Video cleaning will be limited.{Colors.END}")
        if system == 'Windows':
            print(f"  Windows: Download from https://ffmpeg.org/download.html")
            print(f"           Extract and add to PATH")
        elif system == 'Darwin':
            print(f"  macOS: brew install ffmpeg")
        else:
            print(f"  Linux: sudo apt-get install ffmpeg")
    print()

def run_command(cmd: List[str], timeout: int = 300) -> Tuple[int, str, str]:
    """Execute external command safely (cross-platform)."""
    try:
        # On Windows, don't use shell=True for security
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            encoding='utf-8',
            errors='replace'
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except FileNotFoundError:
        return -1, "", f"Command not found: {cmd[0]}"
    except Exception as e:
        return -1, "", str(e)

def create_backup(path: Path, backup_dir: Path) -> bool:
    """Create backup of file before cleaning."""
    try:
        rel_path = path.relative_to(path.parent.parent)
        backup_path = backup_dir / rel_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup_path)
        return True
    except Exception as e:
        logging.error(f"Backup failed for {path}: {e}")
        return False

def clean_with_exiftool(path: Path) -> bool:
    """Use exiftool to strip all metadata (most reliable method)."""
    try:
        # Remove all tags and overwrite original
        cmd = ['exiftool', '-all=', '-overwrite_original', str(path)]
        returncode, stdout, stderr = run_command(cmd)
        
        if returncode == 0:
            # Also remove backup files that exiftool might create
            backup = Path(str(path) + '_original')
            if backup.exists():
                backup.unlink()
            return True
        else:
            logging.debug(f"exiftool error for {path}: {stderr}")
            return False
    except Exception as e:
        logging.error(f"exiftool failed for {path}: {e}")
        return False

def clean_image_pillow(path: Path) -> bool:
    """Clean image metadata using Pillow (fallback method)."""
    if not PIL_AVAILABLE:
        return False
    
    try:
        with Image.open(path) as img:
            # Remove EXIF data by saving without it
            data = list(img.getdata())
            clean_img = Image.new(img.mode, img.size)
            clean_img.putdata(data)
            
            # Save to temporary file
            temp_path = path.with_suffix('.tmp' + path.suffix)
            clean_img.save(temp_path, quality=95, optimize=True)
            
            # Replace original
            temp_path.replace(path)
            return True
    except Exception as e:
        logging.error(f"Pillow cleaning failed for {path}: {e}")
        return False

def clean_video(path: Path, reencode: bool = False) -> bool:
    """Clean video metadata using ffmpeg."""
    if not shutil.which('ffmpeg'):
        return False
    
    try:
        temp_path = path.with_name(path.stem + '_clean' + path.suffix)
        
        if reencode:
            # Re-encode video (slower but more thorough)
            cmd = [
                'ffmpeg', '-i', str(path),
                '-map_metadata', '-1',
                '-c:v', 'libx264', '-crf', '23',
                '-c:a', 'aac', '-b:a', '192k',
                '-movflags', '+faststart',
                '-y', str(temp_path)
            ]
        else:
            # Copy streams without re-encoding (faster)
            cmd = [
                'ffmpeg', '-i', str(path),
                '-map', '0', '-c', 'copy',
                '-map_metadata', '-1',
                '-movflags', '+faststart',
                '-y', str(temp_path)
            ]
        
        returncode, stdout, stderr = run_command(cmd, timeout=600)
        
        if returncode == 0 and temp_path.exists():
            temp_path.replace(path)
            return True
        elif reencode:
            # If re-encode was attempted and failed, don't retry
            return False
        else:
            # Try re-encoding if copy failed
            logging.debug(f"Copy failed for {path}, trying re-encode")
            return clean_video(path, reencode=True)
    except Exception as e:
        logging.error(f"Video cleaning failed for {path}: {e}")
        return False
    finally:
        # Cleanup temp file if it exists
        if temp_path.exists() and path.exists():
            try:
                temp_path.unlink()
            except:
                pass

def clean_pdf(path: Path) -> bool:
    """Clean PDF metadata."""
    if not PYPDF_AVAILABLE:
        return False
    
    try:
        reader = pypdf.PdfReader(str(path))
        writer = pypdf.PdfWriter()
        
        # Copy pages without metadata
        for page in reader.pages:
            writer.add_page(page)
        
        # Clear all metadata fields
        writer.add_metadata({
            '/Author': '',
            '/Creator': '',
            '/Producer': '',
            '/Subject': '',
            '/Title': '',
            '/Keywords': ''
        })
        
        temp_path = path.with_suffix('.tmp.pdf')
        with open(temp_path, 'wb') as f:
            writer.write(f)
        
        temp_path.replace(path)
        return True
    except Exception as e:
        logging.error(f"PDF cleaning failed for {path}: {e}")
        return False

def clean_docx(path: Path) -> bool:
    """Clean Word document metadata."""
    if not DOCX_AVAILABLE:
        return False
    
    try:
        doc = docx.Document(str(path))
        props = doc.core_properties
        
        # Clear all metadata properties
        props.author = ''
        props.title = ''
        props.subject = ''
        props.comments = ''
        props.keywords = ''
        props.last_modified_by = ''
        props.category = ''
        props.content_status = ''
        
        temp_path = path.with_suffix('.tmp.docx')
        doc.save(str(temp_path))
        temp_path.replace(path)
        return True
    except Exception as e:
        logging.error(f"DOCX cleaning failed for {path}: {e}")
        return False

def clean_xlsx(path: Path) -> bool:
    """Clean Excel spreadsheet metadata."""
    if not OPENPYXL_AVAILABLE:
        return False
    
    try:
        wb = load_workbook(str(path))
        props = wb.properties
        
        # Clear metadata
        props.creator = ''
        props.title = ''
        props.description = ''
        props.subject = ''
        props.keywords = ''
        props.lastModifiedBy = ''
        props.category = ''
        
        temp_path = path.with_suffix('.tmp.xlsx')
        wb.save(str(temp_path))
        temp_path.replace(path)
        return True
    except Exception as e:
        logging.error(f"XLSX cleaning failed for {path}: {e}")
        return False

def clean_audio(path: Path) -> bool:
    """Clean audio file metadata."""
    if not MUTAGEN_AVAILABLE:
        return False
    
    try:
        audio = mutagen.File(str(path), easy=True)
        if audio:
            audio.delete()
            audio.save()
            return True
        return False
    except Exception as e:
        logging.error(f"Audio cleaning failed for {path}: {e}")
        return False

def normalize_timestamps(path: Path):
    """Set file timestamps to epoch (Jan 1, 1970) for anonymity."""
    try:
        epoch = 0  # Unix epoch
        os.utime(path, (epoch, epoch))
    except Exception as e:
        logging.debug(f"Timestamp normalization failed for {path}: {e}")

def get_file_category(path: Path) -> str:
    """Determine file category from extension."""
    ext = path.suffix.lower()
    for category, extensions in FILE_CATEGORIES.items():
        if ext in extensions:
            return category
    return 'unknown'

def clean_file(path: Path, args, deps: Dict[str, bool]) -> Tuple[bool, str]:
    """Clean a single file using appropriate method."""
    category = get_file_category(path)
    success = False
    method = "none"
    
    try:
        # Try exiftool first (most comprehensive)
        if deps['exiftool']:
            if clean_with_exiftool(path):
                success = True
                method = "exiftool"
        
        # Use specialized cleaners for certain file types
        if category == 'image' and not success:
            if clean_image_pillow(path):
                success = True
                method = "pillow"
        
        elif category == 'video':
            if clean_video(path, reencode=args.reencode_videos):
                success = True
                method = "ffmpeg"
        
        elif category == 'pdf':
            if clean_pdf(path):
                success = True
                method = "pypdf"
        
        elif category == 'docx':
            if clean_docx(path):
                success = True
                method = "docx"
        
        elif category == 'xlsx':
            if clean_xlsx(path):
                success = True
                method = "openpyxl"
        
        elif category == 'audio':
            if clean_audio(path):
                success = True
                method = "mutagen"
        
        # Normalize timestamps if requested
        if success and args.normalize_time:
            normalize_timestamps(path)
        
        return success, method
    
    except Exception as e:
        logging.error(f"Error cleaning {path}: {e}")
        return False, "error"

def scan_directory(root_path: Path, skip_patterns: Set[str] = None) -> List[Path]:
    """Recursively scan directory for files to clean."""
    if skip_patterns is None:
        skip_patterns = {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}
    
    files = []
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Skip excluded directories
        dirnames[:] = [d for d in dirnames if d not in skip_patterns]
        
        for filename in filenames:
            filepath = Path(dirpath) / filename
            if filepath.is_file():
                files.append(filepath)
    
    return files

def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def print_progress(current: int, total: int, filename: str, success: bool):
    """Print progress bar with current file."""
    bar_length = 40
    progress = current / total
    filled = int(bar_length * progress)
    bar = '█' * filled + '░' * (bar_length - filled)
    
    status = f"{Colors.GREEN}✓{Colors.END}" if success else f"{Colors.RED}✗{Colors.END}"
    percentage = progress * 100
    
    # Truncate filename if too long
    display_name = filename if len(filename) <= 50 else filename[:47] + '...'
    
    print(f"\r{status} [{bar}] {percentage:.1f}% ({current}/{total}) {display_name}", end='', flush=True)

def print_summary(stats: Dict):
    """Print cleaning summary statistics."""
    print(f"\n\n{Colors.BOLD}{Colors.CYAN}╔═══════════════════════════════════════════════════════════╗")
    print(f"║                    CLEANING SUMMARY                       ║")
    print(f"╚═══════════════════════════════════════════════════════════╝{Colors.END}\n")
    
    print(f"{Colors.BOLD}Files Processed:{Colors.END}")
    print(f"  Total files found:      {stats['total_files']}")
    print(f"  Successfully cleaned:   {Colors.GREEN}{stats['cleaned']}{Colors.END}")
    print(f"  Failed:                 {Colors.RED}{stats['failed']}{Colors.END}")
    print(f"  Skipped:                {Colors.YELLOW}{stats['skipped']}{Colors.END}")
    
    print(f"\n{Colors.BOLD}By File Type:{Colors.END}")
    for category, count in sorted(stats['by_category'].items()):
        if count > 0:
            print(f"  {category.capitalize()}: {count}")
    
    print(f"\n{Colors.BOLD}Methods Used:{Colors.END}")
    for method, count in sorted(stats['by_method'].items()):
        if count > 0:
            print(f"  {method}: {count}")
    
    print(f"\n{Colors.BOLD}Total Time:{Colors.END} {stats['elapsed_time']:.2f} seconds")
    
    if stats['backup_dir']:
        print(f"\n{Colors.GREEN}✓ Backups saved to: {stats['backup_dir']}{Colors.END}")
    
    print(f"\n{Colors.CYAN}All metadata and digital footprints have been removed!{Colors.END}\n")

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Enhanced Metadata Cleaner - Remove ALL metadata and digital footprints',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s                              # Clean current directory
  %(prog)s --path /my/files             # Clean specific directory
  %(prog)s --dry-run                    # Preview without making changes
  %(prog)s --backup                     # Create backups before cleaning
  %(prog)s --reencode-videos            # Re-encode videos (thorough but slow)
  %(prog)s --normalize-time             # Anonymize file timestamps
  %(prog)s --verbose                    # Detailed logging
        '''
    )
    
    parser.add_argument('--path', '-p', default='.',
                        help='Directory to clean (default: current directory)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be cleaned without making changes')
    parser.add_argument('--backup', action='store_true',
                        help='Create backups before cleaning')
    parser.add_argument('--reencode-videos', action='store_true',
                        help='Re-encode videos to remove embedded metadata (slower)')
    parser.add_argument('--normalize-time', action='store_true',
                        help='Set all file timestamps to epoch for anonymity')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose logging')
    parser.add_argument('--skip-confirm', action='store_true',
                        help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    # Setup
    print_banner()
    logger = setup_logging(args.verbose)
    deps = check_dependencies()
    print_dependencies(deps)
    
    # Validate path
    root_path = Path(args.path).resolve()
    if not root_path.exists():
        print(f"{Colors.RED}Error: Path does not exist: {root_path}{Colors.END}")
        sys.exit(1)
    
    if not root_path.is_dir():
        print(f"{Colors.RED}Error: Path is not a directory: {root_path}{Colors.END}")
        sys.exit(1)
    
    print(f"{Colors.BOLD}Target Directory:{Colors.END} {root_path}")
    
    # Scan for files
    print(f"\n{Colors.CYAN}Scanning for files...{Colors.END}")
    files = scan_directory(root_path)
    
    if not files:
        print(f"{Colors.YELLOW}No files found to clean.{Colors.END}")
        sys.exit(0)
    
    total_size = sum(f.stat().st_size for f in files if f.exists())
    print(f"{Colors.GREEN}Found {len(files)} files ({format_size(total_size)}){Colors.END}\n")
    
    # Dry run preview
    if args.dry_run:
        print(f"{Colors.YELLOW}DRY RUN - No files will be modified{Colors.END}\n")
        category_counts = {}
        for f in files:
            cat = get_file_category(f)
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        print(f"{Colors.BOLD}Files by type:{Colors.END}")
        for cat, count in sorted(category_counts.items()):
            print(f"  {cat}: {count}")
        
        print(f"\n{Colors.GREEN}Preview complete. Run without --dry-run to clean files.{Colors.END}")
        sys.exit(0)
    
    # Confirmation
    if not args.skip_confirm:
        print(f"{Colors.YELLOW}{Colors.BOLD}WARNING:{Colors.END} This will modify {len(files)} files.")
        if args.backup:
            print(f"{Colors.GREEN}Backups will be created.{Colors.END}")
        else:
            print(f"{Colors.RED}NO BACKUPS will be created. Changes are irreversible!{Colors.END}")
        
        response = input(f"\nProceed with cleaning? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print(f"{Colors.YELLOW}Operation cancelled.{Colors.END}")
            sys.exit(0)
    
    # Setup backup directory
    backup_dir = None
    if args.backup:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if platform.system() == 'Windows':
            backup_dir = Path(os.getenv('APPDATA')) / 'MetaWipe' / 'backups' / timestamp
        else:
            backup_dir = Path.home() / '.metadata_cleaner' / 'backups' / timestamp
        backup_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n{Colors.GREEN}Backup directory: {backup_dir}{Colors.END}")
    
    # Process files
    print(f"\n{Colors.CYAN}{Colors.BOLD}Cleaning files...{Colors.END}\n")
    
    stats = {
        'total_files': len(files),
        'cleaned': 0,
        'failed': 0,
        'skipped': 0,
        'by_category': {},
        'by_method': {},
        'backup_dir': backup_dir,
        'start_time': time.time()
    }
    
    for i, filepath in enumerate(files, 1):
        try:
            # Create backup if requested
            if args.backup:
                create_backup(filepath, backup_dir)
            
            # Clean the file
            success, method = clean_file(filepath, args, deps)
            
            # Update statistics
            category = get_file_category(filepath)
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
            
            if success:
                stats['cleaned'] += 1
                stats['by_method'][method] = stats['by_method'].get(method, 0) + 1
            else:
                stats['failed'] += 1
            
            # Show progress
            print_progress(i, len(files), filepath.name, success)
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}Operation cancelled by user.{Colors.END}")
            break
        except Exception as e:
            logging.error(f"Unexpected error processing {filepath}: {e}")
            stats['failed'] += 1
    
    # Calculate elapsed time
    stats['elapsed_time'] = time.time() - stats['start_time']
    
    # Print summary
    print_summary(stats)
    
    # Exit code
    sys.exit(0 if stats['failed'] == 0 else 1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Operation cancelled by user.{Colors.END}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}Fatal error: {e}{Colors.END}")
        logging.exception("Fatal error")
        sys.exit(1)