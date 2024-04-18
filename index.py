import requests
from unittest import TestCase, mock

def mocked_requests_get(*args, **kwargs):
  mock_response = mock.Mock()
  if args[0] == 'http://yahoo.co.jp':
    mock_response.text = {'name': 'yahoo!'}
  else:
    mock_response.text = {'name': 'unknown!'}
  return mock_response 

class MyTestCase(TestCase):
  @mock.patch('requests.get', side_effect=mocked_requests_get)
  def test_tameshi(self, mock_get):
    # テスト対象のコードを実行します
    res1 = requests.get('http://yahoo.co.jp')
    res2 = requests.get('http://example1.com')

    # 返ってきたResponseオブジェクトのtext属性が期待通りの値を持っているかを確認します
    self.assertEqual(res1.text, {'name': 'yahoo!'})
    self.assertEqual(res2.text, {'name': 'unknown!'})
