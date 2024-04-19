import requests
from unittest import TestCase, mock

RETRY_COUNT = 2

def requestWithRetry():
  for i in range(1, RETRY_COUNT + 1):
    try:
      res = requests.get('http://yahoo.co.jp')
      res.raise_for_status()
      return res.text
    except requests.HTTPError as e:
      if i < RETRY_COUNT:
        print(f"{i}th try failed({e})")
        continue
      else:
        raise RuntimeError('all requests failed')

def raise_for_status():
  raise requests.HTTPError('404 Client Error')
  
class MyTestCase(TestCase):
  #@mock.patch('requests.get', side_effect=mocked_requests_get)
  @mock.patch('requests.get')
  def test_call_multiple_urls(self, mock_get):
    def mocked_requests_get(*args, **kwargs):
      mock_response = mock.Mock()
      if args[0] == 'http://yahoo.co.jp':
        mock_response.text = {'name': 'yahoo!'}
      else:
        mock_response.text = {'name': 'unknown!'}
      return mock_response 

    mock_get.side_effect = mocked_requests_get

    res1 = requests.get('http://yahoo.co.jp', headers = {'user-agent': 'my-app/0.0.1'})
    res2 = requests.get('http://example.com')

    self.assertEqual(res1.text, {'name': 'yahoo!'})
    self.assertEqual(res2.text, {'name': 'unknown!'})
    mock_get.assert_any_call('http://yahoo.co.jp', headers = {'user-agent': 'my-app/0.0.1'})
    mock_get.assert_any_call('http://example.com')

  @mock.patch('requests.get')
  def test_call_same_url_repeatedly(self, mock_get):
    first_resp = mock.Mock();
    first_resp.text = {'name':'first'}
    second_resp = mock.Mock();
    second_resp.text = {'name':'second'}
    mock_get.side_effect = [first_resp, second_resp]

    res1 = requests.get('http://yahoo.co.jp')
    res2 = requests.get('http://yahoo.co.jp')

    self.assertEqual(res1.text, {'name': 'first'})
    self.assertEqual(res2.text, {'name': 'second'})

  @mock.patch('requests.get')
  def test_error(self, mock_get):
    resp = mock.Mock();
    resp.raise_for_status = raise_for_status
    mock_get.return_value = resp

    with self.assertRaises(requests.HTTPError) as context:
      res = requests.get('http://yahoo.co.jp')
      res.raise_for_status()

    self.assertEqual(str(context.exception), '404 Client Error')

  @mock.patch('requests.get')
  def test_success_after_retry(self, mock_get):
    resp1 = mock.Mock();
    resp1.raise_for_status = raise_for_status
    resp2 = mock.Mock();
    resp2.text = {'name':'second'}
    mock_get.side_effect = [ resp1, resp2 ]

    try:  
      text = requestWithRetry()
      self.assertEqual(text, {'name': 'second'})
    except Exception as e:
      self.fail(f"unexpected exception raised: {e}")
  
  @mock.patch('requests.get')
  def test_failed_after_all_retry(self, mock_get):
    resp = mock.Mock();
    resp.raise_for_status = raise_for_status
    mock_get.return_value = resp

    with self.assertRaises(RuntimeError) as context:
      text = requestWithRetry()

    self.assertEqual(str(context.exception), 'all requests failed')
