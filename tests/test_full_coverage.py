import os
import sys
import importlib
import runpy
import random
import time
from datetime import datetime
from unittest.mock import MagicMock

import pytest
import requests

# Ensure src directory is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Guarantee a token is present for initial import
os.environ.setdefault('GITHUB_TOKEN', 'test_token')

import main  # noqa: E402  # Late import after adjusting sys.path


@pytest.fixture(autouse=True)
def restore_main(monkeypatch):
    """Ensure every test starts with a fresh main module and test token."""
    monkeypatch.setenv('GITHUB_TOKEN', 'test_token')
    module = importlib.reload(main)
    yield module


def _mock_rate_limit_response(remaining=5000, reset=None):
    mock = MagicMock()
    mock.status_code = 200
    mock.text = 'ok'
    mock.json.return_value = {
        'resources': {
            'core': {
                'remaining': remaining,
                'reset': int(reset or datetime.now().timestamp())
            }
        }
    }
    return mock


# --- Module import requirements -------------------------------------------------

def test_module_requires_token(monkeypatch):
    import main as main_module
    import dotenv

    monkeypatch.setattr(dotenv, 'load_dotenv', lambda *args, **kwargs: None)
    monkeypatch.delenv('GITHUB_TOKEN', raising=False)
    with pytest.raises(ValueError):
        importlib.reload(main_module)

    # Restore token for remaining tests
    monkeypatch.setenv('GITHUB_TOKEN', 'test_token')
    importlib.reload(main_module)


# --- get_user_* family ----------------------------------------------------------

def test_get_user_info_unexpected_exception(monkeypatch):
    mock_response = MagicMock()
    monkeypatch.setattr(main.requests, 'get', MagicMock(return_value=mock_response))
    monkeypatch.setattr(main, 'handle_api_response', MagicMock(side_effect=Exception('boom')))

    assert main.get_user_info('someone') is None


def test_get_my_info_network_error(monkeypatch):
    monkeypatch.setattr(main.requests, 'get', MagicMock(side_effect=requests.exceptions.Timeout('timeout')))
    assert main.get_my_info() is None


def test_get_user_activity_request_exception(monkeypatch):
    monkeypatch.setattr(main.requests, 'get', MagicMock(side_effect=requests.exceptions.ConnectionError('oops')))
    assert main.get_user_activity('someone') is None


def test_get_my_followers_request_exception(monkeypatch):
    monkeypatch.setattr(main.requests, 'get', MagicMock(side_effect=requests.exceptions.ConnectionError('fail')))
    assert main.get_my_followers() == []


def test_get_my_followers_unexpected_exception(monkeypatch):
    mock_response = MagicMock()
    monkeypatch.setattr(main.requests, 'get', MagicMock(return_value=mock_response))
    monkeypatch.setattr(main, 'handle_api_response', MagicMock(side_effect=Exception('boom')))
    assert main.get_my_followers() == []


def test_get_my_following_multiple_pages(monkeypatch):
    mock_calls = [MagicMock(), MagicMock()]
    monkeypatch.setattr(main.requests, 'get', MagicMock(side_effect=mock_calls))
    monkeypatch.setattr(main, 'handle_api_response', MagicMock(side_effect=[
        [{'login': 'user1'}, {'login': 'user2'}],
        []
    ]))

    assert main.get_my_following() == ['user1', 'user2']


def test_get_my_following_request_exception(monkeypatch):
    monkeypatch.setattr(main.requests, 'get', MagicMock(side_effect=requests.exceptions.HTTPError('bad request')))
    assert main.get_my_following() == []


def test_get_my_following_unexpected_exception(monkeypatch):
    mock_response = MagicMock()
    monkeypatch.setattr(main.requests, 'get', MagicMock(return_value=mock_response))
    monkeypatch.setattr(main, 'handle_api_response', MagicMock(side_effect=Exception('boom')))
    assert main.get_my_following() == []


