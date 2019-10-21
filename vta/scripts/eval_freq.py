##############################################################################
#   Copyright 2019 - IBM Research GmbH. All rights reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
##############################################################################

# @file eval_freq.py
# @author Dionysios Diamantopoulos, did@zurich.ibm.com
# @date 18 Oct 2019
# @brief Script for exploration of frequency for VTA

import os
import subprocess
import numpy as np
import os.path
import fileinput
from shutil import copyfile
import pathlib


def check(file_to_search, string_to_find):
    if (not os.path.exists(file_to_search)):
        print("ERROR: file " + file_to_search + " does not exist, skipping...")
        return False
    else:
        with open(file_to_search) as f:
            datafile = f.readlines()
            found = False  # This isn't really necessary
            for line in datafile:
                if string_to_find in line:
                    # found = True # Not necessary
                    return True
            return False  # Because you finished the search without finding

def parse_hls_log(report_file):
    command = "cat " + report_file + "  | grep -A 3 Estimated | tail -n 2 | head -n 1 |  awk '{print $4}' | sed 's/.$//'"
    #print(command)
    estimated = subprocess.getoutput(command)
    command = "cat " + report_file + "  | grep -A 3 Total | head -n 1 | awk '{print $3}' | sed 's/.$//'"
    brams = subprocess.getoutput(command)
    command = "cat " + report_file + "  | grep -A 3 Total | head -n 1 | awk '{print $4}' | sed 's/.$//'"
    dsps = subprocess.getoutput(command)
    command = "cat " + report_file + "  | grep -A 3 Total | head -n 1 | awk '{print $5}' | sed 's/.$//'"
    ffs = subprocess.getoutput(command)
    command = "cat " + report_file + "  | grep -A 3 Total | head -n 1 | awk '{print $6}' | sed 's/.$//'"
    luts = subprocess.getoutput(command)
    return [estimated, brams, dsps, ffs, luts]

def parse_vivado_log(util_file, timing_file):
    # parse Vivado utilization report file
    command = "cat " + util_file + "  | grep  \"Slice LUTs\" |  awk '{print $5}'"
    vluts = subprocess.getoutput(command)
    command = "cat " + util_file + "  | grep  \"Slice LUTs\" |  awk '{print $11}'"
    vlutsp = subprocess.getoutput(command)
    command = "cat " + util_file + "  | grep  \"Slice Registers\" | head -n 1 | awk '{print $5}'"
    vffs = subprocess.getoutput(command)
    command = "cat " + util_file + "  | grep  \"Slice Registers\" | head -n 1 | awk '{print $11}'"
    vffsp = subprocess.getoutput(command)
    command = "cat " + util_file + "  | grep  \"Block RAM Tile\" | head -n 1 | awk '{print $6}'"
    vbrams = subprocess.getoutput(command)
    command = "cat " + util_file + "  | grep  \"Block RAM Tile\" | head -n 1 | awk '{print $12}'"
    vbramsp = subprocess.getoutput(command)
    command = "cat " + util_file + "  | grep  \"DSPs\" | head -n 1 | awk '{print $4}'"
    vdsps = subprocess.getoutput(command)
    command = "cat " + util_file + "  | grep  \"DSPs\" | head -n 1 | awk '{print $10}'"
    vdspsp = subprocess.getoutput(command)

    # parse Vivado timing report file: WNS(ns), TNS(ns), TNS Failing Endpoints, TNS Total Endpoints
    command = "cat " + timing_file + "  | grep -A 2 \"WNS(ns)\" | head -n 3 | tail -n 1 | awk '{print $1}'"
    wns = subprocess.getoutput(command)
    command = "cat " + timing_file + "  | grep -A 2 \"WNS(ns)\" | head -n 3 | tail -n 1 | awk '{print $2}'"
    tns = subprocess.getoutput(command)
    command = "cat " + timing_file + "  | grep -A 2 \"WNS(ns)\" | head -n 3 | tail -n 1 | awk '{print $3}'"
    tns_fail_endpns = subprocess.getoutput(command)
    command = "cat " + timing_file + "  | grep -A 2 \"WNS(ns)\" | head -n 3 | tail -n 1 | awk '{print $4}'"
    tns_tot_endpns = subprocess.getoutput(command)

    return [vbrams, vdsps, vffs, vluts, vbramsp, vdspsp, vffsp, vlutsp, wns, tns, tns_fail_endpns, tns_tot_endpns]


