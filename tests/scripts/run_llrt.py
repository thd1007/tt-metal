import argparse
import time
import random
from itertools import chain
from functools import partial

from tests.scripts.common import run_single_test, run_process_and_get_result, report_tests, TestEntry, error_out_if_test_report_has_failures, TestSuiteType
from tests.scripts.cmdline_args import get_cmdline_args, get_llrt_arguments_from_cmdline_args


SILICON_DRIVER_TEST_ENTRIES = (
    TestEntry("llrt/tests/test_silicon_driver", "test_silicon_driver"),
    TestEntry("llrt/tests/test_silicon_driver_dram_sweep", "test_silicon_driver_dram_sweep"),
    TestEntry("llrt/tests/test_silicon_driver_l1_sweep", "test_silicon_driver_l1_sweep"),
)

LLRT_TEST_ENTRIES = (
    TestEntry("llrt/tests/test_run_risc_read_speed", "test_run_risc_read_speed"),
    TestEntry("llrt/tests/test_run_risc_write_speed", "test_run_risc_write_speed"),
    TestEntry("llrt/tests/test_run_eltwise_sync", "test_run_eltwise_sync"),
    TestEntry("llrt/tests/test_run_sync", "test_run_sync"),
    TestEntry("llrt/tests/test_run_sync_db", "test_run_sync_db"),
     # TestEntry("llrt/tests/test_run_risc_rw_speed_banked_dram", "test_run_risc_rw_speed_banked_dram"),  # hangs on tttest, must solve
    TestEntry("llrt/tests/test_run_dataflow_cb_test", "test_run_dataflow_cb_test"),

    TestEntry("llrt/tests/test_run_test_debug_print", "test_run_test_debug_print"),
    TestEntry("llrt/tests/test_run_datacopy_switched_riscs", "test_run_datacopy_switched_riscs"),
    TestEntry("llrt/tests/test_dispatch_v1", "test_dispatch_v1"),
)


def run_single_llrt_test(test_entry, timeout):
    run_test = partial(run_single_test, "llrt", timeout=timeout)

    print(f"\n\n=============== RUNNING LLRT TEST - {test_entry}")

    return run_test(test_entry)


def run_llrt_tests(llrt_test_entries, timeout):
    make_test_status_entry = lambda test_entry_: (test_entry_, run_single_llrt_test(test_entry_, timeout))

    seed = time.time()

    random.seed(seed)
    random.shuffle(llrt_test_entries)
    print(f"SHUFFLED LLRT TESTS - Using order generated by seed {seed}")

    test_and_status_entries = map(make_test_status_entry, llrt_test_entries)

    return dict(test_and_status_entries)


def get_llrt_test_entries(skip_driver_tests):
    return list(
        chain.from_iterable([LLRT_TEST_ENTRIES, tuple() if skip_driver_tests else SILICON_DRIVER_TEST_ENTRIES])
    )


if __name__ == "__main__":
    cmdline_args = get_cmdline_args(TestSuiteType.LLRT)

    timeout, skip_driver_tests, = get_llrt_arguments_from_cmdline_args(cmdline_args)

    llrt_test_entries = get_llrt_test_entries(skip_driver_tests=skip_driver_tests)

    test_report = run_llrt_tests(llrt_test_entries, timeout)

    report_tests(test_report)

    error_out_if_test_report_has_failures(test_report)
