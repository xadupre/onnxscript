# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------
from __future__ import annotations

import argparse
import multiprocessing
import os
import platform
import re
import subprocess
import sys
import time
from typing import Any, Sequence

import numpy as np
import onnx


def get_parsed_args(
    name: str,
    description: str | None = None,
    epilog: str | None = None,
    new_args: list[str] | None = None,
    **kwargs: dict[str, tuple[int | str | float, str]],
) -> dict[str, Any]:
    """
    Returns parsed arguments for examples in this package.

    Args:
        name: script name
        scenarios: list of available scenarios
        description: parser description
        epilog: text at the end of the parser
        number: default value for number parameter
        repeat: default value for repeat parameter
        warmup: default value for warmup parameter
        sleep: default value for sleep parameter
        expose: if empty, keeps all the parameters,
            if not None, only publish kwargs contains, otherwise the list
            of parameters to publish separated by a comma
        new_args: args to consider or None to take `sys.args`
        kwargs: additional parameters,
            example: `n_trees=(10, "number of trees to train")`

    Returns:
        interpreted parameters in a dictionary
    """
    parser = argparse.ArgumentParser(
        prog=name,
        description=description or f"Available options for {name}.py.",
        epilog=epilog or "",
    )
    for k, v in kwargs.items():
        parser.add_argument(
            f"--{k}",
            help=f"{v[1]}, default is {v[0]}",
            type=type(v[0]),
            default=v[0],
        )

    parsed = parser.parse_args(args=new_args)
    return {k: getattr(parsed, k) for k in kwargs}


class BenchmarkError(RuntimeError):
    pass


def get_machine() -> dict[str, Any]:
    """Returns the machine specification."""
    cpu: dict[str, Any] = dict(
        machine=str(platform.machine()),
        processor=str(platform.processor()),
        version=str(sys.version),
        cpu=int(multiprocessing.cpu_count()),
        executable=str(sys.executable),
    )
    try:
        import torch.cuda
    except ImportError:
        return cpu

    cpu["has_cuda"] = bool(torch.cuda.is_available())
    if cpu["has_cuda"]:
        cpu["capability"] = torch.cuda.get_device_capability(0)
        cpu["device_name"] = str(torch.cuda.get_device_name(0))
    return cpu


def _cmd_line(script_name: str, **kwargs: dict[str, Any]) -> list[str]:
    args = [sys.executable, "-m", script_name]
    for k, v in kwargs.items():
        args.append(f"--{k}")
        args.append(str(v))
    return args


def _extract_metrics(text: str) -> dict[str, str]:
    reg = re.compile(":(.*?),(.*.?);")
    res = reg.findall(text)
    if len(res) == 0:
        return {}
    return dict(res)


def _make_prefix(script_name: str, index: int) -> str:
    name = os.path.splitext(script_name)[0]
    return f"{name}_dort_c{index}_"


def run_benchmark(
    script_name: str,
    configs: list[dict[str, Any]],
    verbose: int = 0,
    stop_if_exception: bool = True,
    dump: bool = False,
) -> list[dict[str, Any]]:
    """
    Runs a script multiple times and extract information from the output
    following the pattern ``:<metric>,<value>;``.

    Args:
        script_name: python script to run
        configs: list of execution to do
        stop_if_exception: stop if one experiment failed, otherwise continue
        verbose: use tqdm to follow the progress
        dump: dump onnx file

    Returns:
        values
    """
    if verbose:
        from tqdm import tqdm

        loop = tqdm(configs)
    else:
        loop = configs

    data: list[dict[str, Any]] = []
    for i, config in enumerate(loop):
        cmd = _cmd_line(script_name, **config)

        if dump:
            os.environ["ONNXRT_DUMP_PATH"] = _make_prefix(script_name, i)
        else:
            os.environ["ONNXRT_DUMP_PATH"] = ""
        if verbose > 3:
            print(f"[run_benchmark] cmd={cmd if isinstance(cmd, str) else ' '.join(cmd)}")
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        res = p.communicate()
        out, err = res
        sout = out.decode("utf-8", errors="ignore")
        serr = err.decode("utf-8", errors="ignore")

        if "ONNXRuntimeError" in serr or "ONNXRuntimeError" in sout:
            if stop_if_exception:
                raise RuntimeError(
                    f"Unable to continue with config {config} due to the "
                    f"following error\n{serr}"
                    f"\n----OUTPUT--\n{sout}"
                )

        metrics = _extract_metrics(sout)
        if len(metrics) == 0:
            if stop_if_exception:
                raise BenchmarkError(
                    f"Unable (2) to continue with config {config}, no metric was "
                    f"collected.\n--ERROR--\n{serr}\n--OUTPUT--\n{sout}"
                )
            else:
                metrics = {}
        metrics.update(config)
        metrics["ERROR"] = serr
        metrics["OUTPUT"] = sout
        metrics["CMD"] = f"[{' '.join(cmd)}]"
        data.append(metrics)
        if verbose > 5:
            print("--------------- ERROR")
            print(serr)
        if verbose >= 10:
            print("--------------- OUTPUT")
            print(sout)

    return data


