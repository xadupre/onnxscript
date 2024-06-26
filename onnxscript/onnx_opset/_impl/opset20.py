# --------------------------------------------------------------------------
# ⚠️ WARNING - AUTO-GENERATED CODE - DO NOT EDIT ⚠️
# ⚙️ Generated by 'python -m opgen'
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------
# pylint: disable=W0221,W0222,R0901,W0237
# mypy: disable-error-code=override
# ruff: noqa: N801,E741
# ruff: noqa: D214,D402,D405,D411,D412,D416,D417
# --------------------------------------------------------------------------

from __future__ import annotations

from typing import Optional, Tuple, TypeVar, Union

from onnx import TensorProto
from onnx.defs import get_schema
from typing_extensions import TypeAlias

from onnxscript.onnx_opset._impl.opset19 import Opset19
from onnxscript.onnx_types import (
    BFLOAT16,
    BOOL,
    COMPLEX64,
    COMPLEX128,
    DOUBLE,
    FLOAT,
    FLOAT8E4M3FN,
    FLOAT8E4M3FNUZ,
    FLOAT8E5M2,
    FLOAT8E5M2FNUZ,
    FLOAT16,
    INT8,
    INT16,
    INT32,
    INT64,
    STRING,
    UINT8,
    UINT16,
    UINT32,
    UINT64,
)
from onnxscript.values import Op, Opset


