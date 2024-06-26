# WorkflowNo_1712
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1712
doc: A workflow including the tool(s) OpenChrom, PECAN (PEptide-Centric Analysis), Mascot Server, msaccess, esimsa2D.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3162" # MAGE-TAB
  input_2:
    type: File
    format: "http://edamontology.org/format_3016" # VCF
  input_3:
    type: File
    format: "http://edamontology.org/format_3244" # mzML
steps:
  OpenChrom_01:
    run: add-path-to-the-implementation/OpenChrom.cwl 
    in:
      OpenChrom_in_1: input_3
    out: [OpenChrom_out_1, OpenChrom_out_2]
  PECAN (PEptide-Centric Analysis)_02:
    run: add-path-to-the-implementation/PECAN (PEptide-Centric Analysis).cwl 
    in:
      PECAN (PEptide-Centric Analysis)_in_1: input_3
      PECAN (PEptide-Centric Analysis)_in_2: input_1
    out: [PECAN (PEptide-Centric Analysis)_out_1, PECAN (PEptide-Centric Analysis)_out_2]
  Mascot Server_03:
    run: add-path-to-the-implementation/Mascot Server.cwl 
    in:
      Mascot Server_in_1: OpenChrom_01/OpenChrom_out_1
      Mascot Server_in_2: PECAN (PEptide-Centric Analysis)_02/PECAN (PEptide-Centric Analysis)_out_2
    out: [Mascot Server_out_1]
  msaccess_04:
    run: add-path-to-the-implementation/msaccess.cwl 
    in:
      msaccess_in_1: input_3
      msaccess_in_2: Mascot Server_03/Mascot Server_out_1
    out: [msaccess_out_1, msaccess_out_2, msaccess_out_3]
  esimsa2D_05:
    run: add-path-to-the-implementation/esimsa2D.cwl 
    in:
      esimsa2D_in_1: input_2
      esimsa2D_in_2: OpenChrom_01/OpenChrom_out_1
      esimsa2D_in_3: msaccess_04/msaccess_out_1
    out: [esimsa2D_out_1, esimsa2D_out_2, esimsa2D_out_3]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3242" # PSI MI TAB (MITAB)
    outputSource: esimsa2D_05/esimsa2D_out_1
