from django.test import TestCase
from django.urls import reverse
from .models import MediaItem

class SisyphusShelfTests(TestCase):
    
    def setUp(self):
        # This runs before every test to set up a fake "test" database item
        self.test_item = MediaItem.objects.create(
            title="Elden Ring",
            creator="FromSoftware",
            media_type="Game",
            status="Backlog",
            priority_flag=True,
            rating=5,
            notes="Need to beat the DLC."
        )

    def test_dashboard_loads_properly(self):
        """Test 1: Does the homepage load and return a 200 OK status code?"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_database_creation(self):
        """Test 2: Did our fake test item actually save to the database?"""
        item = MediaItem.objects.get(title="Elden Ring")
        self.assertEqual(item.creator, "FromSoftware")
        self.assertTrue(item.priority_flag)

    def test_item_deletion(self):
        """Test 3: Does the delete view actually wipe the item from the database?"""
        # Send a POST request to the delete URL
        response = self.client.post(reverse('delete_item', args=[self.test_item.pk]))
        
        # Check that it redirected us back to the pile (status code 302)
        self.assertEqual(response.status_code, 302)
        
        # Check that the database is now empty
        self.assertEqual(MediaItem.objects.count(), 0)
    def test_item_update(self):
        """Test 4: Does the update form successfully change the item's data?"""
        # Send a POST request to the item_detail view with new data
        response = self.client.post(reverse('item_detail', args=[self.test_item.pk]), {
            'title': 'Elden Ring',
            'creator': 'FromSoftware',
            'media_type': 'Game',
            'status': 'Finished', # Changing from Backlog to Finished!
            'rating': 5,
            'notes': 'Finally beat the DLC.'
        })
        
        # Refresh our test item from the database
        self.test_item.refresh_from_db()
        
        # Verify the status actually changed
        self.assertEqual(self.test_item.status, 'Finished')
    def test_search_functionality(self):
        """Test 5: Does the search bar actually filter items?"""
        # Search for something that exists
        response_match = self.client.get(reverse('pile') + '?q=Elden')
        self.assertContains(response_match, 'Elden Ring')
        
        # Search for something that doesn't exist
        response_empty = self.client.get(reverse('pile') + '?q=Zelda')
        self.assertNotContains(response_empty, 'Elden Ring')