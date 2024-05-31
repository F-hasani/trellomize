import unittest
import json
import os
import uuid
from datetime import datetime, timedelta
from trello_ff import create_account, login, add_project, add_member_to_project, remove_member_from_project, assign_task_to_member, deactivate_user, load_data, save_data, DATA_FILE, PROJECTS_FILE, Priority, Status

class TestProjectManagementSystem(unittest.TestCase):

    def setUp(self):
        # Set up a temporary users and projects file for testing
        self.test_users_file = 'test_users.json'
        self.test_projects_file = 'test_projects.json'
        self.test_user = {
            'id': str(uuid.uuid4()),
            'username': 'testuser',
            'password': 'dGVzdHBhc3M=',  # 'testpass' encoded in base64
            'email': 'testuser@example.com',
            'role': 'manager',
            'active': True
        }
        self.test_project = {
            'id': str(uuid.uuid4()),
            'title': 'Test Project',
            'description': 'A test project',
            'leader': 'testuser',
            'members': ['testuser'],
            'tasks': [],
            'comments': [],
            'priority': Priority.LOW.value,
            'status': Status.BACKLOG.value,
            'start_time': datetime.now().isoformat(),
            'end_time': (datetime.now() + timedelta(hours=24)).isoformat()
        }
        save_data([self.test_user], self.test_users_file)
        save_data([self.test_project], self.test_projects_file)

    def tearDown(self):
        # Clean up the temporary files after each test
        if os.path.exists(self.test_users_file):
            os.remove(self.test_users_file)
        if os.path.exists(self.test_projects_file):
            os.remove(self.test_projects_file)

    def test_create_account(self):
        result = create_account('newuser', 'newpass', 'newuser@example.com', False)
        self.assertTrue(result)
        users = load_data(self.test_users_file)
        self.assertEqual(len(users), 2)
        self.assertEqual(users[1]['username'], 'newuser')

    def test_login(self):
        user = login('testuser', 'testpass')
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], 'testuser')

    def test_add_project(self):
        add_project('testuser')
        projects = load_data(self.test_projects_file)
        self.assertEqual(len(projects), 2)
        self.assertEqual(projects[1]['leader'], 'testuser')

    def test_add_member_to_project(self):
        create_account('newmember', 'newpass', 'newmember@example.com', False)
        add_member_to_project('testuser')
        projects = load_data(self.test_projects_file)
        self.assertIn('newmember', projects[0]['members'])

    def test_remove_member_from_project(self):
        create_account('newmember', 'newpass', 'newmember@example.com', False)
        add_member_to_project('testuser')
        remove_member_from_project('testuser')
        projects = load_data(self.test_projects_file)
        self.assertNotIn('newmember', projects[0]['members'])

    def test_assign_task_to_member(self):
        create_account('newmember', 'newpass', 'newmember@example.com', False)
        add_member_to_project('testuser')
        assign_task_to_member('testuser')
        projects = load_data(self.test_projects_file)
        self.assertEqual(len(projects[0]['tasks']), 1)
        self.assertEqual(projects[0]['tasks'][0]['assigned_to'], 'newmember')

    def test_deactivate_user(self):
        deactivate_user()
        users = load_data(self.test_users_file)
        self.assertFalse(users[0]['active'])

if __name__ == '__main__':
    unittest.main()
