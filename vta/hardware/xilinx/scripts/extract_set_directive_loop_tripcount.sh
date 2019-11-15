grep set_directive_loop_tripcount /home/did/tvm_did/vta/build/hardware/xilinx/hls/pynq_1x16_i8w8a32_15_15_18_17/vta_sim/soln/csim/report/vta_csim.log | cut -d' ' -f3,4,5,6,7,8 | sort -k 6 | uniq