def test_get_my_following_safety_limit(monkeypatch):
    monkeypatch.setattr(main.requests, 'get', MagicMock(side_effect=lambda *args, **kwargs: MagicMock()))

    call_count = {'count': 0}

    def fake_handle(response, context):
        call_count['count'] += 1
        return [{'login': f'user{call_count["count"]}'}]

    monkeypatch.setattr(main, 'handle_api_response', fake_handle)

    result = main.get_my_following()
    assert len(result) == 100
    assert call_count['count'] == 100


def test_get_user_followers_request_exception(monkeypatch):
    monkeypatch.setattr(main.requests, 'get', MagicMock(side_effect=requests.exceptions.RequestException('fail')))
    assert main.get_user_followers('foo') == []


def test_get_user_followers_unexpected_exception(monkeypatch):
    mock_response = MagicMock()
    monkeypatch.setattr(main.requests, 'get', MagicMock(return_value=mock_response))
    monkeypatch.setattr(main, 'handle_api_response', MagicMock(side_effect=Exception('boom')))
    assert main.get_user_followers('foo') == []


def test_get_user_followers_empty_response(monkeypatch):
    mock_response = MagicMock()
    monkeypatch.setattr(main.requests, 'get', MagicMock(return_value=mock_response))
    monkeypatch.setattr(main, 'handle_api_response', MagicMock(return_value=[]))
    assert main.get_user_followers('foo') == []


def test_get_user_following_request_exception(monkeypatch):
    monkeypatch.setattr(main.requests, 'get', MagicMock(side_effect=requests.exceptions.RequestException('fail')))
    assert main.get_user_following('foo') == []


def test_get_user_following_unexpected_exception(monkeypatch):
    mock_response = MagicMock()
    monkeypatch.setattr(main.requests, 'get', MagicMock(return_value=mock_response))
    monkeypatch.setattr(main, 'handle_api_response', MagicMock(side_effect=Exception('boom')))
    assert main.get_user_following('foo') == []


def test_get_user_following_success(monkeypatch):
    mock_response = MagicMock()
    monkeypatch.setattr(main.requests, 'get', MagicMock(return_value=mock_response))
    monkeypatch.setattr(main, 'handle_api_response', MagicMock(return_value=[{'login': 'user1'}, {'login': 'user2'}]))

    assert main.get_user_following('foo') == ['user1', 'user2']


def test_get_user_following_empty_response(monkeypatch):
    mock_response = MagicMock()
    monkeypatch.setattr(main.requests, 'get', MagicMock(return_value=mock_response))
    monkeypatch.setattr(main, 'handle_api_response', MagicMock(return_value=[]))
    assert main.get_user_following('foo') == []


def test_follow_user_authentication_error(monkeypatch):
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = 'Unauthorized'
    monkeypatch.setattr(main.requests, 'put', MagicMock(return_value=mock_response))

    with pytest.raises(main.AuthenticationError):
        main.follow_user('blocked')


# --- find_potential_follows branches --------------------------------------------

def test_find_potential_follows_missing_username(monkeypatch):
    monkeypatch.setattr(main, 'get_my_info', lambda: {'login': None})
    assert main.find_potential_follows() == []


def test_find_potential_follows_handles_following_exception(monkeypatch):
    monkeypatch.setattr(main, 'get_my_info', lambda: {'login': 'me'})
    monkeypatch.setattr(main, 'get_my_followers', lambda: ['follower1'])
    monkeypatch.setattr(main, 'get_my_following', lambda: [])
    monkeypatch.setattr(main.random, 'sample', lambda seq, k: seq)
    monkeypatch.setattr(main, 'get_user_following', MagicMock(side_effect=Exception('boom')))
    monkeypatch.setattr(main, 'get_user_followers', lambda follower: [])
    monkeypatch.setattr(main, 'is_good_follow_candidate', lambda user: False)

    assert main.find_potential_follows() == []


