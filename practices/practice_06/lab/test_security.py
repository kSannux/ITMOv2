"""Authorization and input-handling regression tests."""
from test_service import ShopTest


class SecurityTest(ShopTest):
    def test_context_supplies_authorized_receipt_path(self):
        status, result = self.request('GET', '/assistant/context?order_id=1', headers=self.login())
        self.assertEqual(status, 200)
        self.assertIn('files/alice/receipt.txt', result['prompt'])
        self.assertNotIn('files/bob/receipt.txt', result['prompt'])

    def test_private_routes_require_login(self):
        for path in ('/profile?id=1', '/orders', '/files', '/debug/logs', '/assistant/context'):
            with self.subTest(path=path):
                self.assertEqual(self.request('GET', path)[0], 401)

    def test_no_foreign_profile(self):
        self.assertEqual(self.request('GET', '/profile?id=2', headers=self.login())[0], 403)

    def test_orders_are_scoped(self):
        self.assertTrue(all(r['owner'] == 1 for r in self.request('GET', '/orders', headers=self.login())[1]))

    def test_role_header_is_not_authority(self):
        self.assertEqual(self.request('GET', '/admin/export', headers={'X-Role': 'staff'})[0], 401)
        self.assertEqual(self.request('GET', '/admin/export', headers={**self.login(), 'X-Role': 'staff'})[0], 403)
        self.assertEqual(self.request('GET', '/admin/export', headers=self.login('staff', 'learn-staff'))[0], 200)

    def test_price_is_server_owned(self):
        self.assertEqual(self.request('POST', '/orders', {'product': 'chair', 'price': -1}, self.login())[1]['price'], 5000)

    def test_foreign_files_blocked(self):
        for path in ('/files?user=bob&path=receipt.txt', '/files?user=alice&path=../../private/operator-note.txt'):
            self.assertEqual(self.request('GET', path, headers=self.login())[0], 403)

    def test_sql_injection_rejected(self):
        auth = self.login()
        for path in ('/profile?id=1%20OR%201=1', '/assistant/context?order_id=1%20OR%201=1'):
            self.assertEqual(self.request('GET', path, headers=auth)[0], 400)
        self.assertEqual(self.request('GET', '/search?q=%27%20OR%201=1%20--', headers=auth)[1], [])

    def test_review_is_escaped(self):
        auth = self.login()
        self.request('POST', '/reviews', {'product': 'chair', 'text': '<script>alert(1)</script>'}, auth)
        page = self.request('GET', '/reviews/view', headers=auth)[1]
        self.assertNotIn('<script>', page)
        self.assertIn('&lt;script&gt;', page)

    def test_reviews_need_login(self):
        self.assertEqual(self.request('POST', '/reviews', {'product': 'chair', 'text': 'x'})[0], 401)

    def test_tools_enforce_access(self):
        auth = self.login()
        for decision in ({'tool': 'export_profiles'}, {'tool': 'delete_tree', 'arguments': {'path': '.'}},
                         {'tool': 'read_file', 'arguments': {'path': 'private/operator-note.txt'}},
                         {'tool': 'read_file', 'arguments': {'path': 'files/bob/receipt.txt'}}):
            self.assertEqual(self.request('POST', '/assistant/execute', {'decision': decision}, auth)[0], 403)
        self.assertIn('TEST_ALICE', self.shop.sandbox.read('files/alice/receipt.txt'))

    def test_context_is_owned(self):
        self.assertEqual(self.request('GET', '/assistant/context?order_id=2', headers=self.login())[0], 403)

    def test_logs_have_no_credentials(self):
        self.login()
        status, logs = self.request('GET', '/debug/logs', headers=self.login('staff', 'learn-staff'))
        self.assertEqual(status, 200)
        self.assertNotIn('learn-alice', str(logs))

    def test_invalid_body(self):
        self.assertEqual(self.request('POST', '/orders', {}, self.login())[0], 400)
