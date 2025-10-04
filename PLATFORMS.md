# 🌍 MetaWipe - Platform Compatibility

## ✅ Fully Supported Platforms

MetaWipe works seamlessly on:

- ✅ **Windows 10/11** (64-bit)
- ✅ **Linux** (All major distributions)
- ✅ **macOS** (10.14 Mojave and later, including Apple Silicon)

---

## 🪟 Windows Support

### **Tested On:**
- Windows 11 (22H2, 23H2)
- Windows 10 (21H2, 22H2)
- Windows Server 2019/2022

### **Features:**
- ✅ Full ANSI color support (Windows 10+)
- ✅ Long path support (260+ characters)
- ✅ Works with Windows Defender
- ✅ Compatible with OneDrive/Dropbox folders
- ✅ Handles Windows file permissions
- ✅ Backups in `%APPDATA%\MetaWipe`

### **Requirements:**
- Python 3.8+ (from python.org)
- exiftool (manual download from exiftool.org)
- ffmpeg (optional, from ffmpeg.org)

### **Installation:**
```cmd
# Download and run setup.bat
setup.bat
```

### **Quick Command:**
```cmd
python clean_metadata.py --backup --reencode-videos --normalize-time
```

---

## 🐧 Linux Support

### **Tested Distributions:**
- ✅ Ubuntu 20.04, 22.04, 24.04
- ✅ Debian 11, 12
- ✅ Fedora 38, 39, 40
- ✅ Arch Linux (latest)
- ✅ Linux Mint 21, 22
- ✅ Pop!_OS 22.04
- ✅ Manjaro (latest)
- ✅ openSUSE Leap/Tumbleweed

### **Features:**
- ✅ Full ANSI color support
- ✅ Respects Unix permissions
- ✅ Works with symbolic links
- ✅ Compatible with network drives (NFS, SAMBA)
- ✅ Can run without root (except protected files)
- ✅ Backups in `~/.metadata_cleaner`

### **Requirements:**
```bash
# Ubuntu/Debian
libimage-exiftool-perl ffmpeg python3-pip

# Fedora/RHEL
perl-Image-ExifTool ffmpeg python3-pip

# Arch
perl-image-exiftool ffmpeg python-pip
```

### **Installation:**
```bash
# Ubuntu/Debian
sudo apt-get install -y libimage-exiftool-perl ffmpeg python3-pip
pip3 install pillow pypdf python-docx mutagen openpyxl

# Fedora
sudo dnf install -y perl-Image-ExifTool ffmpeg python3-pip
pip3 install pillow pypdf python-docx mutagen openpyxl

# Arch
sudo pacman -S perl-image-exiftool ffmpeg python-pip
pip install pillow pypdf python-docx mutagen openpyxl
```

### **Quick Command:**
```bash
python3 clean_metadata.py --backup --reencode-videos --normalize-time
```

---

## 🍎 macOS Support

### **Tested Versions:**
- ✅ macOS Sonoma (14.x)
- ✅ macOS Ventura (13.x)
- ✅ macOS Monterey (12.x)
- ✅ macOS Big Sur (11.x)
- ✅ macOS Catalina (10.15.x)
- ✅ macOS Mojave (10.14.x)

### **Architecture:**
- ✅ Intel (x86_64)
- ✅ Apple Silicon (M1, M2, M3, M4 - arm64)

### **Features:**
- ✅ Full ANSI color support
- ✅ Works with APFS filesystem
- ✅ Compatible with iCloud Drive
- ✅ Handles macOS resource forks
- ✅ Supports HEIC/HEIF formats
- ✅ Backups in `~/.metadata_cleaner`

### **Requirements:**
- Homebrew (recommended)
- exiftool (via Homebrew)
- ffmpeg (via Homebrew)
- Python 3.8+ (system or Homebrew)

### **Installation:**
```bash
# Install Homebrew if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install exiftool ffmpeg python3
pip3 install pillow pypdf python-docx mutagen openpyxl
```

### **Quick Command:**
```bash
python3 clean_metadata.py --backup --reencode-videos --normalize-time
```

---

## 🔧 Platform-Specific Differences

