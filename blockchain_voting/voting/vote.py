"""
Vote data class for representing individual votes in the blockchain voting system.
"""

from dataclasses import dataclass
from typing import Dict, Any
import time


@dataclass
class Vote:
    """
    Represents a single vote cast by a voter.
    
    Attributes:
        voter_id: Unique identifier for the voter
        candidate: The candidate or option being voted for
        timestamp: Unix timestamp when the vote was cast
    """
    voter_id: str
    candidate: str
    timestamp: float
    
    def __post_init__(self):
        """Validate vote data after initialization."""
        if not self.voter_id or not isinstance(self.voter_id, str):
            raise ValueError("voter_id must be a non-empty string")
        if not self.candidate or not isinstance(self.candidate, str):
            raise ValueError("candidate must be a non-empty string")
        if not isinstance(self.timestamp, (int, float)) or self.timestamp <= 0:
            raise ValueError("timestamp must be a positive number")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert vote to dictionary for serialization.
        
        Returns:
            Dictionary representation of the vote
        """
        return {
            'voter_id': self.voter_id,
            'candidate': self.candidate,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Vote':
        """
        Create Vote instance from dictionary.
        
        Args:
            data: Dictionary containing vote data
            
        Returns:
            Vote instance
            
        Raises:
            KeyError: If required keys are missing
            ValueError: If data is invalid
        """
        required_keys = {'voter_id', 'candidate', 'timestamp'}
        if not all(key in data for key in required_keys):
            missing = required_keys - set(data.keys())
            raise KeyError(f"Missing required keys: {missing}")
        
        return cls(
            voter_id=data['voter_id'],
            candidate=data['candidate'],
            timestamp=data['timestamp']
        )
    
    @classmethod
    def create_vote(cls, voter_id: str, candidate: str) -> 'Vote':
        """
        Create a new vote with current timestamp.
        
        Args:
            voter_id: Unique identifier for the voter
            candidate: The candidate being voted for
            
        Returns:
            New Vote instance with current timestamp
        """
        return cls(
            voter_id=voter_id,
            candidate=candidate,
            timestamp=time.time()
        )