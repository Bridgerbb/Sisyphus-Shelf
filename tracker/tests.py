from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import MediaItem

class SisyphusTests(TestCase):
    
    def setUp(self):
        # 1. Create a fake user for the test
        self.user = User.objects.create_user(username='testuser', password='password123')
        
        # 2. Force the test client to log in as that user!
        self.client.force_login(self.user)
        
        # 3. Create our fake test item, and make sure it belongs to the logged-in user!
        self.test_item = MediaItem.objects.create(
            title="Elden Ring",
            creator="FromSoftware",
            genre="Action RPG",
            media_type="Game",
            status="Backlog",
            priority_flag=True,
            rating=5,
            notes="Need to beat the DLC.",
            user=self.user 
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
            'genre': 'Action RPG',
            'media_type': 'Game',
            'status': 'Finished',  # Changing from Backlog to Finished!
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
        
    def test_finished_status_removes_priority(self):
        """Test 6: Does marking an item as Finished automatically strip the priority flag?"""
        # We start with our test_item which is currently marked as priority
        self.test_item.status = 'Finished'
        self.test_item.save() # This triggers our custom save() method
        
        self.assertFalse(self.test_item.priority_flag)

    def test_queue_order_api(self):
        """Test 7: Does the hidden API correctly update queue order?"""
        import json
        
        # Create a second item so we can swap their order
        item2 = MediaItem.objects.create(
            title="Dune", creator="Frank Herbert", media_type="Book", 
            status="Backlog", user=self.user
        )
        
        # Simulate our JavaScript sending a silent POST request with the new order
        response = self.client.post(reverse('update_queue_order'), 
                                    data=json.dumps({'ordered_ids': [item2.id, self.test_item.id]}),
                                    content_type='application/json')
        
        # Check that the API responded with a success code
        self.assertEqual(response.status_code, 200)
        
        # Refresh the items from the database
        item2.refresh_from_db()
        self.test_item.refresh_from_db()
        
        # Ensure Dune is now in position 0, and Elden Ring is in position 1
        self.assertEqual(item2.queue_order, 0)
        self.assertEqual(self.test_item.queue_order, 1)