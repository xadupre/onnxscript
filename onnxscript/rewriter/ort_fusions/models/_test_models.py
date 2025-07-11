# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
from __future__ import annotations

import onnx_ir as ir
import torch
import transformers
from transformers import LlamaConfig

import onnxscript.optimizer

# Create a LlamaConfig object with the desired parameters
_config = LlamaConfig(
    _name_or_path="HuggingFaceTB/SmolLM-1.7B",
    architectures=["LlamaForCausalLM"],
    attention_bias=False,
    attention_dropout=0.0,
    bos_token_id=0,
    eos_token_id=0,
    hidden_act="silu",
    hidden_size=2048,
    initializer_range=0.02,
    intermediate_size=8192,
    max_position_embeddings=2048,
    model_type="llama",
    num_attention_heads=32,
    num_hidden_layers=1,
    num_key_value_heads=32,
    pretraining_tp=1,
    rms_norm_eps=1e-05,
    rope_scaling=None,
    rope_theta=10000.0,
    tie_word_embeddings=True,
    torch_dtype="float32",
    transformers_version="4.37.2",
    use_cache=True,
    vocab_size=49152,
)

# Dimensions for inputs:
_batch_size = 1
_seq_len = 10
_hidden_size = _config.hidden_size
_num_attention_heads = _config.num_attention_heads
dim = _hidden_size // _num_attention_heads
_vocab_size = _config.vocab_size


class _SmollmTestData:
    def __init__(self):
        pass

    def get_torch_model(self):
        if not hasattr(self, "_torch_model"):
            model = transformers.LlamaForCausalLM(_config)
            model.eval()
            self._torch_model = model
        return self._torch_model

    def get_onnx_model(self) -> ir.Model:
        model = self.get_torch_model()
        inputs = self.get_inputs()
        input_names = ["input" + str(i) for i in range(len(inputs)) if inputs[i] is not None]
        exported = torch.onnx.export(
            model, inputs, input_names=input_names, dynamo=True, fallback=True
        )
        # ORT Transformer optimizations are applied after basic optimization.
        exported_model = exported.model  # type: ignore[union-attr]
        onnxscript.optimizer.optimize(exported_model)
        return exported_model

    def get_inputs(self):
        if not hasattr(self, "_inputs"):
            input_ids = torch.randint(0, _vocab_size, (_batch_size, _seq_len)).to(torch.int64)
            attention_mask = torch.ones(input_ids.shape)
            position_ids = torch.arange(0, input_ids.size(-1)).unsqueeze(0)
            self._inputs = (input_ids, attention_mask, position_ids)
        return self._inputs

    def get_torch_outputs(self):
        output = self.get_torch_model()(*self.get_inputs())
        logits = output.logits
        past_key_value = output.past_key_values[0]
        key = past_key_value[0]
        value = past_key_value[1]
        return (logits.detach().numpy(), key.detach().numpy(), value.detach().numpy())

    def get_ort_inputs(self):
        inputs = self.get_inputs()
        return {
            f"input{i}": input.numpy() for i, input in enumerate(inputs) if input is not None
        }