class Opset20(Opset19):
    def __new__(cls):
        return Opset.__new__(cls, "", 20)

    T1_AffineGrid = TypeVar("T1_AffineGrid", BFLOAT16, DOUBLE, FLOAT, FLOAT16)

    T2_AffineGrid: TypeAlias = INT64

    def AffineGrid(
        self, theta: T1_AffineGrid, size: T2_AffineGrid, *, align_corners: int = 0
    ) -> T1_AffineGrid:
        r"""[🌐 AffineGrid(20)](https://onnx.ai/onnx/operators/onnx__AffineGrid.html#affinegrid-20 "Online Documentation")


        Generates a 2D or 3D flow field (sampling grid), given a batch of affine matrices theta
        (https://pytorch.org/docs/stable/generated/torch.nn.functional.affine_grid.html).
        An affine matrix `theta` is applied to a position tensor represented in its homogeneous expression. Here is an example in 3D:
        ::

            [r00, r01, r02, t0]   [x]   [x']
            [r10, r11, r12, t1] * [y] = [y']
            [r20, r21, r22, t2]   [z]   [z']
            [0,   0,   0,   1 ]   [1]   [1 ]


        where `(x, y, z)` is the position in the original space, `(x', y', z')` is the position in the output space.
        The last row is always `[0, 0, 0, 1]` and is not stored in the affine matrix. Therefore we have `theta` of shape `(N, 2, 3)` for 2D or `(N, 3, 4)` for 3D.

        Input `size` is used to define grid of positions evenly spaced in the original 2D or 3D space, with dimensions ranging from `-1` to `1`.
        The output `grid` contains positions in the output space.

        When `align_corners=1`, consider `-1` and `1` to refer to the centers of the corner pixels (mark `v` in illustration).
        ::

            v            v            v            v
            |-------------------|------------------|
            -1                  0                  1


        When `align_corners=0`, consider `-1` and `1` to refer to the outer edge of the corner pixels.
        ::

                v        v         v         v
            |------------------|-------------------|
            -1                 0                   1




        Args:
            theta: (non-differentiable) input batch of affine matrices with shape (N, 2,
                3) for 2D or (N, 3, 4) for 3D

            size: (non-differentiable) the target output image size (N, C, H, W) for 2D
                or (N, C, D, H, W) for 3D

            align_corners: if align_corners=1, consider -1 and 1 to refer to the centers
                of the corner pixels. if align_corners=0, consider -1 and 1 to refer to
                the outer edge the corner pixels.
        """

        schema = get_schema("AffineGrid", 20, "")
        op = Op(self, "AffineGrid", schema)
        return op(*self._prepare_inputs(schema, theta, size), align_corners=align_corners)

    T1_ConstantOfShape: TypeAlias = INT64

    T2_ConstantOfShape: TypeAlias = Union[
        BFLOAT16,
        BOOL,
        DOUBLE,
        FLOAT,
        FLOAT16,
        FLOAT8E4M3FN,
        FLOAT8E4M3FNUZ,
        FLOAT8E5M2,
        FLOAT8E5M2FNUZ,
        INT16,
        INT32,
        INT64,
        INT8,
        UINT16,
        UINT32,
        UINT64,
        UINT8,
    ]

    def ConstantOfShape(
        self, input: T1_ConstantOfShape, *, value: Optional[TensorProto] = None
    ) -> T2_ConstantOfShape:
        r"""[🌐 ConstantOfShape(20)](https://onnx.ai/onnx/operators/onnx__ConstantOfShape.html#constantofshape-20 "Online Documentation")


        Generate a tensor with given value and shape.


        Args:
            input: 1D tensor. The shape of the expected output tensor. If empty tensor
                is given, the output would be a scalar. All values must be >= 0.

            value: (Optional) The value of the output elements.Should be a one-element
                tensor. If not specified, it defaults to a tensor of value 0 and
                datatype float32
        """

        schema = get_schema("ConstantOfShape", 20, "")
        op = Op(self, "ConstantOfShape", schema)
        return op(*self._prepare_inputs(schema, input), value=value)

    T1_DFT = TypeVar("T1_DFT", BFLOAT16, DOUBLE, FLOAT, FLOAT16)

    T2_DFT = TypeVar("T2_DFT", INT32, INT64)

    def DFT(
        self,
        input: T1_DFT,
        dft_length: Optional[T2_DFT] = None,
        axis: Optional[INT64] = None,
        *,
        inverse: int = 0,
        onesided: int = 0,
    ) -> T1_DFT:
        r"""[🌐 DFT(20)](https://onnx.ai/onnx/operators/onnx__DFT.html#dft-20 "Online Documentation")

        Computes the discrete Fourier Transform (DFT) of the input.

        Assuming the input has shape `[M, N]`, where `N` is the dimension over which the
        DFT is computed and `M` denotes the conceptual "all other dimensions,"
        the DFT `y[m, k]` of shape `[M, N]` is defined as

        $$y[m, k] = \sum_{n=0}^{N-1} e^{-2 \pi j \frac{k n}{N} } x[m, n] ,$$

        and the inverse transform is defined as

        $$x[m, n] = \frac{1}{N} \sum_{k=0}^{N-1} e^{2 \pi j \frac{k n}{N} } y[m, k] ,$$

        where $j$ is the imaginary unit.

        The actual shape of the output is specified in the "output" section.

        Reference: https://docs.scipy.org/doc/scipy/tutorial/fft.html


        Args:
            input: (non-differentiable) For real input, the following shape is expected:
                `[signal_dim0][signal_dim1][signal_dim2]...[signal_dimN][1]`. For
                complex input, the following shape is expected:
                `[signal_dim0][signal_dim1][signal_dim2]...[signal_dimN][2]`. The final
                dimension represents the real and imaginary parts of the value in that
                order.

            dft_length: (optional, non-differentiable) The length of the signal as a
                scalar. If greater than the axis dimension, the signal will be
                zero-padded up to `dft_length`. If less than the axis dimension, only
                the first `dft_length` values will be used as the signal.

            axis: (optional, non-differentiable) The axis as a scalar on which to
                perform the DFT. Default is `-2` (last signal axis). Negative value
                means counting dimensions from the back. Accepted range is $[-r, -2]
                \cup [0, r-2]$ where `r = rank(input)`. The last dimension is for
                representing complex numbers and thus is an invalid axis.

            inverse: Whether to perform the inverse discrete Fourier Transform. Default
                is 0, which corresponds to `false`.

            onesided: If `onesided` is `1` and input is real, only values for `k` in
                `[0, 1, 2, ..., floor(n_fft/2) + 1]` are returned because the
                real-to-complex Fourier transform satisfies the conjugate symmetry,
                i.e., `X[m, k] = X[m, n_fft-k]*`, where `m` denotes "all other
                dimensions" DFT was not applied on. If the input tensor is complex,
                onesided output is not possible. Value can be `0` or `1`. Default is
                `0`.
        """

        schema = get_schema("DFT", 20, "")
        op = Op(self, "DFT", schema)
        return op(
            *self._prepare_inputs(schema, input, dft_length, axis),
            inverse=inverse,
            onesided=onesided,
        )

    T_Gelu = TypeVar("T_Gelu", BFLOAT16, DOUBLE, FLOAT, FLOAT16)

    def Gelu(self, X: T_Gelu, *, approximate: str = "none") -> T_Gelu:
        r"""[🌐 Gelu(20)](https://onnx.ai/onnx/operators/onnx__Gelu.html#gelu-20 "Online Documentation")


        Gelu takes one input data (Tensor<T>) and produces one
        output data (Tensor<T>) where the gaussian error linear units function,
        $y = 0.5 * x * (1 + erf(x/sqrt(2)))$ is applied to the tensor elementwise.
        If the attribute "approximate" is set to "tanh", the function estimation,
        $y = 0.5 * x * (1 + Tanh(sqrt(2/\pi) * (x + 0.044715 * x^3)))$ is used and applied
        to the tensor elementwise.



        Args:
            X: (differentiable) Input tensor

            approximate: Gelu approximation algorithm: `"tanh"`,
                `"none"`(default).`"none"`: do not use approximation.`"tanh"`: use tanh
                approximation.
        """

        schema = get_schema("Gelu", 20, "")
        op = Op(self, "Gelu", schema)
        return op(*self._prepare_inputs(schema, X), approximate=approximate)

    T1_GridSample = TypeVar(
        "T1_GridSample",
        BOOL,
        COMPLEX128,
        COMPLEX64,
        DOUBLE,
        FLOAT,
        FLOAT16,
        INT16,
        INT32,
        INT64,
        INT8,
        STRING,
        UINT16,
        UINT32,
        UINT64,
        UINT8,
    )

    T2_GridSample = TypeVar("T2_GridSample", DOUBLE, FLOAT, FLOAT16)

    def GridSample(
        self,
        X: T1_GridSample,
        grid: T2_GridSample,
        *,
        align_corners: int = 0,
        mode: str = "linear",
        padding_mode: str = "zeros",
    ) -> T1_GridSample:
        r"""[🌐 GridSample(20)](https://onnx.ai/onnx/operators/onnx__GridSample.html#gridsample-20 "Online Documentation")


        Given an input `X` and a flow-field `grid`, computes the output `Y` using `X` values and pixel locations from the `grid`.
        For spatial input `X` with shape (N, C, H, W), the `grid` will have shape (N, H_out, W_out, 2),
        the output `Y` will have shape (N, C, H_out, W_out). For volumetric input `X` with shape (N, C, D, H, W),
        the `grid` will have shape (N, D_out, H_out, W_out, 3), the output `Y` will have shape (N, C, D_out, H_out, W_out).
        More generally, for an input `X` of rank r+2 with shape (N, C, d1, d2, ..., dr),
        the `grid` will have shape (N, D1_out, D2_out, ..., Dr_out, r), the output `Y` will have shape (N, C, D1_out, D2_out, ..., Dr_out).

        The tensor `X` contains values at centers of square pixels (voxels, etc) locations such as (n, c, d1_in, d2_in, ..., dr_in).
        The (n, d1_out, d2_out, ..., dr_out, :) values from the tensor `grid` are the normalized positions for interpolating the values
        at the (n, c, d1_out, d2_out, ..., dr_out) locations from the output tensor `Y` using a specified interpolation method (the mode)
        and a padding mode (for `grid` positions falling outside the 2-dimensional image).

        For example, the values in `grid[n, h_out, w_out, :]` are size-2 vectors specifying normalized positions in the 2-dimensional space of `X`.
        They are used to interpolate output values of `Y[n, c, h_out, w_out]`.

        The GridSample operator is often used in doing grid generator and sampler in the
        [Spatial Transformer Networks](https://arxiv.org/abs/1506.02025).
        See also in [torch.nn.functional.grid_sample](https://pytorch.org/docs/stable/generated/torch.nn.functional.grid_sample.html).


        Args:
            X: (differentiable) Input tensor of rank r+2 that has shape (N, C, D1, D2,
                ..., Dr), where N is the batch size, C is the number of channels, D1,
                D2, ..., Dr are the spatial dimensions.

            grid: (non-differentiable) Input offset of shape (N, D1_out, D2_out, ...,
                Dr_out, r), where D1_out, D2_out, ..., Dr_out are the spatial dimensions
                of the grid and output, and r is the number of spatial dimensions. Grid
                specifies the sampling locations normalized by the input spatial
                dimensions. Therefore, it should have most values in the range of [-1,
                1]. If the grid has values outside the range of [-1, 1], the
                corresponding outputs will be handled as defined by padding_mode.
                Following computer vision convention, the coordinates in the length-r
                location vector are listed from the innermost tensor dimension to the
                outermost, the opposite of regular tensor indexing.

            align_corners: If align_corners=1, the extrema (-1 and 1) are considered as
                referring to the center points of the input's corner pixels (voxels,
                etc.). If align_corners=0, they are instead considered as referring to
                the corner points of the input's corner pixels (voxels, etc.), making
                the sampling more resolution agnostic.

            mode: Three interpolation modes: linear (default), nearest and cubic. The
                "linear" mode includes linear and N-linear interpolation modes depending
                on the number of spatial dimensions of the input tensor (i.e. linear for
                1 spatial dimension, bilinear for 2 spatial dimensions, etc.). The
                "cubic" mode also includes N-cubic interpolation modes following the
                same rules. The "nearest" mode rounds to the nearest even index when the
                sampling point falls halfway between two indices.

            padding_mode: Support padding modes for outside grid values:
                `zeros`(default), `border`, `reflection`. zeros: use 0 for out-of-bound
                grid locations, border: use border values for out-of-bound grid
                locations, reflection: use values at locations reflected by the border
                for out-of-bound grid locations. If index 0 represents the margin pixel,
                the reflected value at index -1 will be the same as the value at index
                1. For location far away from the border, it will keep being reflected
                until becoming in bound. If pixel location x = -3.5 reflects by border
                -1 and becomes x' = 1.5, then reflects by border 1 and becomes x'' =
                0.5.
        """

        schema = get_schema("GridSample", 20, "")
        op = Op(self, "GridSample", schema)
        return op(
            *self._prepare_inputs(schema, X, grid),
            align_corners=align_corners,
            mode=mode,
            padding_mode=padding_mode,
        )

    T1_ImageDecoder: TypeAlias = UINT8

    T2_ImageDecoder: TypeAlias = UINT8

    def ImageDecoder(
        self, encoded_stream: T1_ImageDecoder, *, pixel_format: str = "RGB"
    ) -> T2_ImageDecoder:
        r"""[🌐 ImageDecoder(20)](https://onnx.ai/onnx/operators/onnx__ImageDecoder.html#imagedecoder-20 "Online Documentation")

        Loads and decodes and image from a file. If it can't decode for any reason (e.g. corrupted encoded
        stream, invalid format, it will return an empty matrix).
        The following image formats are supported:
        * BMP
        * JPEG (note: Lossless JPEG support is optional)
        * JPEG2000
        * TIFF
        * PNG
        * WebP
        * Portable image format (PBM, PGM, PPM, PXM, PNM)
        Decoded images follow a channel-last layout: (Height, Width, Channels).
        **JPEG chroma upsampling method:**
        When upsampling the chroma components by a factor of 2, the pixels are linearly interpolated so that the
        centers of the output pixels are 1/4 and 3/4 of the way between input pixel centers.
        When rounding, 0.5 is rounded down and up at alternative pixels locations to prevent bias towards
        larger values (ordered dither pattern).
        Considering adjacent input pixels A, B, and C, B is upsampled to pixels B0 and B1 so that
        ::

            B0 = round_half_down((1/4) * A + (3/4) * B)
            B1 = round_half_up((3/4) * B + (1/4) * C)


        This method,  is the default chroma upsampling method in the well-established libjpeg-turbo library,
        also referred as "smooth" or "fancy" upsampling.


        Args:
            encoded_stream: (non-differentiable) Encoded stream

            pixel_format: Pixel format. Can be one of "RGB", "BGR", or "Grayscale".
        """

        schema = get_schema("ImageDecoder", 20, "")
        op = Op(self, "ImageDecoder", schema)
        return op(*self._prepare_inputs(schema, encoded_stream), pixel_format=pixel_format)

    T1_IsInf = TypeVar(
        "T1_IsInf",
        BFLOAT16,
        DOUBLE,
        FLOAT,
        FLOAT16,
        FLOAT8E4M3FN,
        FLOAT8E4M3FNUZ,
        FLOAT8E5M2,
        FLOAT8E5M2FNUZ,
    )

    T2_IsInf: TypeAlias = BOOL

    def IsInf(
        self, X: T1_IsInf, *, detect_negative: int = 1, detect_positive: int = 1
    ) -> T2_IsInf:
        r"""[🌐 IsInf(20)](https://onnx.ai/onnx/operators/onnx__IsInf.html#isinf-20 "Online Documentation")

        Map infinity to true and other values to false.

        Args:
            X: (non-differentiable) input

            detect_negative: (Optional) Whether map negative infinity to true. Default
                to 1 so that negative infinity induces true. Set this attribute to 0 if
                negative infinity should be mapped to false.

            detect_positive: (Optional) Whether map positive infinity to true. Default
                to 1 so that positive infinity induces true. Set this attribute to 0 if
                positive infinity should be mapped to false.
        """

        schema = get_schema("IsInf", 20, "")
        op = Op(self, "IsInf", schema)
        return op(
            *self._prepare_inputs(schema, X),
            detect_negative=detect_negative,
            detect_positive=detect_positive,
        )

    T1_IsNaN = TypeVar(
        "T1_IsNaN",
        BFLOAT16,
        DOUBLE,
        FLOAT,
        FLOAT16,
        FLOAT8E4M3FN,
        FLOAT8E4M3FNUZ,
        FLOAT8E5M2,
        FLOAT8E5M2FNUZ,
    )

    T2_IsNaN: TypeAlias = BOOL

    def IsNaN(self, X: T1_IsNaN) -> T2_IsNaN:
        r"""[🌐 IsNaN(20)](https://onnx.ai/onnx/operators/onnx__IsNaN.html#isnan-20 "Online Documentation")

        Returns which elements of the input are NaN.

        Args:
            X: (non-differentiable) input
        """

        schema = get_schema("IsNaN", 20, "")
        op = Op(self, "IsNaN", schema)
        return op(*self._prepare_inputs(schema, X))

    T_ReduceMax = TypeVar(
        "T_ReduceMax",
        BFLOAT16,
        BOOL,
        DOUBLE,
        FLOAT,
        FLOAT16,
        INT32,
        INT64,
        INT8,
        UINT32,
        UINT64,
        UINT8,
    )

    def ReduceMax(
        self,
        data: T_ReduceMax,
        axes: Optional[INT64] = None,
        *,
        keepdims: int = 1,
        noop_with_empty_axes: int = 0,
    ) -> T_ReduceMax:
        r"""[🌐 ReduceMax(20)](https://onnx.ai/onnx/operators/onnx__ReduceMax.html#reducemax-20 "Online Documentation")


        Computes the max of the input tensor's elements along the provided axes. The resulting
        tensor has the same rank as the input if `keepdims` equals 1. If `keepdims` equals 0, then
        the resulting tensor has the reduced dimension pruned. Input tensors of rank zero are
        valid. Reduction over an empty set of values yields minus infinity (if supported by the datatype) or the minimum value of the data type otherwise.


        If the input data type is Boolean, the comparison should consider `False < True`.

        The above behavior is similar to numpy, with the exception that numpy defaults `keepdims`
        to `False` instead of `True`.

        Args:
            data: (differentiable) An input tensor.

            axes: (optional, non-differentiable) Optional input list of integers, along
                which to reduce. The default is to reduce over all the dimensions of the
                input tensor if 'noop_with_empty_axes' is false, else act as an Identity
                op when 'noop_with_empty_axes' is true. Accepted range is [-r, r-1]
                where r = rank(data).

            keepdims: Keep the reduced dimension or not, default 1 means keep reduced
                dimension.

            noop_with_empty_axes: Defines behavior if 'axes' is empty. Default behavior
                with 'false' is to reduce all axes. When axes is empty and this
                attribute is set to true, input tensor will not be reduced,and the
                output tensor would be equivalent to input tensor.
        """

        schema = get_schema("ReduceMax", 20, "")
        op = Op(self, "ReduceMax", schema)
        return op(
            *self._prepare_inputs(schema, data, axes),
            keepdims=keepdims,
            noop_with_empty_axes=noop_with_empty_axes,
        )

    T_ReduceMin = TypeVar(
        "T_ReduceMin",
        BFLOAT16,
        BOOL,
        DOUBLE,
        FLOAT,
        FLOAT16,
        INT32,
        INT64,
        INT8,
        UINT32,
        UINT64,
        UINT8,
    )

    def ReduceMin(
        self,
        data: T_ReduceMin,
        axes: Optional[INT64] = None,
        *,
        keepdims: int = 1,
        noop_with_empty_axes: int = 0,
    ) -> T_ReduceMin:
        r"""[🌐 ReduceMin(20)](https://onnx.ai/onnx/operators/onnx__ReduceMin.html#reducemin-20 "Online Documentation")


        Computes the min of the input tensor's elements along the provided axes. The resulting
        tensor has the same rank as the input if `keepdims` equals 1. If `keepdims` equals 0, then
        the resulting tensor has the reduced dimension pruned. Input tensors of rank zero are
        valid. Reduction over an empty set of values yields plus infinity (if supported by the datatype) or the maximum value of the data type otherwise.


        If the input data type is Boolean, the comparison should consider `False < True`.

        The above behavior is similar to numpy, with the exception that numpy defaults `keepdims`
        to `False` instead of `True`.

        Args:
            data: (differentiable) An input tensor.

            axes: (optional, non-differentiable) Optional input list of integers, along
                which to reduce. The default is to reduce over all the dimensions of the
                input tensor if 'noop_with_empty_axes' is false, else act as an Identity
                op when 'noop_with_empty_axes' is true. Accepted range is [-r, r-1]
                where r = rank(data).

            keepdims: Keep the reduced dimension or not, default 1 means keep reduced
                dimension.

            noop_with_empty_axes: Defines behavior if 'axes' is empty. Default behavior
                with 'false' is to reduce all axes. When axes is empty and this
                attribute is set to true, input tensor will not be reduced,and the
                output tensor would be equivalent to input tensor.
        """

        schema = get_schema("ReduceMin", 20, "")
        op = Op(self, "ReduceMin", schema)
        return op(
            *self._prepare_inputs(schema, data, axes),
            keepdims=keepdims,
            noop_with_empty_axes=noop_with_empty_axes,
        )

    T1_RegexFullMatch: TypeAlias = STRING

    T2_RegexFullMatch: TypeAlias = BOOL

    def RegexFullMatch(
        self, X: T1_RegexFullMatch, *, pattern: Optional[str] = None
    ) -> T2_RegexFullMatch:
        r"""[🌐 RegexFullMatch(20)](https://onnx.ai/onnx/operators/onnx__RegexFullMatch.html#regexfullmatch-20 "Online Documentation")

        RegexFullMatch performs a full regex match on each element of the input tensor. If an element fully matches the regex pattern specified as an attribute, the corresponding element in the output is True and it is False otherwise. [RE2](https://github.com/google/re2/wiki/Syntax) regex syntax is used.

        Args:
            X: (non-differentiable) Tensor with strings to match on.

            pattern: Regex pattern to match on. This must be valid RE2 syntax.
        """

        schema = get_schema("RegexFullMatch", 20, "")
        op = Op(self, "RegexFullMatch", schema)
        return op(*self._prepare_inputs(schema, X), pattern=pattern)

    T_StringConcat: TypeAlias = STRING

    def StringConcat(self, X: T_StringConcat, Y: T_StringConcat) -> T_StringConcat:
        r"""[🌐 StringConcat(20)](https://onnx.ai/onnx/operators/onnx__StringConcat.html#stringconcat-20 "Online Documentation")

        StringConcat concatenates string tensors elementwise (with NumPy-style broadcasting support)

        Args:
            X: (non-differentiable) Tensor to prepend in concatenation

            Y: (non-differentiable) Tensor to append in concatenation
        """

        schema = get_schema("StringConcat", 20, "")
        op = Op(self, "StringConcat", schema)
        return op(*self._prepare_inputs(schema, X, Y))

    T1_StringSplit: TypeAlias = STRING

    T2_StringSplit: TypeAlias = STRING

    T3_StringSplit: TypeAlias = INT64

    def StringSplit(
        self,
        X: T1_StringSplit,
        *,
        delimiter: Optional[str] = None,
        maxsplit: Optional[int] = None,
    ) -> Tuple[T2_StringSplit, T3_StringSplit]:
        r"""[🌐 StringSplit(20)](https://onnx.ai/onnx/operators/onnx__StringSplit.html#stringsplit-20 "Online Documentation")

        StringSplit splits a string tensor's elements into substrings based on a delimiter attribute and a maxsplit attribute.

        The first output of this operator is a tensor of strings representing the substrings from splitting each input string on the `delimiter` substring. This tensor has one additional rank compared to the input tensor in order to store the substrings for each input element (where the input tensor is not empty). Note that, in order to ensure the same number of elements are present in the final dimension, this tensor will pad empty strings as illustrated in the examples below. Consecutive delimiters are not grouped together and are deemed to delimit empty strings, except if the `delimiter` is unspecified or is the empty string (""). In the case where the `delimiter` is unspecified or the empty string, consecutive whitespace characters are regarded as a single separator and leading or trailing whitespace is removed in the output.

        The second output tensor represents the number of substrings generated. `maxsplit` can be used to limit the number of splits performed - after the `maxsplit`th split if the string is not fully split, the trailing suffix of input string after the final split point is also added. For elements where fewer splits are possible than specified in `maxsplit`, it has no effect.

        Args:
            X: (non-differentiable) Tensor of strings to split.

            delimiter: Delimiter to split on. If left unset or set to the empty string
                (""), the input is split on consecutive whitespace.

            maxsplit: Maximum number of splits (from left to right). If left unset (or
                if the number of possible splits are less than maxsplit), it will make
                as many splits as possible. Note that the maximum possible number of
                substrings returned with `maxsplit` specified is `maxsplit+1` since the
                remaining suffix after the `maxsplit`th split is included in the output.
        """

        schema = get_schema("StringSplit", 20, "")
        op = Op(self, "StringSplit", schema)
        return op(*self._prepare_inputs(schema, X), delimiter=delimiter, maxsplit=maxsplit)