def common_export(
    model: Any,
    inputs: Sequence[Any],
    exporter: str = "dynamo",
    target_opset: int = 18,
    folder: str = "",
    filename: str = "model.onnx",
    dynamic_shapes: Any | None = None,
    verbose: int = 0,
    optimization: str | None = None,
    stats: dict[str, Any] | None = None,
):
    """
    Exports a model into a folder.

    Args:
        model: model
        exporter: script, dynamo
        folder: folder to export into
        filename: onnx filename
        inputs: inputs
        dynamic_shapes: dynamic shapes
        target_opset: target opset
        optimization: optimization scenario
        verbose: verbosity
        stats: if not None, populates this
            dictionary with statistics about time

    Returns:
        onnx proto

    """
    import torch.onnx

    if folder:
        if not os.path.exists(folder):
            os.mkdir(folder)
        filename = os.path.join(folder, filename)

    if verbose:
        print(f"[common_export] start exporting with {exporter!r} in {filename!r}")
    begin = time.perf_counter()
    if exporter == "script":
        torch.onnx.export(
            model,
            inputs,
            filename,
            do_constant_folding=False,
            input_names=[f"input{i}" for i in range(len(inputs))],
            opset_version=target_opset,
        )
    elif exporter == "dynamo":
        with torch.no_grad():
            prog = torch.onnx.dynamo_export(model, *inputs)
        onx = prog.model_proto
        with open(filename, "wb") as f:
            f.write(onx.SerializeToString())
    else:
        raise AssertionError(f"Unknown exporter {exporter!r}")

    if stats is not None:
        stats["export_time"] = time.perf_counter() - begin

    if verbose:
        print(f"[common_export] exporter done in {time.perf_counter() - begin}s")
        print(f"[common_export] size of the export: {os.stat(filename).st_size / 2**20} Mb")

    with open(filename, "rb") as f:
        onx = onnx.load(filename)

    if optimization:
        if verbose:
            print(f"[common_export] start optimization with {optimization!r}")
        begin = time.perf_counter()
        onx = optimize_model_proto(onx, optimization, verbose=verbose, stats=stats)
        end = time.perf_counter() - begin
        if stats is not None:
            stats["optimization_time"] = end
        if verbose:
            print(f"[common_export] optimization done in {end}")
            print(f"[common_export] saves the model in {filename!r}")
            begin = time.perf_counter()

        with open(filename, "wb") as f:
            f.write(onx.SerializeToString())
        if verbose:
            print(f"[common_export] done saving in {time.perf_counter() - begin}")

    return onx


def optimize_model_proto(
    model_proto: onnx.ModelProto,
    optimization: str | None = None,
    verbose: int = 0,
    stats: dict[str, Any] | None = None,
):
    """
    Optimizes a model given some scenarios.

    Args:
        model_proto: ModelProto
        optimization: comma separated value
        verbose: verbosity
        stats: if not None, populates this dictionary with statistics

    Returns:
        optmized model
    """
    if not optimization:
        return model_proto

    for value in optimization.split(","):

        if verbose:
            print(f"[optimize_model_proto] start {value}")

        begin = time.perf_counter()
        if value == "optimize":

            import onnxscript.optimizer

            model_proto = onnxscript.optimizer.optimize(
                model_proto,
                num_iterations=2,
                onnx_shape_inference=False,
            )

        elif value == "rewrite":
            import onnxscript.rewriter

            model_proto = onnxscript.rewriter.rewrite(model_proto)

        elif value == "inline":
            import onnx.inliner

            model_proto = onnx.inliner.inline_local_functions(model_proto)

        else:
            raise AssertionError(
                f"Optimization step {value!r} is not implemented in {optimization!r}"
            )

        end = time.perf_counter() - begin
        if stats:
            stats[f"opt_{value}_time"] = end
        if verbose:
            print(f"[optimize_model_proto] {value} done in {end}")

    return model_proto


