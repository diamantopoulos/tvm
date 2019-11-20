conf=pynq_1x16_i8w16a32_15_15_18_17
grep set_directive_loop_tripcount /home/did/tvm_did/vta/build/hardware/xilinx/hls/${conf}/vta_sim/soln/csim/report/vta_csim.log | cut -d' ' -f3,4,5,6,7,8 | sort -k 6 | uniq >> ${TVM_HOME}/vta/build/hardware/xilinx/hls/${conf}/vta_sim/soln/directives.tcl
echo "Appended to ${TVM_HOME}/vta/build/hardware/xilinx/hls/${conf}/vta_sim/soln/directives.tcl"