def parse_eval_log(pynq_eval_out):
    command = "cat " + pynq_eval_out + " | grep  \"VTA CONV2D TEST FAILED\" | awk '{print $4}' | sed 's/.$//' | uniq"
    status_eval = subprocess.getoutput(command)
    if status_eval != "FAILED":
        status_eval = "PASSED"
    command = "cat " + pynq_eval_out + " | grep  \"VTA CONV2D TEST\" | head -n 1 | tail -n 1 | awk '{print $8}'"
    conv1_time = subprocess.getoutput(command)
    command = "cat " + pynq_eval_out + " | grep  \"VTA CONV2D TEST\" | head -n 1 | tail -n 1 | awk '{print $10}'"
    conv1_gops = subprocess.getoutput(command)
    command = "cat " + pynq_eval_out + " | grep  \"VTA CONV2D TEST\" | head -n 2 | tail -n 1 | awk '{print $8}'"
    conv2_time = subprocess.getoutput(command)
    command = "cat " + pynq_eval_out + " | grep  \"VTA CONV2D TEST\" | head -n 2 | tail -n 1 | awk '{print $10}'"
    conv2_gops = subprocess.getoutput(command)
    command = "cat " + pynq_eval_out + " | grep  \"VTA CONV2D TEST\" | head -n 3 | tail -n 1 | awk '{print $8}'"
    conv3_time = subprocess.getoutput(command)
    command = "cat " + pynq_eval_out + " | grep  \"VTA CONV2D TEST\" | head -n 3 | tail -n 1 | awk '{print $10}'"
    conv3_gops = subprocess.getoutput(command)
    command = "cat " + pynq_eval_out + " | grep  \"VTA CONV2D TEST\" | head -n 4 | tail -n 1 | awk '{print $8}'"
    conv4_time = subprocess.getoutput(command)
    command = "cat " + pynq_eval_out + " | grep  \"VTA CONV2D TEST\" | head -n 4 | tail -n 1 | awk '{print $10}'"
    conv4_gops = subprocess.getoutput(command)
    command = "cat " + pynq_eval_out + " | grep  \"VTA CONV2D TEST\" | head -n 5 | tail -n 1 | awk '{print $8}'"
    conv5_time = subprocess.getoutput(command)
    command = "cat " + pynq_eval_out + " | grep  \"VTA CONV2D TEST\" | head -n 5 | tail -n 1 | awk '{print $10}'"
    conv5_gops = subprocess.getoutput(command)
    command = "cat " + pynq_eval_out + " | grep  \"VTA CONV2D TEST\" | head -n 6 | tail -n 1 | awk '{print $8}'"
    conv6_time = subprocess.getoutput(command)
    command = "cat " + pynq_eval_out + " | grep  \"VTA CONV2D TEST\" | head -n 6 | tail -n 1 | awk '{print $10}'"
    conv6_gops = subprocess.getoutput(command)
    command = "cat " + pynq_eval_out + " | grep  \"VTA CONV2D TEST\" | head -n 7 | tail -n 1 | awk '{print $8}'"
    conv7_time = subprocess.getoutput(command)
    command = "cat " + pynq_eval_out + " | grep  \"VTA CONV2D TEST\" | head -n 7 | tail -n 1 | awk '{print $10}'"
    conv7_gops = subprocess.getoutput(command)
    command = "cat " + pynq_eval_out + " | grep  \"VTA CONV2D TEST\" | head -n 8 | tail -n 1 | awk '{print $8}'"
    conv8_time = subprocess.getoutput(command)
    command = "cat " + pynq_eval_out + " | grep  \"VTA CONV2D TEST\" | head -n 8 | tail -n 1 | awk '{print $10}'"
    conv8_gops = subprocess.getoutput(command)
    command = "cat " + pynq_eval_out + " | grep  \"VTA CONV2D TEST\" | head -n 9 | tail -n 1 | awk '{print $8}'"
    conv9_time = subprocess.getoutput(command)
    command = "cat " + pynq_eval_out + " | grep  \"VTA CONV2D TEST\" | head -n 9 | tail -n 1 | awk '{print $10}'"
    conv9_gops = subprocess.getoutput(command)
    command = "cat " + pynq_eval_out + " | grep  \"VTA CONV2D TEST\" | head -n 10 | tail -n 1 | awk '{print $8}'"
    conv10_time = subprocess.getoutput(command)
    command = "cat " + pynq_eval_out + " | grep  \"VTA CONV2D TEST\" | head -n 10 | tail -n 1 | awk '{print $10}'"
    conv10_gops = subprocess.getoutput(command)
    return [status_eval, conv1_time, conv2_time, conv3_time, conv4_time, conv5_time, conv6_time, conv7_time, conv8_time, conv9_time, conv10_time, conv1_gops, conv2_gops, conv3_gops, conv4_gops, conv5_gops, conv6_gops, conv7_gops, conv8_gops, conv9_gops, conv10_gops]