def run_inference(
    model: Any,
    example_inputs: Sequence[Any],
    warmup: int = 5,
    repeat: int = 5,
    verbose: int = 0,
) -> dict[str, Any]:
    """
    Runs multiple times the same inference.

    Args:
        model: torch model to run
        example_inputs: dummy inputs
        warmup: number of iterations to warmup
        repeat: number of iterations to repeat
        verbose: verbosity

    Returns:
        statistcs
    """
    if verbose:
        print(f"[run_inference] start {warmup} warmup iterations")

    stats = {}
    iterations = []
    begin = time.perf_counter()
    for i in range(warmup):
        t0 = time.perf_counter()
        model(*example_inputs[i % len(example_inputs)])
        iterations.append(time.perf_counter() - t0)
    end = time.perf_counter() - begin
    stats["warmup"] = warmup
    stats["warmup_time"] = end
    stats["warmup_iter"] = iterations

    if verbose:
        print(f"[run_inference] warmup done in {time.perf_counter() - begin}")
        print(f"[run_inference] start {repeat} iterations")

    iterations = []
    begin = time.perf_counter()
    for i in range(warmup):
        t0 = time.perf_counter()
        model(*example_inputs[i % len(example_inputs)])
        iterations.append(time.perf_counter() - t0)
    end = time.perf_counter() - begin
    stats["repeat"] = repeat
    stats["repeat_time"] = end
    stats["repeat_iter"] = iterations

    if verbose:
        print(f"[run_inference] measure done in {time.perf_counter() - begin}")

    return stats


class WrapInferenceSessionForTorch:

    def __init__(self, sess: "onnxruntime.InferenceSession"):  # noqa: F821
        import onnxruntime
        import torch
        from onnxruntime.capi import _pybind_state as ORTC  # noqa: N812

        self.sess = sess
        self.input_names = [i.name for i in sess.get_inputs()]
        self.output_names = [i.name for i in sess.get_outputs()]
        self.bind = onnxruntime.SessionIOBinding(sess._sess)
        self.OrtValue = ORTC.OrtValue
        self.ORTC = ORTC
        self.torch = torch
        self.run_options = onnxruntime.RunOptions()

        self.TORCH_DTYPE_TO_NUMPY_DTYPE = {
            torch.float16: np.float16,
            torch.float32: np.float32,
            torch.float64: np.float64,
            torch.uint8: np.uint8,
            torch.int8: np.int8,
            torch.int16: np.int16,
            torch.int32: np.int32,
            torch.int64: np.int64,
            torch.bool: np.bool_,
        }

        DEVICES = {
            -1: ORTC.OrtDevice(ORTC.OrtDevice.cpu(), ORTC.OrtDevice.default_memory(), 0)
        }

        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                DEVICES[i] = ORTC.OrtDevice(
                    ORTC.OrtDevice.cuda(), ORTC.OrtDevice.default_memory(), i
                )

        self.DEVICES = DEVICES

    def _get_ortvalues_from_torch_tensors(
        self,
        tensors: tuple["torch.Tensor", ...],  # noqa: F821
        n_outputs: int,
        log_set: list[Any] | None = None,
    ) -> tuple[tuple["torch.Tensor", ...], tuple["OrtDevice", ...], Any]:  # noqa: F821

        ortvalues = self.ORTC.OrtValueVector()
        ortvalues.reserve(len(tensors))
        dtypes = []
        shapes = []
        data_ptrs = []
        devices = []

        max_device = -1
        assert isinstance(max_device, int), f"unexpected type for device={max_device!r}"
        assert tensors is not None, "tensors cannot be None"
        new_tensors = []
        for tensor in tensors:
            assert isinstance(tensor, self.torch.Tensor), f"Unexpected type {type(tensor)}"
            dtypes.append(self.TORCH_DTYPE_TO_NUMPY_DTYPE[tensor.dtype])
            shapes.append(tensor.size())
            data_ptrs.append(tensor.data_ptr())
            d = tensor.get_device()
            devices.append(self.DEVICES[d])
            new_tensors.append(tensor)
            max_device = max(max_device, tensor.get_device())

        ortvalues.push_back_batch(new_tensors, data_ptrs, dtypes, shapes, devices)
        output_devices = []
        for _ in range(n_outputs):
            dev = self.DEVICES[max_device]
            output_devices.append(dev)

        return ortvalues, output_devices

    def _ortvalues_to_torch_tensor(
        self, ortvalues: "onnxruntime.OrtValueVector"  # noqa: F821
    ) -> tuple["torch.Tensor", ...]:  # noqa: F821
        if len(ortvalues) == 0:
            return tuple()

        from torch._C import _from_dlpack

        if all(map(lambda i: ortvalues[i].has_value(), range(len(ortvalues)))):  # noqa: C417
            res = ortvalues.to_dlpacks(_from_dlpack)
        else:
            res = []
            for i in range(len(ortvalues)):
                res.append(
                    _from_dlpack(ortvalues[i].to_dlpack())
                    if ortvalues[i].has_value()
                    else None
                )
        return tuple(res)

    def run(self, output_names, feeds):
        inputs = [feeds[i] for i in self.input_names]
        return self.run_dlpack(*inputs, output_names=output_names)

    def run_dlpack(self, *inputs, output_names=None):

        if output_names is None:
            output_names = self.output_names
        ortvalues, output_devices = self._get_ortvalues_from_torch_tensors(
            inputs, len(output_names)
        )

        ort_outputs = self.ORTC.OrtValueVector()
        self.sess.run_with_ortvaluevector(
            self.run_options,
            self.input_names,
            ortvalues,
            output_names,
            ort_outputs,
            output_devices,
        )
        pth_outputs = self._ortvalues_to_torch_tensor(ort_outputs)
        return pth_outputs