def test_find_potential_follows_handles_followers_exception(monkeypatch):
    monkeypatch.setattr(main, 'get_my_info', lambda: {'login': 'me'})
    monkeypatch.setattr(main, 'get_my_followers', lambda: ['follower1'])
    monkeypatch.setattr(main, 'get_my_following', lambda: [])
    monkeypatch.setattr(main.random, 'sample', lambda seq, k: seq)
    monkeypatch.setattr(main, 'get_user_following', lambda follower: ['candidate'])
    monkeypatch.setattr(main, 'get_user_followers', MagicMock(side_effect=Exception('boom')))
    monkeypatch.setattr(main, 'is_good_follow_candidate', lambda user: False)

    assert main.find_potential_follows() == []


def test_find_potential_follows_logs_progress(monkeypatch):
    monkeypatch.setattr(main, 'get_my_info', lambda: {'login': 'me'})
    monkeypatch.setattr(main, 'get_my_followers', lambda: ['follower1'])
    monkeypatch.setattr(main, 'get_my_following', lambda: [])
    monkeypatch.setattr(main.random, 'sample', lambda seq, k: seq)

    candidates = [f'user{i}' for i in range(1, 15)]
    monkeypatch.setattr(main, 'get_user_following', lambda follower: candidates)
    monkeypatch.setattr(main, 'get_user_followers', lambda follower: [])

    call_order = {'count': 0}

    def evaluator(user):
        call_order['count'] += 1
        return False

    monkeypatch.setattr(main, 'is_good_follow_candidate', evaluator)

    result = main.find_potential_follows()
    assert result == []
    assert call_order['count'] >= 10  # triggers progress logging branch


def test_find_potential_follows_respects_daily_limit(monkeypatch):
    monkeypatch.setattr(main, 'get_my_info', lambda: {'login': 'me'})
    monkeypatch.setattr(main, 'get_my_followers', lambda: ['follower1'])
    monkeypatch.setattr(main, 'get_my_following', lambda: [])
    monkeypatch.setattr(main.random, 'sample', lambda seq, k: seq)
    monkeypatch.setattr(main, 'MAX_FOLLOWS_PER_DAY', 1)

    candidates = [f'user{i}' for i in range(1, 5)]
    monkeypatch.setattr(main, 'get_user_following', lambda follower: candidates)
    monkeypatch.setattr(main, 'get_user_followers', lambda follower: [])

    monkeypatch.setattr(main, 'is_good_follow_candidate', lambda user: True)

    result = main.find_potential_follows()
    assert len(result) == 1


def test_find_potential_follows_candidate_exception(monkeypatch):
    monkeypatch.setattr(main, 'get_my_info', lambda: {'login': 'me'})
    monkeypatch.setattr(main, 'get_my_followers', lambda: ['follower1'])
    monkeypatch.setattr(main, 'get_my_following', lambda: [])
    monkeypatch.setattr(main.random, 'sample', lambda seq, k: seq)
    monkeypatch.setattr(main, 'get_user_following', lambda follower: ['candidate'])
    monkeypatch.setattr(main, 'get_user_followers', lambda follower: [])

    def evaluator(user):
        raise RuntimeError('boom')

    monkeypatch.setattr(main, 'is_good_follow_candidate', evaluator)
    assert main.find_potential_follows() == []


def test_find_potential_follows_unexpected_error(monkeypatch):
    monkeypatch.setattr(main, 'get_my_info', MagicMock(side_effect=RuntimeError('fail')))
    assert main.find_potential_follows() == []


# --- main() branches ------------------------------------------------------------

def test_main_rate_limit_low_remaining(monkeypatch):
    mock_response = _mock_rate_limit_response(remaining=50)
    monkeypatch.setattr(main.requests, 'get', MagicMock(return_value=mock_response))
    mock_find = MagicMock()
    monkeypatch.setattr(main, 'find_potential_follows', mock_find)

    main.main()
    mock_find.assert_not_called()


def test_main_rate_limit_data_none(monkeypatch):
    mock_response = _mock_rate_limit_response(remaining=500)
    monkeypatch.setattr(main.requests, 'get', MagicMock(return_value=mock_response))
    monkeypatch.setattr(main, 'handle_api_response', MagicMock(return_value=None))
    monkeypatch.setattr(main, 'find_potential_follows', MagicMock(return_value=[]))

    main.main()


