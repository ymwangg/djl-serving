import json
import unittest

import djl_python.rolling_batch.rolling_batch
from djl_python.rolling_batch.rolling_batch import Request, Token, _json_output_formatter, _jsonlines_output_formatter


class TestRollingBatch(unittest.TestCase):

    def test_json_fmt(self):
        req1 = Request(0,
                       "This is a wonderful day",
                       parameters={"max_new_tokens": 256},
                       output_formatter=_json_output_formatter)
        req2 = Request(1,
                       "This is a wonderful day",
                       parameters={
                           "max_new_tokens": 256,
                           "stream": False
                       })
        for req in [req1, req2]:
            req.set_next_token(Token(244, "He", -0.334532))
            print(req.get_next_token(), end='')
            assert req.get_next_token() == '{"generated_text": "He'
            req.reset_next_token()
            req.set_next_token(Token(576, "llo", -0.123123))
            print(req.get_next_token(), end='')
            assert req.get_next_token() == 'llo'
            req.reset_next_token()
            req.set_next_token(Token(4558, " world", -0.567854), True,
                               'length')
            print(req.get_next_token(), end='')
            assert req.get_next_token() == ' world"}'
            req.reset_next_token()

    def test_json_fmt_with_appending(self):
        req1 = Request(0,
                       "This is a wonderful day",
                       parameters={"max_new_tokens": 256},
                       output_formatter=_json_output_formatter)
        req2 = Request(1,
                       "This is a wonderful day",
                       parameters={
                           "max_new_tokens": 256,
                           "stream": False
                       })
        for req in [req1, req2]:
            req.set_next_token(Token(244, "He", -0.334532))
            req.set_next_token(Token(576, "llo", -0.123123))
            print(req.get_next_token(), end='')
            assert req.get_next_token() == '{"generated_text": "Hello'
            req.reset_next_token()
            req.set_next_token(Token(4558, " world", -0.567854), True,
                               'length')
            print(req.get_next_token(), end='')
            assert req.get_next_token() == ' world"}'

    def test_json_fmt_hf_compat(self):
        djl_python.rolling_batch.rolling_batch.TGI_COMPAT = True

        req = Request(0,
                      "This is a wonderful day",
                      parameters={
                          "max_new_tokens": 256,
                          "return_full_text": True,
                      },
                      output_formatter=_json_output_formatter)

        final_str = []
        req.set_next_token(Token(244, "He", -0.334532))
        final_str.append(req.get_next_token())
        req.reset_next_token()
        req.set_next_token(Token(576, "llo", -0.123123))
        final_str.append(req.get_next_token())
        req.reset_next_token()
        req.set_next_token(Token(4558, " world", -0.567854), True, 'length')
        final_str.append(req.get_next_token())
        final_json = json.loads(''.join(final_str))
        print(final_json, end='')
        assert final_json == [{
            "generated_text":
            "This is a wonderful dayHello world",
        }]
        djl_python.rolling_batch.rolling_batch.TGI_COMPAT = False

    def test_jsonlines_fmt(self):
        req1 = Request(0,
                       "This is a wonderful day",
                       parameters={"max_new_tokens": 256},
                       output_formatter=_jsonlines_output_formatter)
        req2 = Request(1,
                       "This is a wonderful day",
                       parameters={
                           "max_new_tokens": 256,
                           "stream": True
                       })
        for req in [req1, req2]:
            req.set_next_token(Token(244, "He", -0.334532))
            print(req.get_next_token(), end='')
            assert json.loads(req.get_next_token()) == {
                "token": {
                    "id": [244],
                    "text": "He",
                    "log_prob": -0.334532
                }
            }
            req.reset_next_token()
            req.set_next_token(Token(576, "llo", -0.123123))
            print(req.get_next_token(), end='')
            assert json.loads(req.get_next_token()) == {
                "token": {
                    "id": [576],
                    "text": "llo",
                    "log_prob": -0.123123
                }
            }
            req.reset_next_token()
            req.set_next_token(Token(4558, " world", -0.567854), True,
                               'length')
            print(req.get_next_token(), end='')
            assert json.loads(req.get_next_token()) == {
                "token": {
                    "id": [4558],
                    "text": " world",
                    "log_prob": -0.567854
                },
                "generated_text": "Hello world"
            }

    def test_return_full_text(self):
        req = Request(0,
                      "This is a wonderful day",
                      parameters={
                          "max_new_tokens": 256,
                          "return_full_text": True,
                      },
                      output_formatter=_json_output_formatter)

        final_str = []
        req.set_next_token(Token(244, "He", -0.334532))
        final_str.append(req.get_next_token())
        req.reset_next_token()
        req.set_next_token(Token(576, "llo", -0.123123))
        final_str.append(req.get_next_token())
        req.reset_next_token()
        req.set_next_token(Token(4558, " world", -0.567854), True, 'length')
        final_str.append(req.get_next_token())
        final_json = json.loads(''.join(final_str))
        print(final_json, end='')
        assert final_json == {
            "generated_text": "This is a wonderful dayHello world",
        }

        req = Request(0,
                      "This is a wonderful day",
                      parameters={
                          "max_new_tokens": 256,
                          "return_full_text": True
                      },
                      output_formatter=_jsonlines_output_formatter)
        req.set_next_token(Token(244, "He", -0.334532))
        req.set_next_token(Token(576, "llo", -0.123123))
        req.set_next_token(Token(4558, " world", -0.567854), True, 'length')
        print(req.get_next_token(), end='')
        assert json.loads(req.get_next_token().splitlines()[-1]) == {
            "token": {
                "id": [4558],
                "text": " world",
                "log_prob": -0.567854
            },
            "generated_text": "This is a wonderful dayHello world",
        }

    def test_details(self):
        req = Request(0,
                      "This is a wonderful day",
                      parameters={
                          "max_new_tokens": 256,
                          "details": True
                      },
                      details=True,
                      output_formatter=_json_output_formatter)
        final_str = []
        req.set_next_token(Token(244, "He", -0.334532))
        final_str.append(req.get_next_token())
        req.reset_next_token()
        req.set_next_token(Token(576, "llo", -0.123123))
        final_str.append(req.get_next_token())
        req.reset_next_token()
        req.set_next_token(Token(4558, " world", -0.567854), True, 'length')
        final_str.append(req.get_next_token())
        final_json = json.loads(''.join(final_str))
        print(final_json)
        assert final_json == {
            "generated_text": "Hello world",
            "details": {
                'inputs':
                'This is a wonderful day',
                "finish_reason":
                "length",
                "generated_tokens":
                3,
                "tokens": [{
                    "id": [244],
                    "text": "He",
                    "log_prob": -0.334532
                }, {
                    "id": [576],
                    "text": "llo",
                    "log_prob": -0.123123
                }, {
                    "id": [4558],
                    "text": " world",
                    "log_prob": -0.567854
                }]
            }
        }
        # Jsonlines tests
        req = Request(0,
                      "This is a wonderful day",
                      parameters={
                          "max_new_tokens": 256,
                          "details": True
                      },
                      details=True,
                      output_formatter=_jsonlines_output_formatter)
        req.set_next_token(Token(244, "He", -0.334532))
        req.set_next_token(Token(576, "llo", -0.123123))
        req.set_next_token(Token(4558, " world", -0.567854), True, 'length')
        print(req.get_next_token(), end='')
        assert json.loads(req.get_next_token().splitlines()[-1]) == {
            "token": {
                "id": [4558],
                "text": " world",
                "log_prob": -0.567854
            },
            "generated_text": "Hello world",
            "details": {
                'inputs': 'This is a wonderful day',
                "finish_reason": "length",
                "generated_tokens": 3,
            }
        }

    def test_details_jsonlines(self):
        req = Request(0,
                      "This is a wonderful day",
                      parameters={
                          "max_new_tokens": 256,
                          "details": True,
                          "decoder_input_details": True
                      },
                      details=True,
                      output_formatter=_jsonlines_output_formatter)
        req.set_next_token(Token(244, "He", -0.334532))
        print(req.get_next_token(), end='')
        assert json.loads(req.get_next_token()) == {
            "token": {
                "id": [244],
                "text": "He",
                "log_prob": -0.334532
            }
        }
        req.reset_next_token()
        req.set_next_token(Token(576, "llo", -0.123123))
        print(req.get_next_token(), end='')
        assert json.loads(req.get_next_token()) == {
            "token": {
                "id": [576],
                "text": "llo",
                "log_prob": -0.123123
            }
        }
        req.reset_next_token()
        req.set_next_token(Token(4558, " world", -0.567854),
                           True,
                           'length',
                           prompt_tokens_details=[
                               Token(id=[123], text="This",
                                     log_prob=None).as_dict(),
                               Token(id=[456], text="is",
                                     log_prob=0.456).as_dict(),
                               Token(id=[789], text="a",
                                     log_prob=0.789).as_dict(),
                               Token(id=[124],
                                     text="wonderful",
                                     log_prob=0.124).as_dict(),
                               Token(id=[356], text="day",
                                     log_prob=0.356).as_dict()
                           ])
        print(req.get_next_token(), end='')
        assert json.loads(req.get_next_token()) == {
            "token": {
                "id": [4558],
                "text": " world",
                "log_prob": -0.567854
            },
            'details': {
                'finish_reason':
                'length',
                'generated_tokens':
                3,
                'inputs':
                'This is a wonderful day',
                'prefill': [{
                    'id': [123],
                    'text': 'This'
                }, {
                    'id': [456],
                    'log_prob': 0.456,
                    'text': 'is'
                }, {
                    'id': [789],
                    'log_prob': 0.789,
                    'text': 'a'
                }, {
                    'id': [124],
                    'log_prob': 0.124,
                    'text': 'wonderful'
                }, {
                    'id': [356],
                    'log_prob': 0.356,
                    'text': 'day'
                }],
            },
            "generated_text": "Hello world"
        }

    def test_custom_fmt(self):

        def custom_fmt(token: Token, first_token: bool, last_token: bool,
                       details: dict, generated_tokens: str, id: int):
            result = {
                "token_id": token.id,
                "token_text": token.text,
                "request_id": token.request_id
            }
            if last_token:
                result["finish_reason"] = details["finish_reason"]
            return json.dumps(result) + "\n"

        req = Request(132,
                      "This is a wonderful day",
                      parameters={
                          "max_new_tokens": 256,
                          "details": True
                      },
                      details=True,
                      output_formatter=custom_fmt)
        req.set_next_token(Token(244, "He", -0.334532))
        print(req.get_next_token(), end='')
        assert json.loads(req.get_next_token()) == {
            'token_id': [244],
            'token_text': 'He',
            "request_id": 132
        }
        req.reset_next_token()
        req.set_next_token(Token(576, "llo", -0.123123))
        print(req.get_next_token(), end='')
        assert json.loads(req.get_next_token()) == {
            'token_id': [576],
            'token_text': 'llo',
            "request_id": 132
        }
        req.reset_next_token()
        req.set_next_token(Token(4558, " world", -0.567854), True, 'length')
        print(req.get_next_token(), end='')
        assert json.loads(req.get_next_token()) == {
            'token_id': [4558],
            'token_text': ' world',
            'finish_reason': 'length',
            "request_id": 132
        }

    def test_custom_fmt_with_detailed_data_retrival(self):

        def custom_fmt(token: Token, first_token: bool, last_token: bool,
                       details: dict, generated_tokens: str, id: int):
            result = details
            return json.dumps(result) + "\n"

        req = Request(132,
                      "This is a wonderful day",
                      parameters={
                          "max_new_tokens": 256,
                          "details": True
                      },
                      details=True,
                      input_ids=[101, 1188, 1110, 170, 7310, 1285, 102],
                      output_formatter=custom_fmt)
        req.set_next_token(Token(244, "He", -0.334532))
        print(req.get_next_token(), end='')
        assert json.loads(req.get_next_token()) == {
            'finish_reason': None,
            'generated_tokens': 1,
            'inputs': 'This is a wonderful day',
            'tokens': [{
                'id': [244],
                'log_prob': -0.334532,
                'text': 'He'
            }],
            "parameters": {
                "max_new_tokens": 256,
                "details": True
            },
            "prompt_tokens": 7
        }
        req.reset_next_token()
        req.set_next_token(Token(576, "llo", -0.123123))
        print(req.get_next_token(), end='')
        assert json.loads(req.get_next_token()) == {
            'finish_reason':
            None,
            'generated_tokens':
            2,
            'inputs':
            'This is a wonderful day',
            'tokens': [
                {
                    'id': [244],
                    'text': 'He',
                    'log_prob': -0.334532,
                },
                {
                    'id': [576],
                    'text': 'llo',
                    'log_prob': -0.123123,
                },
            ],
            "parameters": {
                "max_new_tokens": 256,
                "details": True
            },
            "prompt_tokens":
            7
        }
        req.reset_next_token()
        req.set_next_token(Token(4558, " world", -0.567854), True, 'length')
        print(req.get_next_token(), end='')
        assert json.loads(req.get_next_token()) == {
            'finish_reason':
            'length',
            'generated_tokens':
            3,
            'inputs':
            'This is a wonderful day',
            'tokens': [{
                'id': [244],
                'text': 'He',
                'log_prob': -0.334532,
            }, {
                'id': [576],
                'text': 'llo',
                'log_prob': -0.123123,
            }, {
                'id': [4558],
                'text': ' world',
                'log_prob': -0.567854,
            }],
            "parameters": {
                "max_new_tokens": 256,
                "details": True
            },
            "prompt_tokens":
            7
        }


if __name__ == '__main__':
    unittest.main()