def run_onnx_inference(
    model: onnx.ModelProto,
    example_inputs: Sequence[Any],
    warmup: int = 5,
    repeat: int = 5,
    verbose: int = 0,
    ort_optimize: bool = True,
) -> dict[str, Any]:
    """
    Runs multiple times the same inference with onnxruntime.

    Args:
        model: torch model to run
        example_inputs: dummy inputs
        warmup: number of iterations to warmup
        repeat: number of iterations to repeat
        verbose: verbosity
        ort_optimize: enable, disable onnxruntime optimizations

    Returns:
        statistcs
    """
    stats = {}
    device = example_inputs[0][0].get_device()
    providers = (
        ["CUDAExecutionProvider", "CPUExecutionProvider"]
        if device >= 0
        else ["CPUExecutionProvider"]
    )
    stats["providers"] = ",".join(providers)
    if verbose:
        print(f"[run_inference] create session with providers {providers!r}")

    begin = time.perf_counter()
    import onnxruntime

    so = onnxruntime.SessionOptions()
    if ort_optimize:
        so.add_session_config_entry("session.disable_aot_function_inlining", "0")
        so.graph_optimization_level = onnxruntime.GraphOptimizationLevel.ORT_ENABLE_ALL
    else:
        so.add_session_config_entry("session.disable_aot_function_inlining", "1")
        so.graph_optimization_level = onnxruntime.GraphOptimizationLevel.ORT_DISABLE_ALL

    sess = onnxruntime.InferenceSession(model.SerializeToString(), so, providers)
    wrapped_sess = WrapInferenceSessionForTorch(sess)

    end = time.perf_counter() - begin
    stats["ort_session_create_time"] = end
    if verbose:
        print(f"[run_inference] created session in {end}")
        print(f"[run_inference] start {warmup} warmup iterations")

    iterations = []
    begin = time.perf_counter()
    for i in range(warmup):
        t0 = time.perf_counter()
        wrapped_sess.run_dlpack(*example_inputs[i % len(example_inputs)])
        iterations.append(time.perf_counter() - t0)
    end = time.perf_counter() - begin
    stats["warmup"] = warmup
    stats["warmup_time"] = end / warmup
    stats["warmup_iter"] = iterations

    if verbose:
        print(f"[run_inference] warmup done in {time.perf_counter() - begin}")
        print(f"[run_inference] start {repeat} iterations")

    iterations = []
    begin = time.perf_counter()
    for i in range(repeat):
        t0 = time.perf_counter()
        wrapped_sess.run_dlpack(*example_inputs[i % len(example_inputs)])
        iterations.append(time.perf_counter() - t0)
    end = time.perf_counter() - begin
    stats["repeat"] = repeat
    stats["repeat_time"] = end / repeat
    stats["repeat_iter"] = iterations

    if verbose:
        print(f"[run_inference] measure done in {time.perf_counter() - begin}")

    return stats
