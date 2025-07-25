# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
from __future__ import annotations

import unittest

import onnx_ir as ir
from parameterized import parameterized

import onnxscript
import onnxscript.rewriter.onnx_fusions as onnx_fusions
from onnxscript.rewriter.models import _rotary_embedding_models


class OnnxFusionsTest(unittest.TestCase):
    def test_rms_normalization_fusion(self):
        opset23 = onnxscript.values.Opset("", 23)

        @onnxscript.script()
        def rms_norm_script(embedding, layernorm_weight):
            two = opset23.Constant(value_float=2.0)
            pow_1 = opset23.Pow(embedding, two)
            mean = opset23.ReduceMean(pow_1, [-1], keepdims=1, noop_with_empty_axes=0)
            epsilon = opset23.Constant(value_float=1e-05)
            add_1 = opset23.Add(mean, epsilon)
            val_244 = opset23.Sqrt(add_1)
            rsqrt = opset23.Reciprocal(val_244)
            mul_3 = opset23.Mul(embedding, rsqrt)
            mul_4 = opset23.Mul(layernorm_weight, mul_3)
            return mul_4

        rms_norm_model_proto = rms_norm_script.to_model_proto(
            input_types=[onnxscript.FLOAT[128], onnxscript.FLOAT[128]],
            output_types=[onnxscript.FLOAT[128]],
        )
        model = ir.serde.deserialize_model(rms_norm_model_proto)
        onnx_fusions.fuse(model, debug=True)
        self.assertEqual(model.graph.node(-1).op_type, "RMSNormalization")

    @parameterized.expand(
        [
            (
                "test_case_1",
                _rotary_embedding_models.test_case_1,
            ),
            (
                "test_case_2",
                _rotary_embedding_models.test_case_2,
            ),
        ]
    )
    def test_rotary_embedding_fusion(self, _: str, test_data_constructor):
        test = test_data_constructor()
        for opset_version in [22, 23]:
            model: ir.Model = test.get_onnx_model()
            model.graph.opset_imports[""] = opset_version
            onnxscript.optimizer.optimize(model)
            onnx_fusions.fuse(model)
            op_types = [n.op_type for n in model.graph]
            if opset_version == 22:
                self.assertNotIn("RotaryEmbedding", op_types)
            else:
                self.assertIn("RotaryEmbedding", op_types)


if __name__ == "__main__":
    unittest.main()
