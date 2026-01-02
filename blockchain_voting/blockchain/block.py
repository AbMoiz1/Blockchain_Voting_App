"""
Block data class for representing blocks in the blockchain.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
import hashlib
import json
import time
from blockchain_voting.voting.vote import Vote


@dataclass
class Block:
    """
    Represents a single block in the blockchain.
    
    Attributes:
        index: Position of the block in the chain
        timestamp: Unix timestamp when the block was created
        votes: List of votes contained in this block
        previous_hash: Hash of the previous block in the chain
        hash: SHA-256 hash of this block's data
    """
    index: int
    timestamp: float
    votes: List[Vote]
    previous_hash: str
    hash: str = ""
    
    def __post_init__(self):
        """Calculate hash if not provided and validate block data."""
        if not isinstance(self.index, int) or self.index < 0:
            raise ValueError("index must be a non-negative integer")
        if not isinstance(self.timestamp, (int, float)) or self.timestamp <= 0:
            raise ValueError("timestamp must be a positive number")
        if not isinstance(self.votes, list):
            raise ValueError("votes must be a list")
        if not isinstance(self.previous_hash, str):
            raise ValueError("previous_hash must be a string")
        
        # Validate all votes
        for vote in self.votes:
            if not isinstance(vote, Vote):
                raise ValueError("All items in votes must be Vote instances")
        
        # Calculate hash if not provided
        if not self.hash:
            self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """
        Calculate SHA-256 hash of the block data.
        
        Returns:
            Hexadecimal string representation of the hash
        """
        # Create a consistent string representation of block data
        block_data = {
            'index': self.index,
            'timestamp': self.timestamp,
            'votes': [vote.to_dict() for vote in self.votes],
            'previous_hash': self.previous_hash
        }
        
        # Convert to JSON string with sorted keys for consistency
        block_string = json.dumps(block_data, sort_keys=True, separators=(',', ':'))
        
        # Calculate SHA-256 hash
        return hashlib.sha256(block_string.encode('utf-8')).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert block to dictionary for serialization.
        
        Returns:
            Dictionary representation of the block
        """
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'votes': [vote.to_dict() for vote in self.votes],
            'previous_hash': self.previous_hash,
            'hash': self.hash
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Block':
        """
        Create Block instance from dictionary.
        
        Args:
            data: Dictionary containing block data
            
        Returns:
            Block instance
            
        Raises:
            KeyError: If required keys are missing
            ValueError: If data is invalid
        """
        required_keys = {'index', 'timestamp', 'votes', 'previous_hash', 'hash'}
        if not all(key in data for key in required_keys):
            missing = required_keys - set(data.keys())
            raise KeyError(f"Missing required keys: {missing}")
        
        # Convert vote dictionaries back to Vote objects
        votes = [Vote.from_dict(vote_data) for vote_data in data['votes']]
        
        return cls(
            index=data['index'],
            timestamp=data['timestamp'],
            votes=votes,
            previous_hash=data['previous_hash'],
            hash=data['hash']
        )
    
    @classmethod
    def create_block(cls, index: int, votes: List[Vote], previous_hash: str) -> 'Block':
        """
        Create a new block with current timestamp.
        
        Args:
            index: Position of the block in the chain
            votes: List of votes to include in the block
            previous_hash: Hash of the previous block
            
        Returns:
            New Block instance with calculated hash
        """
        return cls(
            index=index,
            timestamp=time.time(),
            votes=votes,
            previous_hash=previous_hash
        )
    
    def validate_hash(self) -> bool:
        """
        Validate that the stored hash matches the calculated hash.
        
        Returns:
            True if hash is valid, False otherwise
        """
        return self.hash == self.calculate_hash()