def test_main_candidate_search_rate_limit_error(monkeypatch):
    mock_response = _mock_rate_limit_response(remaining=500)
    monkeypatch.setattr(main.requests, 'get', MagicMock(return_value=mock_response))
    monkeypatch.setattr(main, 'find_potential_follows', MagicMock(side_effect=main.RateLimitError('limit')))

    main.main()


def test_main_candidate_search_generic_error(monkeypatch):
    mock_response = _mock_rate_limit_response(remaining=500)
    monkeypatch.setattr(main.requests, 'get', MagicMock(return_value=mock_response))
    monkeypatch.setattr(main, 'find_potential_follows', MagicMock(side_effect=RuntimeError('fail')))

    main.main()


def test_main_follow_candidates_success_failure(monkeypatch):
    mock_response = _mock_rate_limit_response(remaining=500)
    monkeypatch.setattr(main.requests, 'get', MagicMock(return_value=mock_response))
    monkeypatch.setattr(main.time, 'sleep', lambda _: None)
    monkeypatch.setattr(main.random, 'uniform', lambda a, b: 0)
    monkeypatch.setattr(main, 'find_potential_follows', MagicMock(return_value=['good', 'bad', 'error']))

    outcomes = [True, False, Exception('boom')]

    def follow_side_effect(user):
        result = outcomes.pop(0)
        if isinstance(result, Exception):
            raise result
        return result

    monkeypatch.setattr(main, 'follow_user', MagicMock(side_effect=follow_side_effect))

    main.main()


def test_main_follow_candidates_authentication_error(monkeypatch):
    mock_response = _mock_rate_limit_response(remaining=500)
    monkeypatch.setattr(main.requests, 'get', MagicMock(return_value=mock_response))
    monkeypatch.setattr(main, 'find_potential_follows', MagicMock(return_value=['user1']))
    monkeypatch.setattr(main, 'follow_user', MagicMock(side_effect=main.AuthenticationError('invalid')))

    main.main()


def test_main_outer_keyboard_interrupt(monkeypatch):
    mock_response = _mock_rate_limit_response(remaining=500)
    monkeypatch.setattr(main.requests, 'get', MagicMock(return_value=mock_response))
    monkeypatch.setattr(main, 'find_potential_follows', MagicMock(side_effect=KeyboardInterrupt()))

    main.main()


def test_main_outer_generic_exception(monkeypatch):
    mock_response = _mock_rate_limit_response(remaining=500)
    monkeypatch.setattr(main.requests, 'get', MagicMock(return_value=mock_response))
    monkeypatch.setattr(main, 'find_potential_follows', MagicMock(return_value=5))  # truthy, non-iterable

    main.main()


def test_main_script_entry(monkeypatch):
    monkeypatch.setenv('GITHUB_TOKEN', 'entry_token')

    def fake_get(url, headers=None, timeout=None):
        if url.endswith('/rate_limit'):
            return _mock_rate_limit_response(remaining=500)
        if url.endswith('/user'):
            resp = MagicMock()
            resp.status_code = 200
            resp.text = 'ok'
            resp.json.return_value = {'login': 'me'}
            return resp
        if '/events/public' in url:
            resp = MagicMock()
            resp.status_code = 200
            resp.text = 'ok'
            resp.json.return_value = []
            return resp
        resp = MagicMock()
        resp.status_code = 200
        resp.text = 'ok'
        resp.json.return_value = []
        return resp

    def fake_put(url, headers=None, timeout=None):
        resp = MagicMock()
        resp.status_code = 204
        resp.text = ''
        return resp

    original_main_module = sys.modules.get('__main__')

    monkeypatch.setattr(requests, 'get', fake_get)
    monkeypatch.setattr(requests, 'put', fake_put)
    monkeypatch.setattr(time, 'sleep', lambda _: None)
    monkeypatch.setattr(random, 'sample', lambda seq, k: [])

    try:
        runpy.run_module('main', run_name='__main__')
    finally:
        if original_main_module is not None:
            sys.modules['__main__'] = original_main_module
        else:
            sys.modules.pop('__main__', None)
