"""
VoterManager class for handling voter registration and voting status tracking.
"""

from typing import Set, List, Dict, Any


class VoterManager:
    """
    Manages voter registration and tracks voting status.
    
    Handles voter registration with uniqueness checking and maintains
    voting status to enforce one-vote-per-voter policy.
    """
    
    def __init__(self):
        """Initialize VoterManager with empty voter sets."""
        self._registered_voters: Set[str] = set()
        self._voted_voters: Set[str] = set()
    
    def register_voter(self, voter_id: str) -> bool:
        """
        Register a new voter with unique ID validation.
        
        Args:
            voter_id: Unique identifier for the voter
            
        Returns:
            True if registration successful, False if voter already registered
            
        Raises:
            ValueError: If voter_id is invalid (empty or not string)
        """
        if not voter_id or not isinstance(voter_id, str):
            raise ValueError("voter_id must be a non-empty string")
        
        if voter_id in self._registered_voters:
            return False
        
        self._registered_voters.add(voter_id)
        return True
    
    def is_registered(self, voter_id: str) -> bool:
        """
        Check if a voter is registered.
        
        Args:
            voter_id: Voter ID to check
            
        Returns:
            True if voter is registered, False otherwise
        """
        if not voter_id or not isinstance(voter_id, str):
            return False
        
        return voter_id in self._registered_voters
    
    def has_voted(self, voter_id: str) -> bool:
        """
        Check if a registered voter has already voted.
        
        Args:
            voter_id: Voter ID to check
            
        Returns:
            True if voter has voted, False otherwise
        """
        if not voter_id or not isinstance(voter_id, str):
            return False
        
        return voter_id in self._voted_voters
    
    def mark_as_voted(self, voter_id: str) -> None:
        """
        Mark a voter as having voted.
        
        Args:
            voter_id: Voter ID to mark as voted
            
        Raises:
            ValueError: If voter_id is invalid or voter is not registered
        """
        if not voter_id or not isinstance(voter_id, str):
            raise ValueError("voter_id must be a non-empty string")
        
        if voter_id not in self._registered_voters:
            raise ValueError("Voter must be registered before marking as voted")
        
        self._voted_voters.add(voter_id)
    
    def get_registered_voters(self) -> List[str]:
        """
        Get list of all registered voter IDs.
        
        Returns:
            List of registered voter IDs (sorted for consistency)
        """
        return sorted(list(self._registered_voters))
    
    def get_voted_voters(self) -> List[str]:
        """
        Get list of all voters who have voted.
        
        Returns:
            List of voter IDs who have voted (sorted for consistency)
        """
        return sorted(list(self._voted_voters))
    
    def get_registration_count(self) -> int:
        """
        Get total number of registered voters.
        
        Returns:
            Number of registered voters
        """
        return len(self._registered_voters)
    
    def get_voted_count(self) -> int:
        """
        Get total number of voters who have voted.
        
        Returns:
            Number of voters who have voted
        """
        return len(self._voted_voters)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert VoterManager state to dictionary for serialization.
        
        Returns:
            Dictionary representation of voter manager state
        """
        return {
            'registered_voters': list(self._registered_voters),
            'voted_voters': list(self._voted_voters)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VoterManager':
        """
        Create VoterManager instance from dictionary.
        
        Args:
            data: Dictionary containing voter manager state
            
        Returns:
            VoterManager instance
            
        Raises:
            KeyError: If required keys are missing
            ValueError: If data is invalid
        """
        required_keys = {'registered_voters', 'voted_voters'}
        if not all(key in data for key in required_keys):
            missing = required_keys - set(data.keys())
            raise KeyError(f"Missing required keys: {missing}")
        
        voter_manager = cls()
        
        # Validate and set registered voters
        registered = data['registered_voters']
        if not isinstance(registered, list):
            raise ValueError("registered_voters must be a list")
        
        for voter_id in registered:
            if not isinstance(voter_id, str) or not voter_id:
                raise ValueError("All voter IDs must be non-empty strings")
            voter_manager._registered_voters.add(voter_id)
        
        # Validate and set voted voters
        voted = data['voted_voters']
        if not isinstance(voted, list):
            raise ValueError("voted_voters must be a list")
        
        for voter_id in voted:
            if not isinstance(voter_id, str) or not voter_id:
                raise ValueError("All voter IDs must be non-empty strings")
            if voter_id not in voter_manager._registered_voters:
                raise ValueError(f"Voted voter {voter_id} must be registered")
            voter_manager._voted_voters.add(voter_id)
        
        return voter_manager
    
    def clear(self) -> None:
        """
        Clear all voter data (for testing purposes).
        """
        self._registered_voters.clear()
        self._voted_voters.clear()