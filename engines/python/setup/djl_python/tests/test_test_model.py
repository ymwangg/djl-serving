#!/usr/bin/env python3
#
# Copyright 2024 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file
# except in compliance with the License. A copy of the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "LICENSE.txt" file accompanying this file. This file is distributed on an "AS IS"
# BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied. See the License for
# the specific language governing permissions and limitations under the License.
import json
import os
import unittest
from djl_python.test_model import TestHandler
from djl_python import huggingface
from .rolling_batch.fake_rolling_batch import FakeRollingBatch, FakeRollingBatchWithException


def override_rolling_batch(rolling_batch_type: str, is_mpi: bool,
                           model_config):
    return FakeRollingBatch


def override_rolling_batch_with_exception(rolling_batch_type: str,
                                          is_mpi: bool, model_config):
    return FakeRollingBatchWithException


class TestTestModel(unittest.TestCase):

    def test_all_code(self):
        model_id = "NousResearch/Nous-Hermes-Llama2-13b"
        huggingface.get_rolling_batch_class_from_str = override_rolling_batch
        handler = TestHandler(huggingface)
        inputs = [{
            "inputs": "The winner of oscar this year is",
            "parameters": {
                "max_new_tokens": 256
            }
        }, {
            "inputs": "A little redhood is",
            "parameters": {
                "max_new_tokens": 50
            }
        }]
        serving_properties = {
            "engine": "Python",
            "rolling_batch": "auto",
            "model_id": model_id
        }
        result = handler.inference_rolling_batch(
            inputs, serving_properties=serving_properties)
        self.assertEqual(len(result), len(inputs))
        self.assertTrue(json.loads(result[0]), dict)
        self.assertTrue(json.loads(result[1]), dict)

    def test_with_env(self):
        envs = {
            "OPTION_MODEL_ID": "NousResearch/Nous-Hermes-Llama2-13b",
            "SERVING_LOAD_MODELS": "test::MPI=/opt/ml/model",
            "OPTION_ROLLING_BATCH": "auto",
            "OPTION_TGI_COMPAT": "true"
        }
        for key, value in envs.items():
            os.environ[key] = value
        huggingface.get_rolling_batch_class_from_str = override_rolling_batch
        handler = TestHandler(huggingface)
        self.assertEqual(handler.serving_properties["model_id"],
                         envs["OPTION_MODEL_ID"])
        self.assertEqual(handler.serving_properties["rolling_batch"],
                         envs["OPTION_ROLLING_BATCH"])
        inputs = [{
            "inputs": "The winner of oscar this year is",
            "parameters": {
                "max_new_tokens": 50
            }
        }, {
            "inputs": "A little redhood is",
            "parameters": {
                "min_new_tokens": 51,
                "max_new_tokens": 256
            }
        }]
        result = handler.inference_rolling_batch(inputs)
        self.assertEqual(len(result), len(inputs))
        self.assertTrue(len(result[1]) > len(result[0]))
        # TGI compat tests
        self.assertTrue(json.loads(result[0]), list)
        self.assertTrue(json.loads(result[1]), list)

        for key in envs.keys():
            os.environ[key] = ""

    def test_all_code_chat(self):
        model_id = "TheBloke/Llama-2-7B-Chat-fp16"
        huggingface.get_rolling_batch_class_from_str = override_rolling_batch
        handler = TestHandler(huggingface)
        inputs = [{
            "inputs":
            "<|system|>You are a helpful assistant.</s><|user|>What is deep learning?</s>",
            "parameters": {
                "max_new_tokens": 50
            }
        }, {
            "inputs":
            "<|system|>You are a friendly chatbot who always responds in the style of a pirate</s><|user|>How many helicopters can a human eat in one sitting?</s>",
            "parameters": {
                "max_new_tokens": 50
            }
        }]
        serving_properties = {
            "engine": "Python",
            "rolling_batch": "auto",
            "model_id": model_id
        }
        result = handler.inference_rolling_batch(
            inputs, serving_properties=serving_properties)
        self.assertEqual(len(result), len(inputs))

    def test_with_env_chat(self):
        envs = {
            "OPTION_MODEL_ID": "TheBloke/Llama-2-7B-Chat-fp16",
            "SERVING_LOAD_MODELS": "test::MPI=/opt/ml/model",
            "OPTION_ROLLING_BATCH": "auto"
        }
        for key, value in envs.items():
            os.environ[key] = value
        huggingface.get_rolling_batch_class_from_str = override_rolling_batch
        handler = TestHandler(huggingface)
        self.assertEqual(handler.serving_properties["model_id"],
                         envs["OPTION_MODEL_ID"])
        self.assertEqual(handler.serving_properties["rolling_batch"],
                         envs["OPTION_ROLLING_BATCH"])
        inputs = [{
            "inputs":
            "<|system|>You are a helpful assistant.</s><|user|>What is deep learning?</s>",
            "parameters": {
                "max_new_tokens": 50
            }
        }, {
            "inputs":
            "<|system|>You are a friendly chatbot who always responds in the style of a pirate</s><|user|>How many helicopters can a human eat in one sitting?</s>",
            "parameters": {
                "min_new_tokens": 51,
                "max_new_tokens": 256
            }
        }]
        result = handler.inference_rolling_batch(inputs)
        self.assertEqual(len(result), len(inputs))
        self.assertTrue(len(result[1]) > len(result[0]))

        for key in envs.keys():
            os.environ[key] = ""

    def test_exception_handling(self):
        huggingface.get_rolling_batch_class_from_str = override_rolling_batch_with_exception
        model_id = "NousResearch/Nous-Hermes-Llama2-13b"
        handler = TestHandler(huggingface)
        inputs = [{
            "inputs": "The winner of oscar this year is",
            "parameters": {
                "min_new_tokens": 100,
                "max_new_tokens": 256,
            }
        }, {
            "inputs": "Hello world",
            "parameters": {
                "min_new_tokens": 100,
                "max_new_tokens": 512,
            }
        }]
        serving_properties = {
            "engine": "Python",
            "rolling_batch": "auto",
            "model_id": model_id
        }
        result = handler.inference_rolling_batch(
            inputs, serving_properties=serving_properties)
        for key, value in result.items():
            final_dict = json.loads(value)
            self.assertEqual(final_dict["details"]["finish_reason"], 'error')
        # test streaming
        inputs = [{
            "inputs": "The winner of oscar this year is",
            "parameters": {
                "min_new_tokens": 100,
                "max_new_tokens": 256,
            },
            "stream": True,
        }, {
            "inputs": "Hello world",
            "parameters": {
                "min_new_tokens": 100,
                "max_new_tokens": 512,
            },
            "stream": True,
        }]
        result = handler.inference_rolling_batch(
            inputs, serving_properties=serving_properties)
        for _, value in result.items():
            final_dict = json.loads(value.splitlines()[-1])
            self.assertEqual(final_dict["details"]["finish_reason"], 'error')
