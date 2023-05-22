#pragma once

#include <cstdint>
#include "ckernel_structs.h"
#include "hostdevcommon/common_runtime_address_map.h"

extern uint32_t cfg_state_id;
extern uint32_t unp_cfg_context;
extern uint32_t gl_alu_format_spec_reg;

extern volatile uint32_t l1_buffer[16];

//extern const int32_t unpack_src_format[24];
//extern const int32_t unpack_dst_format[24];
//extern const int32_t pack_src_format[16];
//extern const int32_t pack_dst_format[16];

extern uint32_t pack_sync_tile_dst_ptr;
extern uint32_t math_sync_tile_dst_index;

extern CBReadInterface cb_read_interface[NUM_CIRCULAR_BUFFERS];
extern CBWriteInterface cb_write_interface[NUM_CIRCULAR_BUFFERS];

extern uint32_t __local_mem_rodata_start_addr[];
extern uint32_t __local_mem_rodata_end_addr[];
extern uint32_t __ldm_data_start[];
extern uint32_t __ldm_data_end[];
extern uint32_t __firmware_start[];
