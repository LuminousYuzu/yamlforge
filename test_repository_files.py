#!/usr/bin/env python3
"""
Test script to check what files are in your repository
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from yaml_parser.bitbucket_reader import BitbucketYAMLReader

def test_repository_files():
    """Test what files are in your repository"""
    
    # Replace with your actual access token
    access_token = "YOUR_ACCESS_TOKEN_HERE"  # You'll need to provide this
    workspace = "kyleswe"
    repository = "yaml_test"
    
    print(f"🔍 Checking files in {workspace}/{repository}")
    print("=" * 50)
    
    try:
        reader = BitbucketYAMLReader(access_token, workspace, repository)
        
        # List all files
        yaml_files = reader.list_yaml_files()
        
        print(f"\n✅ Found {len(yaml_files)} YAML files:")
        for file_path in yaml_files:
            print(f"   • {file_path}")
            
            # Try to get content
            content = reader.get_file_content(file_path)
            if content:
                print(f"     ✅ Successfully retrieved content ({len(content)} characters)")
                
                # Try to parse
                parsed_data = reader.parse_yaml_content(content)
                if parsed_data:
                    print(f"     ✅ Successfully parsed YAML")
                else:
                    print(f"     ❌ Failed to parse YAML")
            else:
                print(f"     ❌ Failed to retrieve content")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure to:")
        print("1. Replace 'YOUR_ACCESS_TOKEN_HERE' with your actual Bitbucket access token")
        print("2. Verify the workspace and repository names are correct")
        print("3. Check that your access token has read permissions for the repository")

if __name__ == "__main__":
    test_repository_files() 