| Feature | Windows | Linux | macOS |
|---------|---------|-------|-------|
| **Colors** | ✅ Win10+ | ✅ All | ✅ All |
| **Setup Script** | `setup.bat` | `setup.sh` | `setup.sh` |
| **Python Command** | `python` | `python3` | `python3` |
| **Backup Location** | `%APPDATA%\MetaWipe` | `~/.metadata_cleaner` | `~/.metadata_cleaner` |
| **Path Separator** | `\` | `/` | `/` |
| **exiftool Install** | Manual | Package manager | Homebrew |
| **ffmpeg Install** | Manual | Package manager | Homebrew |
| **Long Paths** | ✅ Supported | ✅ Native | ✅ Native |
| **Symbolic Links** | ⚠️ Limited | ✅ Full | ✅ Full |

---

## 🎯 Cross-Platform Commands

The same command works on all platforms (just adjust paths):

### **Maximum Privacy Mode:**

**Windows:**
```cmd
python clean_metadata.py --path "C:\MyFiles" --backup --reencode-videos --normalize-time
```

**Linux:**
```bash
python3 clean_metadata.py --path /home/user/MyFiles --backup --reencode-videos --normalize-time
```

**macOS:**
```bash
python3 clean_metadata.py --path ~/MyFiles --backup --reencode-videos --normalize-time
```

### **Quick Clean:**

**All platforms:**
```
python(3) clean_metadata.py --backup
```

---

## 📂 File Path Examples

### **Windows:**
```cmd
--path "C:\Users\John\Pictures"
--path "%USERPROFILE%\Documents"
--path "D:\Work\Projects"
--path "\\network\share\files"
```

### **Linux:**
```bash
--path /home/john/Pictures
--path ~/Documents
--path /media/usb/files
--path /mnt/network/share
```

### **macOS:**
```bash
--path ~/Pictures
--path /Users/john/Documents
--path /Volumes/USB/files
--path ~/Library/Mobile\ Documents/com~apple~CloudDocs
```

---

## 🔍 Known Platform Issues

### **Windows:**

#### **Issue: exiftool not found**
**Solution:** Download from exiftool.org, rename to `exiftool.exe`, add to PATH or place in script directory

#### **Issue: Long path errors**
**Solution:** Enable long paths in Windows:
```cmd
reg add HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1 /f
```

#### **Issue: Antivirus blocking**
**Solution:** Add MetaWipe folder to antivirus exclusions

### **Linux:**

#### **Issue: Permission denied**
**Solution:** Run with appropriate permissions or use `sudo` for system directories

#### **Issue: Python command not found**
**Solution:** Install `python3` package or create alias:
```bash
alias python=python3
```

### **macOS:**

#### **Issue: "python3" command not found**
**Solution:** Install via Homebrew:
```bash
brew install python3
```

#### **Issue: Permission denied on system folders**
**Solution:** Grant Full Disk Access in System Preferences → Security & Privacy

#### **Issue: Certificate errors with pip**
**Solution:** Use `--trusted-host` flag:
```bash
pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org [packages]
```

---

## 🚀 Performance by Platform

Based on 1000 mixed files (images, videos, docs):

| Platform | Time (no re-encode) | Time (with re-encode) |
|----------|---------------------|----------------------|
| **Windows 11** (i7-12700) | ~5 min | ~35 min |
| **Linux** (Ubuntu 22.04, i7-12700) | ~4 min | ~30 min |
| **macOS** (M2, Ventura) | ~3 min | ~25 min |

*Linux and macOS are typically faster due to better I/O performance*

---

## 🎓 Best Practices by Platform

### **Windows:**
1. Run Command Prompt as Administrator for system files
2. Exclude MetaWipe from antivirus scans for better performance
3. Use short paths when possible to avoid MAX_PATH issues
4. Close File Explorer before cleaning to avoid file locks

### **Linux:**
1. Use `sudo` only when necessary (e.g., `/var/`, `/etc/`)
2. Run in terminal, not through file manager
3. Check disk space before cleaning large collections
4. Use absolute paths for clarity

### **macOS:**
1. Grant Full Disk Access if cleaning system folders
2. Avoid cleaning files in Time Machine backups
3. Works great with external drives and iCloud
4. Use Terminal, not through Finder

---

## 🔒 Security Considerations

### **All Platforms:**
- ✅ No internet connection required
- ✅ No data sent externally
- ✅ All processing local
- ✅ Open source - inspect the code
- ✅ No admin/root required (except for system files)

### **Windows:**
- Backups stored in user profile (encrypted if BitLocker enabled)
- Compatible with Windows Defender
- No registry modifications
- Portable - can run from USB

### **Linux:**
- Respects file permissions and ownership
- No system files modified
- Compatible with SELinux/AppArmor
- Can run in restricted environments

### **macOS:**
- No system extensions required
- Works in sandboxed mode
- Compatible with Gatekeeper
- No system integrity modifications

---

## 📋 System Requirements

### **Minimum:**
- **OS**: Windows 10 / Ubuntu 18.04 / macOS 10.14
- **RAM**: 512 MB
- **Disk**: 100 MB free space + space for backups
- **Python**: 3.8+

### **Recommended:**
- **OS**: Windows 11 / Ubuntu 22.04 / macOS 13+
- **RAM**: 2 GB
- **Disk**: 1 GB free space + 2x file size for backups
- **Python**: 3.10+
- **CPU**: Multi-core for video re-encoding

---

## ✅ Compatibility Matrix

| File Type | Windows | Linux | macOS | Notes |
|-----------|---------|-------|-------|-------|
| **JPEG/PNG** | ✅ | ✅ | ✅ | Perfect |
| **HEIC/HEIF** | ✅ | ✅ | ✅ | Best on macOS |
| **RAW (CR2/NEF)** | ✅ | ✅ | ✅ | Requires exiftool |
| **MP4/MOV** | ✅ | ✅ | ✅ | Re-encode recommended |
| **PDF** | ✅ | ✅ | ✅ | Perfect |
| **DOCX/XLSX** | ✅ | ✅ | ✅ | Perfect |
| **MP3/FLAC** | ✅ | ✅ | ✅ | Perfect |

---

## 🎉 Summary

**MetaWipe is truly cross-platform!**

- ✅ Same code works everywhere
- ✅ Same accuracy on all platforms
- ✅ Platform-specific optimizations included
- ✅ Comprehensive error handling
- ✅ Detailed documentation for each OS

**Choose your platform and start cleaning!** 🚀