LOAD_SESSION = 0
PLOT_ENABLE = 1

savesessionfile = 'globalsave.npy'

if (LOAD_SESSION == 1):
    #dill.load_session(filename)
    [labels, confMat, mat_acc_min, mat_acc_max, [total_bits, frac_bits], mat_brams, mat_dsps, mat_ffs, mat_luts] = np.load(savesessionfile)

else:
    RUN_SYN  = True
    RUN_EVAL = True

    tvm_root = os.environ.get("TVM_HOME")
    vta_config = "pynq_1x16_i8w8a32_15_15_18_17"

    filein = tvm_root + "/vta/python/vta/pkg_config.py"
    fileout = tvm_root + "/vta/python/vta/pkg_config_replaced.py"
    log_file_path = "/tmp/run.log"
    pynq_report_hls_in = tvm_root + "/vta/build/hardware/xilinx/hls/" + vta_config + "/vta_sim/soln/syn/report/vta_csynth.rpt"
    pynq_images_dir = tvm_root + "/vta/Images/"
    pathlib.Path(pynq_images_dir).mkdir(parents=True, exist_ok=True)
    pynq_image_path  = tvm_root + "/vta/build/hardware/xilinx/vivado/" + vta_config + "/export/"
    pynq_report_path = tvm_root + "/vta/build/hardware/xilinx/vivado/" + vta_config + "/vta.runs/impl_1/"

    pathlib.Path(pynq_image_path).mkdir(parents=True, exist_ok=True)
    pynq_image_in = pynq_image_path + "vta.bit"
    pynq_report_timing_in = pynq_report_path + "vta_wrapper_timing_summary_routed.rpt"
    pynq_report_utilization_in = pynq_report_path + "vta_wrapper_utilization_placed.rpt"

    f = open(filein,'r')
    filedata = newdata = f.read()
    f.close()
    logfd = open("./run.log",'w')
    line = "viv_freq\thls_clk\tstatus_syn\test\tbrams\tdsps\tffs\tluts\tvbrams\tvdsps\tvffs\tvluts\twns\ttns\ttns_fail_endpns\ttns_tot_endpns\n"
    logfd.write(line)
    logfd.close()

    VIV_FREQ_list = [100, 142, 167, 200]
    HLS_CLK_list = [1, 2, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 6.6, 6.7, 6.8, 6.9, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 8, 8.5, 9, 9.5, 10]

    sstring_HLSCLK = "self.fpga_per = "
    rstring_HLSCLK = "self.fpga_per = "
    sstring_VIVFREQ = "self.fpga_freq = "
    rstring_VIVFREQ = "self.fpga_freq = "

    for fr in VIV_FREQ_list:
        search_string = sstring_VIVFREQ
        replace_string = rstring_VIVFREQ + str(fr) + " #"
        newdata = newdata.replace(search_string, replace_string)
        for tr in HLS_CLK_list:
            search_string = sstring_HLSCLK
            replace_string = rstring_HLSCLK + str(tr) + " #"
            newdata = newdata.replace(search_string, replace_string)
            infostr = "Injecting " + filein + " with " + replace_string
            f = open(fileout,'w')
            f.write(newdata)
            f.close()
            copyfile(fileout, filein)

            evaluation = vta_config + "_FREQ-" + str(fr) + "_TARGET-" + str(tr)
            pynq_image_out = pynq_images_dir + evaluation + "_vta.bit"
            pynq_report_hls_out = pynq_images_dir + evaluation + "_vta_csynth.rpt"
            pynq_report_timing_out = pynq_images_dir + evaluation + "_vta_wrapper_timing_summary_routed.rpt"
            pynq_report_utilization_out = pynq_images_dir + evaluation + "_vta_wrapper_utilization_placed.rpt"
            pynq_eval_out = pynq_images_dir + evaluation + "_vta_eval.rpt"

            if (RUN_SYN):
                print("INFO: Synthesis of " + evaluation + " with Vivado...")
                if (not os.path.exists(pynq_image_out)):
                    print("WARNING: file " + pynq_image_out + " does not exist. Generating it...")
                    command = "cd " + tvm_root + "/vta/hardware/xilinx && make clean && make cleanall && make ip && time make > " + log_file_path
                    subprocess.getoutput(command)
                    #process = subprocess.Popen(command, stderr=subprocess.STDOUT)
                    #if process.wait() != 0:
                    #    print("Severe Error executing command: " + command + ". Aborting this evaluation...\n")
                    #    continue
                    status_syn = ' OK '
                    copyfile(pynq_image_in, pynq_image_out)
                    copyfile(pynq_report_hls_in, pynq_report_hls_out)
                    copyfile(pynq_report_timing_in, pynq_report_timing_out)
                    copyfile(pynq_report_utilization_in, pynq_report_utilization_out)
                    [estimated, brams, dsps, ffs, luts] = parse_hls_log(pynq_report_hls_in)
                else:
                    print("WARNING: file " + pynq_image_out + " was found already. Skipping generation.")
                    copyfile(pynq_image_out, pynq_image_in) # opposite copy
                    status_syn = 'FOUND';
                    [estimated, brams, dsps, ffs, luts] = parse_hls_log(pynq_report_hls_out)

                [vbrams, vdsps, vffs, vluts, vbramsp, vdspsp, vffsp, vlutsp, \
                wns, tns, tns_fail_endpns, tns_tot_endpns] = \
                parse_vivado_log(pynq_report_utilization_out, pynq_report_timing_out)
            else:
                print("INFO: Skipping synthesis of " + evaluation + " with Vivado\n")
                status_syn = 'SKIP'; estimated='0'; brams='0'; dsps='0'; ffs='0'; \
                luts='0'; vbrams='0'; vdsps='0'; vffs='0'; vluts='0'; \
                vbramsp='0'; vdspsp='0'; vffsp='0'; vlutsp='0'; wns='0'; \
                tns='0'; tns_fail_endpns='0'; tns_tot_endpns='0';


            if (RUN_EVAL):
                print("INFO: Evaluation of " + evaluation + " on PYNQs...")
                if (not os.path.exists(pynq_eval_out)):
                    print("WARNING: file " + pynq_eval_out + " does not exist. Evaluating...")
                    if (not os.path.exists(pynq_image_out)):
                        print("ERROR: file " + pynq_image_out + " does not exist. Cannot evaluate solution.")
                        status_run_eval = 'ERROR'; status_eval = 'UNKNOWN'
                        conv1_time = conv2_time = conv3_time = conv4_time = conv5_time \
                        = conv6_time = conv7_time = conv8_time = conv9_time = \
                        conv10_time = conv1_gops = conv2_gops = conv3_gops = \
                        conv4_gops = conv5_gops = conv6_gops = conv7_gops = \
                        conv8_gops = conv9_gops = conv10_gops = '0';
                    else:
                        # ensure that the right bitstream will be picked
                        copyfile(pynq_image_out, pynq_image_in) # opposite copy
                        command = "python3 " + tvm_root + "/vta/tests/python/integration/test_did_benchmark_topi_conv2d.py > "  + pynq_eval_out
                        subprocess.getoutput(command)
                        subprocess.getoutput("sync")
                        status_run_eval = ' OK '
                        [status_eval, conv1_time, conv2_time, conv3_time, conv4_time, conv5_time, \
                        conv6_time, conv7_time, conv8_time, conv9_time, conv10_time, \
                        conv1_gops, conv2_gops, conv3_gops, conv4_gops, conv5_gops,  \
                        conv6_gops, conv7_gops, conv8_gops, conv9_gops, conv10_gops] \
                        = parse_eval_log(pynq_eval_out)
                else:
                    print("WARNING: file " + pynq_eval_out + " was found already. Skipping evaluation.")
                    status_run_eval = 'FOUND';
                    [status_eval, conv1_time, conv2_time, conv3_time, conv4_time, conv5_time, \
                    conv6_time, conv7_time, conv8_time, conv9_time, conv10_time, \
                    conv1_gops, conv2_gops, conv3_gops, conv4_gops, conv5_gops,  \
                    conv6_gops, conv7_gops, conv8_gops, conv9_gops, conv10_gops] \
                    = parse_eval_log(pynq_eval_out)
            else:
                print("INFO: Skipping evaluation " + evaluation + " on PYNQs\n")
                status_run_eval = 'SKIP'; status_eval = 'SKIP';
                conv1_time = conv2_time = conv3_time = conv4_time = conv5_time \
                = conv6_time = conv7_time = conv8_time = conv9_time = \
                conv10_time = conv1_gops = conv2_gops = conv3_gops = \
                conv4_gops = conv5_gops = conv6_gops = conv7_gops = \
                conv8_gops = conv9_gops = conv10_gops = '0';

            line = line + str(fr) + "\t" + str(tr) + "\t" + status_syn + "\t" + estimated + "\t" +  \
            brams + "\t" + dsps + "\t" + ffs + "\t" + luts + "\t" +  vbrams + \
            "\t" + vdsps + "\t" + vffs + "\t" + vluts + "\t" + wns + "\t" + \
            tns + "\t" + tns_fail_endpns + "\t" + tns_tot_endpns + "\t" + \
            status_run_eval + "\t" + status_eval + "\t" + \
            conv1_time + "\t" + conv2_time + "\t" + conv3_time + "\t" + conv4_time + "\t" + conv5_time + "\t" + \
            conv6_time + "\t" + conv7_time + "\t" + conv8_time + "\t" + conv9_time + "\t" + conv10_time + "\t" + \
            conv1_gops + "\t" + conv2_gops + "\t" + conv3_gops + "\t" + conv4_gops + "\t" + conv5_gops + "\t" +  \
            conv6_gops + "\t" + conv7_gops + "\t" + conv8_gops + "\t" + conv9_gops + "\t" + conv10_gops + "\n"
            logfd = open("./run.log",'w')
            logfd.write(line)
            logfd.close()

    #restore config
    f = open(filein,'w')
    f.write(filedata)
    f.close()
