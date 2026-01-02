"""
Unit tests for VoterManager class.
"""

import unittest
from hypothesis import given, strategies as st
from blockchain_voting.voting import VoterManager


class TestVoterManager(unittest.TestCase):
    """Test cases for VoterManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.voter_manager = VoterManager()
    
    def test_register_voter_success(self):
        """Test successful voter registration."""
        result = self.voter_manager.register_voter("voter1")
        self.assertTrue(result)
        self.assertTrue(self.voter_manager.is_registered("voter1"))
    
    def test_register_voter_duplicate(self):
        """Test duplicate voter registration is rejected."""
        self.voter_manager.register_voter("voter1")
        result = self.voter_manager.register_voter("voter1")
        self.assertFalse(result)
        self.assertEqual(self.voter_manager.get_registration_count(), 1)
    
    def test_register_voter_invalid_id(self):
        """Test registration with invalid voter ID."""
        with self.assertRaises(ValueError):
            self.voter_manager.register_voter("")
        
        with self.assertRaises(ValueError):
            self.voter_manager.register_voter(None)
    
    def test_is_registered(self):
        """Test voter registration checking."""
        self.assertFalse(self.voter_manager.is_registered("voter1"))
        self.voter_manager.register_voter("voter1")
        self.assertTrue(self.voter_manager.is_registered("voter1"))
    
    def test_voting_status_tracking(self):
        """Test voting status tracking."""
        self.voter_manager.register_voter("voter1")
        
        # Initially not voted
        self.assertFalse(self.voter_manager.has_voted("voter1"))
        
        # Mark as voted
        self.voter_manager.mark_as_voted("voter1")
        self.assertTrue(self.voter_manager.has_voted("voter1"))
    
    def test_mark_as_voted_unregistered(self):
        """Test marking unregistered voter as voted raises error."""
        with self.assertRaises(ValueError):
            self.voter_manager.mark_as_voted("unregistered")
    
    def test_get_registered_voters(self):
        """Test getting list of registered voters."""
        voters = ["voter1", "voter2", "voter3"]
        for voter in voters:
            self.voter_manager.register_voter(voter)
        
        registered = self.voter_manager.get_registered_voters()
        self.assertEqual(set(registered), set(voters))
        self.assertEqual(len(registered), 3)
    
    def test_get_voted_voters(self):
        """Test getting list of voters who have voted."""
        self.voter_manager.register_voter("voter1")
        self.voter_manager.register_voter("voter2")
        self.voter_manager.mark_as_voted("voter1")
        
        voted = self.voter_manager.get_voted_voters()
        self.assertEqual(voted, ["voter1"])
    
    def test_serialization(self):
        """Test to_dict and from_dict methods."""
        # Set up some data
        self.voter_manager.register_voter("voter1")
        self.voter_manager.register_voter("voter2")
        self.voter_manager.mark_as_voted("voter1")
        
        # Serialize
        data = self.voter_manager.to_dict()
        
        # Deserialize
        new_manager = VoterManager.from_dict(data)
        
        # Verify state is preserved
        self.assertEqual(
            set(new_manager.get_registered_voters()),
            set(self.voter_manager.get_registered_voters())
        )
        self.assertEqual(
            set(new_manager.get_voted_voters()),
            set(self.voter_manager.get_voted_voters())
        )
    
    def test_from_dict_invalid_data(self):
        """Test from_dict with invalid data."""
        # Missing keys
        with self.assertRaises(KeyError):
            VoterManager.from_dict({"registered_voters": []})
        
        # Invalid voted voter (not registered)
        with self.assertRaises(ValueError):
            VoterManager.from_dict({
                "registered_voters": ["voter1"],
                "voted_voters": ["voter2"]  # voter2 not registered
            })
    
    @given(
        voter_id=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc', 'Pd'))),
        additional_voter_ids=st.lists(
            st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc', 'Pd'))),
            min_size=0,
            max_size=10
        )
    )
    def test_voter_registration_uniqueness_property_1(self, voter_id, additional_voter_ids):
        """
        Property 1: Voter Registration Uniqueness
        Feature: blockchain-voting, Property 1: Voter Registration Uniqueness
        Validates: Requirements 1.1, 1.2
        
        For any voter ID, registering it should succeed if and only if it hasn't been 
        registered before, and attempting to register a duplicate should leave the 
        system state unchanged.
        """
        voter_manager = VoterManager()
        
        # Test 1: First registration should succeed
        initial_count = voter_manager.get_registration_count()
        result = voter_manager.register_voter(voter_id)
        
        self.assertTrue(result, "First registration of any voter ID should succeed")
        self.assertTrue(voter_manager.is_registered(voter_id), "Voter should be registered after successful registration")
        self.assertEqual(voter_manager.get_registration_count(), initial_count + 1, 
                        "Registration count should increase by 1 after successful registration")
        
        # Test 2: Duplicate registration should fail and leave state unchanged
        pre_duplicate_count = voter_manager.get_registration_count()
        pre_duplicate_voters = set(voter_manager.get_registered_voters())
        
        duplicate_result = voter_manager.register_voter(voter_id)
        
        self.assertFalse(duplicate_result, "Duplicate registration should fail")
        self.assertTrue(voter_manager.is_registered(voter_id), "Voter should still be registered after duplicate attempt")
        self.assertEqual(voter_manager.get_registration_count(), pre_duplicate_count,
                        "Registration count should remain unchanged after duplicate attempt")
        self.assertEqual(set(voter_manager.get_registered_voters()), pre_duplicate_voters,
                        "Registered voters list should remain unchanged after duplicate attempt")
        
        # Test 3: Multiple duplicate attempts should all fail
        for _ in range(3):
            pre_attempt_count = voter_manager.get_registration_count()
            pre_attempt_voters = set(voter_manager.get_registered_voters())
            
            duplicate_result = voter_manager.register_voter(voter_id)
            
            self.assertFalse(duplicate_result, "Multiple duplicate registrations should all fail")
            self.assertEqual(voter_manager.get_registration_count(), pre_attempt_count,
                            "Registration count should remain unchanged after multiple duplicate attempts")
            self.assertEqual(set(voter_manager.get_registered_voters()), pre_attempt_voters,
                            "Registered voters list should remain unchanged after multiple duplicate attempts")
        
        # Test 4: Other unique voter IDs should still register successfully
        already_registered = {voter_id}  # Track what we've registered so far
        
        for other_voter_id in additional_voter_ids:
            if other_voter_id not in already_registered:  # Only test truly unique voter IDs
                pre_other_count = voter_manager.get_registration_count()
                other_result = voter_manager.register_voter(other_voter_id)
                
                self.assertTrue(other_result, f"Registration of unique voter ID '{other_voter_id}' should succeed")
                self.assertTrue(voter_manager.is_registered(other_voter_id), 
                              f"Voter '{other_voter_id}' should be registered after successful registration")
                self.assertEqual(voter_manager.get_registration_count(), pre_other_count + 1,
                               f"Registration count should increase after registering '{other_voter_id}'")
                already_registered.add(other_voter_id)
            else:
                # This voter ID was already registered (duplicate in our test)
                pre_other_count = voter_manager.get_registration_count()
                other_result = voter_manager.register_voter(other_voter_id)
                
                self.assertFalse(other_result, f"Duplicate registration of '{other_voter_id}' should fail")
                self.assertEqual(voter_manager.get_registration_count(), pre_other_count,
                               f"Registration count should remain unchanged for duplicate '{other_voter_id}'")
        
        # Test 5: Original voter should still be registered and unchanged
        self.assertTrue(voter_manager.is_registered(voter_id), 
                       "Original voter should still be registered after other registrations")
        
        # Test 6: System state should be consistent
        registered_voters = voter_manager.get_registered_voters()
        self.assertIn(voter_id, registered_voters, "Original voter should be in registered voters list")
        
        # Each voter in the list should be registered
        for registered_voter in registered_voters:
            self.assertTrue(voter_manager.is_registered(registered_voter),
                           f"Every voter in registered list should be registered: {registered_voter}")
        
        # No duplicates in registered voters list
        self.assertEqual(len(registered_voters), len(set(registered_voters)),
                        "Registered voters list should contain no duplicates")
    
    @given(
        voter_ids=st.lists(
            st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc', 'Pd'))),
            min_size=0,
            max_size=20,
            unique=True  # Ensure all voter IDs are unique
        )
    )
    def test_voter_registry_completeness_property_2(self, voter_ids):
        """
        Property 2: Voter Registry Completeness
        Feature: blockchain-voting, Property 2: Voter Registry Completeness
        Validates: Requirements 1.3, 1.4
        
        For any set of registered voter IDs, retrieving the registered voters should 
        return exactly the same set with no additions or omissions.
        """
        voter_manager = VoterManager()
        
        # Register all the voter IDs
        successfully_registered = set()
        for voter_id in voter_ids:
            result = voter_manager.register_voter(voter_id)
            if result:  # Should always be True since voter_ids are unique
                successfully_registered.add(voter_id)
        
        # All registrations should succeed since voter_ids are unique
        self.assertEqual(len(successfully_registered), len(voter_ids),
                        "All unique voter IDs should register successfully")
        self.assertEqual(successfully_registered, set(voter_ids),
                        "Successfully registered set should match input set")
        
        # Test 1: Retrieved voters should exactly match registered voters
        retrieved_voters = voter_manager.get_registered_voters()
        retrieved_set = set(retrieved_voters)
        
        self.assertEqual(retrieved_set, successfully_registered,
                        "Retrieved voter set should exactly match registered voter set")
        self.assertEqual(len(retrieved_voters), len(successfully_registered),
                        "Retrieved voter count should match registered voter count")
        
        # Test 2: No additions - every retrieved voter should be one we registered
        for retrieved_voter in retrieved_voters:
            self.assertIn(retrieved_voter, successfully_registered,
                         f"Retrieved voter '{retrieved_voter}' should be one we registered")
        
        # Test 3: No omissions - every registered voter should be retrieved
        for registered_voter in successfully_registered:
            self.assertIn(registered_voter, retrieved_set,
                         f"Registered voter '{registered_voter}' should be in retrieved set")
        
        # Test 4: No duplicates in retrieved list
        self.assertEqual(len(retrieved_voters), len(set(retrieved_voters)),
                        "Retrieved voters list should contain no duplicates")
        
        # Test 5: Consistency check - is_registered should match retrieved list
        for voter_id in voter_ids:
            is_registered_result = voter_manager.is_registered(voter_id)
            in_retrieved_list = voter_id in retrieved_set
            self.assertEqual(is_registered_result, in_retrieved_list,
                           f"is_registered({voter_id}) should match presence in retrieved list")
        
        # Test 6: Registration count should match retrieved count
        registration_count = voter_manager.get_registration_count()
        self.assertEqual(registration_count, len(retrieved_voters),
                        "Registration count should match length of retrieved voters list")
        self.assertEqual(registration_count, len(successfully_registered),
                        "Registration count should match number of successfully registered voters")
        
        # Test 7: Test with empty set (edge case)
        if len(voter_ids) == 0:
            self.assertEqual(len(retrieved_voters), 0,
                           "Empty registration should result in empty retrieved list")
            self.assertEqual(registration_count, 0,
                           "Empty registration should result in zero count")
        
        # Test 8: Test persistence through serialization (completeness preserved)
        if len(voter_ids) > 0:
            # Serialize and deserialize
            data = voter_manager.to_dict()
            new_manager = VoterManager.from_dict(data)
            
            # Check completeness is preserved
            new_retrieved_voters = new_manager.get_registered_voters()
            new_retrieved_set = set(new_retrieved_voters)
            
            self.assertEqual(new_retrieved_set, retrieved_set,
                           "Voter registry completeness should be preserved through serialization")
            self.assertEqual(len(new_retrieved_voters), len(retrieved_voters),
                           "Voter count should be preserved through serialization")


if __name__ == '__main__':
    unittest.main()