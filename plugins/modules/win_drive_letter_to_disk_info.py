#!/usr/bin/python

DOCUMENTATION = r'''
---
module: win_drive_letter_to_disk_info
short_description: Get disk information for a Windows drive letter
description:
    - Retrieves disk information for a specified Windows drive letter
    - Returns disk space, free space, and other disk properties
    - Supports both local and network drives
    - Provides disk usage statistics in multiple units
version_added: "1.0.0"
options:
    drive_letter:
        description: Windows drive letter to query (e.g., 'C:', 'C', 'D:')
        required: true
        type: str
author:
    - DAI Development Team
notes:
    - This module is designed for Windows systems
    - Requires appropriate permissions to query disk information
    - Network drives may have limited information available
'''

EXAMPLES = r'''
- name: Get C: drive information
  dai_continuous_testing.utilities.win_drive_letter_to_disk_info:
    drive_letter: "C:"

- name: Get drive info without colon
  dai_continuous_testing.utilities.win_drive_letter_to_disk_info:
    drive_letter: "D"

- name: Check network drive
  dai_continuous_testing.utilities.win_drive_letter_to_disk_info:
    drive_letter: "Z:"
'''

RETURN = r'''
success:
    description: Whether the operation succeeded
    type: bool
    returned: always
msg:
    description: Result message
    type: str
    returned: always
drive_letter:
    description: The drive letter that was queried
    type: str
    returned: always
disk_info:
    description: Detailed disk information
    type: dict
    returned: on success
    contains:
        DriveLetter:
            description: Drive letter
            type: str
        Size:
            description: Total disk size in bytes
            type: int
        FreeSpace:
            description: Available free space in bytes
            type: int
        FileSystem:
            description: File system type (NTFS, FAT32, etc.)
            type: str
        DriveType:
            description: Drive type (3=Local, 4=Network, 5=CD-ROM, etc.)
            type: int
        VolumeLabel:
            description: Volume label/name
            type: str
        DiskNumber:
            description: Physical disk number
            type: int
        PartitionNumber:
            description: Partition number on the disk
            type: int
'''

import os
import re
import subprocess
import json

from ansible.module_utils.basic import AnsibleModule

def parse_drive_letter(drive_input):
    """Parse and validate drive letter input"""
    if not drive_input:
        raise ValueError("Drive letter cannot be empty")
    
    # Remove colon if present and convert to uppercase
    drive_letter = str(drive_input).rstrip(':').upper()
    
    # Validate single letter
    if len(drive_letter) != 1 or not drive_letter.isalpha():
        raise ValueError(f"Invalid drive letter: {drive_input}")
    
    return drive_letter

def get_disk_info(drive_letter):
    """Get disk information for a Windows drive letter using PowerShell"""
    try:
        parsed_drive = parse_drive_letter(drive_letter)
    except ValueError as e:
        return {
            'success': False,
            'msg': str(e),
            'drive_letter': drive_letter
        }
    
    # PowerShell command to get comprehensive disk information
    ps_command = f'''
    Get-WmiObject -Class Win32_LogicalDisk | Where-Object {{ $_.DeviceID -eq "{parsed_drive}:" }} | 
    ForEach-Object {{
        $disk = $_
        $partition = Get-WmiObject -Class Win32_LogicalDiskToPartition | Where-Object {{ $_.Dependent -match $disk.DeviceID }}
        $physicalDisk = $null
        if ($partition) {{
            $physicalDisk = Get-WmiObject -Class Win32_DiskPartition | Where-Object {{ $_.DeviceID -eq $partition.Antecedent.Split('=')[1].Trim('"') }}
        }}
        
        [PSCustomObject]@{{
            DriveLetter = $disk.DeviceID.Replace(':', '')
            Size = $disk.Size
            FreeSpace = $disk.FreeSpace
            FileSystem = $disk.FileSystem
            DriveType = $disk.DriveType
            DeviceID = $disk.DeviceID
            VolumeLabel = $disk.VolumeName
            DiskNumber = if ($physicalDisk) {{ $physicalDisk.DiskIndex }} else {{ $null }}
            PartitionNumber = if ($physicalDisk) {{ $physicalDisk.Index }} else {{ $null }}
            DiskSize = $disk.Size
            DiskModel = $null
            DiskInterface = $null
        }}
    }} | ConvertTo-Json
    '''
    
    try:
        result = subprocess.run(
            ['powershell.exe', '-Command', ps_command],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return {
                'success': False,
                'msg': f'PowerShell command failed: {result.stderr}',
                'drive_letter': parsed_drive
            }
        
        # Parse JSON output
        try:
            disk_data = json.loads(result.stdout.strip())
            if isinstance(disk_data, list):
                disk_data = disk_data[0] if disk_data else None
            
            if not disk_data:
                return {
                    'success': False,
                    'msg': f'Drive {parsed_drive}: not found',
                    'drive_letter': parsed_drive
                }
            
            return {
                'success': True,
                'msg': 'OK',
                'drive_letter': parsed_drive,
                'disk_info': disk_data
            }
            
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'msg': f'Failed to parse PowerShell output: {e}',
                'drive_letter': parsed_drive
            }
            
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'msg': 'PowerShell command timed out',
            'drive_letter': parsed_drive
        }
    except Exception as e:
        return {
            'success': False,
            'msg': f'Unexpected error: {e}',
            'drive_letter': parsed_drive
        }

def filter_not_none(item):
    return item is not None

def get_partition_by_letter(drive_letter):
    
    def f(disk):
        for partition in disk["partitions"]:

            actual_drive_letter = partition["drive_letter"] or ""
            expected_drive_letter = drive_letter or ""

            if actual_drive_letter.lower() == expected_drive_letter.lower():
                return partition

        return None

    return f

def get_free_space_in_partition(partition):
    return partition["volumes"][0]["size_remaining"]

def get_disk_space_in_partition(partition):
    return partition["volumes"][0]["size"]

def main():
    
    module_args = dict(
        disks=dict(type='list', required=True),
        drive_letter=dict(type='str', required=True)
    )
    
    module = AnsibleModule(
        argument_spec=module_args
    )

    result = {}

    disks = module.params["disks"]
    drive_letter = module.params["drive_letter"]

    matched_partitions = list(map(get_partition_by_letter(drive_letter), disks))
    filterred_matched_partitions = list(filter(filter_not_none, matched_partitions))

    if len(filterred_matched_partitions) == 0:
        result["disk_found"] = False
        module.fail_json("disk %s:\\ not found" % drive_letter, **result)
    
    elif len(filterred_matched_partitions) > 1:
        result["disk_found"] = False
        module.fail_json("more than one disk is found", **result)
    
    else:
        result["disk_found"] = True
        
        free_disk_space = get_free_space_in_partition(filterred_matched_partitions[0])
        total_disk_space = get_disk_space_in_partition(filterred_matched_partitions[0])

        result["free_disk_space"] = {
            "bytes": free_disk_space,
            "mib": round(free_disk_space / (1024 * 1024)),
            "gib": round(free_disk_space / (1024 * 1024 * 1024))
        }

        result["total_disk_space"] = {
            "bytes": total_disk_space,
            "mib": round(total_disk_space / (1024 * 1024)),
            "gib": round(total_disk_space / (1024 * 1024 * 1024))
        }

    module.exit_json(**result)

if __name__ == '__main__':
    main()
