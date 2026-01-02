"""
Unit tests for Block class.
"""

import unittest
import time
from blockchain_voting.blockchain.block import Block
from blockchain_voting.voting.vote import Vote


class TestBlock(unittest.TestCase):
    """Test cases for Block class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.valid_index = 1
        self.valid_timestamp = time.time()
        self.valid_votes = [
            Vote("voter1", "Alice", time.time()),
            Vote("voter2", "Bob", time.time())
        ]
        self.valid_previous_hash = "0" * 64  # 64-character hex string
    
    def test_block_creation(self):
        """Test creating a valid block."""
        block = Block(
            self.valid_index,
            self.valid_timestamp,
            self.valid_votes,
            self.valid_previous_hash
        )
        
        self.assertEqual(block.index, self.valid_index)
        self.assertEqual(block.timestamp, self.valid_timestamp)
        self.assertEqual(block.votes, self.valid_votes)
        self.assertEqual(block.previous_hash, self.valid_previous_hash)
        self.assertTrue(len(block.hash) == 64)  # SHA-256 produces 64-char hex
    
    def test_block_validation_negative_index(self):
        """Test block creation with negative index raises ValueError."""
        with self.assertRaises(ValueError):
            Block(-1, self.valid_timestamp, self.valid_votes, self.valid_previous_hash)
    
    def test_block_validation_invalid_timestamp(self):
        """Test block creation with invalid timestamp raises ValueError."""
        with self.assertRaises(ValueError):
            Block(self.valid_index, -1, self.valid_votes, self.valid_previous_hash)
    
    def test_block_validation_invalid_votes(self):
        """Test block creation with invalid votes raises ValueError."""
        with self.assertRaises(ValueError):
            Block(self.valid_index, self.valid_timestamp, "not a list", self.valid_previous_hash)
    
    def test_calculate_hash_consistency(self):
        """Test that hash calculation is consistent."""
        block = Block(
            self.valid_index,
            self.valid_timestamp,
            self.valid_votes,
            self.valid_previous_hash
        )
        
        hash1 = block.calculate_hash()
        hash2 = block.calculate_hash()
        
        self.assertEqual(hash1, hash2)
        self.assertEqual(hash1, block.hash)
    
    def test_to_dict(self):
        """Test block serialization to dictionary."""
        block = Block(
            self.valid_index,
            self.valid_timestamp,
            self.valid_votes,
            self.valid_previous_hash
        )
        block_dict = block.to_dict()
        
        self.assertEqual(block_dict['index'], self.valid_index)
        self.assertEqual(block_dict['timestamp'], self.valid_timestamp)
        self.assertEqual(block_dict['previous_hash'], self.valid_previous_hash)
        self.assertEqual(block_dict['hash'], block.hash)
        self.assertEqual(len(block_dict['votes']), len(self.valid_votes))
    
    def test_from_dict(self):
        """Test block deserialization from dictionary."""
        original_block = Block(
            self.valid_index,
            self.valid_timestamp,
            self.valid_votes,
            self.valid_previous_hash
        )
        block_dict = original_block.to_dict()
        reconstructed_block = Block.from_dict(block_dict)
        
        self.assertEqual(reconstructed_block.index, original_block.index)
        self.assertEqual(reconstructed_block.timestamp, original_block.timestamp)
        self.assertEqual(reconstructed_block.previous_hash, original_block.previous_hash)
        self.assertEqual(reconstructed_block.hash, original_block.hash)
        self.assertEqual(len(reconstructed_block.votes), len(original_block.votes))
    
    def test_create_block(self):
        """Test creating block with current timestamp."""
        before_time = time.time()
        block = Block.create_block(self.valid_index, self.valid_votes, self.valid_previous_hash)
        after_time = time.time()
        
        self.assertEqual(block.index, self.valid_index)
        self.assertEqual(block.votes, self.valid_votes)
        self.assertEqual(block.previous_hash, self.valid_previous_hash)
        self.assertGreaterEqual(block.timestamp, before_time)
        self.assertLessEqual(block.timestamp, after_time)
    
    def test_validate_hash(self):
        """Test hash validation."""
        block = Block(
            self.valid_index,
            self.valid_timestamp,
            self.valid_votes,
            self.valid_previous_hash
        )
        
        # Valid hash should pass validation
        self.assertTrue(block.validate_hash())
        
        # Corrupted hash should fail validation
        block.hash = "invalid_hash"
        self.assertFalse(block.validate_hash())


if __name__ == '__main__':
    unittest.main()