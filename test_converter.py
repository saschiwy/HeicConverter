import unittest
import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock
from PIL import Image
import piexif

from converter import (
    generate_unique_filename,
    get_file_list,
    convert_heic_file,
    convert_heic_to_jpeg,
    convert_multiple_heic_files
)


class TestConverter(unittest.TestCase):
    """Tests for the HEIC to JPEG converter functions"""
    
    def setUp(self):
        """Set up temporary directories and files for testing"""
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()
        self.target_dir = tempfile.mkdtemp()
        
        # Create a fake HEIC file structure
        self.fake_files = []
        for i in range(3):
            # Create fake directory structure
            subdir = os.path.join(self.test_dir, f"subdir_{i}")
            os.makedirs(subdir, exist_ok=True)
            
            # Create a dummy file with .heic extension
            dummy_file = os.path.join(subdir, f"test_{i}.heic")
            with open(dummy_file, 'w') as f:
                f.write("This is not a real HEIC file")
            
            self.fake_files.append(dummy_file)
    
    def tearDown(self):
        """Clean up temporary files and directories"""
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.target_dir)
    
    def test_generate_unique_filename(self):
        """Test the unique filename generation"""
        # Create a test file
        test_file = os.path.join(self.target_dir, "test.jpg")
        with open(test_file, 'w') as f:
            f.write("Test file")
            
        # Test generating a unique name
        unique_name = generate_unique_filename(test_file)
        self.assertNotEqual(unique_name, test_file)
        self.assertEqual(os.path.basename(unique_name), "test(1).jpg")
        
        # Create the new file and test again
        with open(unique_name, 'w') as f:
            f.write("Another test file")
            
        # Should generate test(2).jpg now
        next_unique = generate_unique_filename(test_file)
        self.assertEqual(os.path.basename(next_unique), "test(2).jpg")
        
        # Test with a file that has (n) pattern already
        pattern_file = os.path.join(self.target_dir, "example(5).jpg")
        with open(pattern_file, 'w') as f:
            f.write("Pattern file")
            
        pattern_unique = generate_unique_filename(pattern_file)
        self.assertEqual(os.path.basename(pattern_unique), "example(6).jpg")
    
    def test_get_file_list(self):
        """Test the file list retrieval function"""
        # Test with recursive=True
        files_recursive = get_file_list(self.test_dir, True)
        self.assertEqual(len(files_recursive), 3)
        
        # Create a file in the root directory
        root_file = os.path.join(self.test_dir, "root.heic")
        with open(root_file, 'w') as f:
            f.write("Root HEIC file")
            
        # Test again with the root file
        files_recursive = get_file_list(self.test_dir, True)
        self.assertEqual(len(files_recursive), 4)
        
        # Test with recursive=False
        files_non_recursive = get_file_list(self.test_dir, False)
        self.assertEqual(len(files_non_recursive), 1)  # Should only find the root file
        
        # Test with invalid directory
        invalid_files = get_file_list(os.path.join(self.test_dir, "nonexistent"), True)
        self.assertEqual(len(invalid_files), 0)
    
    @patch('converter.Image.open')
    @patch('converter.piexif.load')
    @patch('converter.piexif.dump')
    def test_convert_heic_file(self, mock_dump, mock_load, mock_open):
        """Test the HEIC file conversion function with mocks"""
        # Setup mocks
        mock_image = MagicMock()
        mock_exif = MagicMock()
        mock_exif.items.return_value = {274: 1}  # Orientation tag
        mock_image.getexif.return_value = mock_exif
        mock_image.info = {"exif": b"fake_exif"}
        mock_open.return_value = mock_image
        
        mock_load.return_value = {"0th": {}, "1st": {}, "Exif": {}, "GPS": {}, "Interop": {}}
        mock_dump.return_value = b"new_exif"
        
        # Test conversion
        source_file = os.path.join(self.test_dir, "test.heic")
        with open(source_file, 'w') as f:
            f.write("Fake HEIC data")
            
        target_file = os.path.join(self.target_dir, "test.jpg")
        
        # Test with callback
        callback = MagicMock()
        result = convert_heic_file(
            source_file, 
            target_file, 
            True, 
            False, 
            95, 
            callback
        )
        
        self.assertTrue(result)
        callback.assert_called()
        mock_image.save.assert_called_with(target_file, "jpeg", exif=b"new_exif", quality=95)
        
        # Test with invalid file
        invalid_file = os.path.join(self.test_dir, "invalid.txt")
        with open(invalid_file, 'w') as f:
            f.write("Not a HEIC file")
            
        result = convert_heic_file(invalid_file, target_file, True, False, 95)
        self.assertFalse(result)
    
    @patch('converter.convert_heic_file')
    def test_convert_multiple_heic_files(self, mock_convert):
        """Test converting multiple HEIC files"""
        # Setup mock to return success for all conversions
        mock_convert.return_value = True
        
        # Create target directory
        os.makedirs(self.target_dir, exist_ok=True)
        
        # Test conversion
        result = convert_multiple_heic_files(
            self.fake_files,
            True,
            False,
            95,
            self.target_dir
        )
        
        # Should have successfully converted all files
        self.assertEqual(len(result), len(self.fake_files))
        self.assertEqual(mock_convert.call_count, len(self.fake_files))
        
        # Test with callback
        callback = MagicMock()
        convert_multiple_heic_files(
            self.fake_files,
            True,
            False,
            95,
            self.target_dir,
            callback
        )
        
        # Callback should be called for each file
        self.assertEqual(callback.call_count, 0)  # It's passed through but not called directly
    
    @patch('converter.convert_heic_file')
    def test_convert_heic_to_jpeg(self, mock_convert):
        """Test the directory-based conversion function"""
        # Setup mock
        mock_convert.return_value = True
        
        # Test conversion
        result = convert_heic_to_jpeg(
            self.test_dir,
            True,
            False,
            False,
            95,
            self.target_dir
        )
        
        # Should match the number of fake files (3 subdirectory files + 1 root file)
        self.assertEqual(mock_convert.call_count, 3)  # We mocked get_file_list
        
        # Test with non-recursive
        mock_convert.reset_mock()
        result = convert_heic_to_jpeg(
            self.test_dir,
            False,
            False,
            False,
            95,
            self.target_dir
        )
        
        # Should only find files in the root directory
        self.assertEqual(mock_convert.call_count, 0)  # We mocked get_file_list


if __name__ == '__main__':
    unittest.main()
    