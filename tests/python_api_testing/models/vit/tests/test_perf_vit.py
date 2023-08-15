from pathlib import Path
import sys

f = f"{Path(__file__).parent}"
sys.path.append(f"{f}")
sys.path.append(f"{f}/..")
sys.path.append(f"{f}/../..")
sys.path.append(f"{f}/../../..")
sys.path.append(f"{f}/../../../..")

from transformers import AutoImageProcessor, ViTForImageClassification
import torch
from loguru import logger
import pytest

import tt_lib
from models.utility_functions import torch_to_tt_tensor_rm, tt_to_torch_tensor
from tests.python_api_testing.models.utility_functions_new import Profiler
from models.utility_functions import disable_persistent_kernel_cache, enable_persistent_kernel_cache
from tests.python_api_testing.models.utility_functions_new import prep_report
from models.vit.tt.modeling_vit import vit_for_image_classification

BATCH_SIZE = 1


def run_perf_vit(expected_inference_time, expected_compile_time, hf_cat_image_sample_input):
    profiler = Profiler()
    disable_persistent_kernel_cache()
    first_key = "first_iter"
    second_key = "second_iter"
    cpu_key = "ref_key"

    image = hf_cat_image_sample_input

    # Initialize the device
    device = tt_lib.device.CreateDevice(tt_lib.device.Arch.GRAYSKULL, 0)
    tt_lib.device.InitializeDevice(device)
    tt_lib.device.SetDefaultDevice(device)


    image_processor = AutoImageProcessor.from_pretrained("google/vit-base-patch16-224")
    HF_model = ViTForImageClassification.from_pretrained(
        "google/vit-base-patch16-224"
    )  # loaded for the labels
    inputs = image_processor(image, return_tensors="pt")

    tt_inputs = torch_to_tt_tensor_rm(
        inputs["pixel_values"], device, put_on_device=False
    )

    tt_inputs = tt_inputs.to(device, tt_lib.tensor.MemoryConfig(True, tt_lib.tensor.BufferType.L1))
    tt_model = vit_for_image_classification(device)

    with torch.no_grad():
        profiler.start(cpu_key)
        logits = HF_model(**inputs).logits
        tt_lib.device.Synchronize()
        profiler.end(cpu_key)

        profiler.start(first_key)
        tt_output = tt_model(tt_inputs)[0]
        profiler.end(first_key)

        enable_persistent_kernel_cache()

        profiler.start(second_key)
        tt_output = tt_model(tt_inputs)[0]
        tt_lib.device.Synchronize()
        profiler.end(second_key)

    first_iter_time = profiler.get(first_key)
    second_iter_time = profiler.get(second_key)
    cpu_time = profiler.get(cpu_key)
    tt_lib.device.CloseDevice(device)

    prep_report(
        model_name="vit",
        batch_size=BATCH_SIZE,
        inference_and_compile_time=first_iter_time,
        inference_time=second_iter_time,
        expected_compile_time=expected_compile_time,
        expected_inference_time=expected_inference_time,
        comments="base-patch16",
        inference_time_cpu=cpu_time
    )

    compile_time = first_iter_time - second_iter_time
    logger.info(f"vit inference time: {second_iter_time}")
    logger.info(f"vit compile time: {compile_time}")
    assert second_iter_time < expected_inference_time, "vit is too slow"
    assert compile_time < expected_compile_time, "vit compile time is too slow"


@pytest.mark.models_performance_bare_metal
@pytest.mark.parametrize(
    "expected_inference_time, expected_compile_time",
    (
        (2.15,
        13,
        ),
    ),
)
def test_perf_bare_metal(use_program_cache, expected_inference_time, expected_compile_time, hf_cat_image_sample_input):
    run_perf_vit(expected_inference_time, expected_compile_time, hf_cat_image_sample_input)


@pytest.mark.models_performance_virtual_machine
@pytest.mark.parametrize(
    "expected_inference_time, expected_compile_time",
    (
        (2.7,
        17.5,
        ),
    ),
)
def test_perf_virtual_machine(use_program_cache, expected_inference_time, expected_compile_time, hf_cat_image_sample_input):
    run_perf_vit(expected_inference_time, expected_compile_time, hf_cat_image_sample_input)
