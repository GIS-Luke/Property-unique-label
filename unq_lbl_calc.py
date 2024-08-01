'''
To make labelling more legible at 1:2000 and 1:1000 zoom scales.
Only label 1 property where the VIEW_PFI is repeated except if
it is a multi assessment and 'NUM_ADDRESS = HOU_NUM_1_2_CONCAT'
'''
try:
    import sys
    # make sure this path is correct and it contains
    # sendErrorEmail.py script
    scriptdir = f'D:\ArcGISCatalog\PYs\email_errors'
    sys.path.insert(0, scriptdir) 
    from sendErrorEmail import sendEmail
    import arcpy as ap
    from os.path import join
    sde = (r'\\cappgis10\d$\ArcGISCatalog\SDEConnections'
           r'\cdbpsql20GIS_DEVgisdba.sde')
    in_mem = 'in_memory'
    prop = 'PROPERTY'
    prop_lbl = 'PROPERTY_UNQ_LBL'
    add = 'ADDRESS'
    sde_prop = join(sde, prop)
    prop_vw = 'prop_view'
    sde_add = join(sde, add)
    tmp_prop_lbl = join(in_mem, prop_lbl)
    sde_prop_lbl = join(sde, prop_lbl)
    # Exclude the rows without a propnum so we don't get first returns
    # without an address.
    # We'll work on non multi assessments first
    sql_approved = "PROPNUM_INT <> -1 And STATUS LIKE 'A'"
    ap.MakeTableView_management(sde_prop, prop_vw, sql_approved)
    # First PROPERTY_PFI with a PROPNUM for a VIEW_PFI
    # This is my best bet for labelling
    ap.Statistics_analysis(prop_vw, tmp_prop_lbl, "PFI FIRST", "VIEW_PFI")
    ap.TruncateTable_management(sde_prop_lbl)
    ap.Append_management(tmp_prop_lbl, sde_prop_lbl, 'NO_TEST')
    # Block to allow a proposed label to appear in addition
    # to an approved property label. Similar to the above
    # block except it deletes to allow for new creation
    # it also doesn't truncate the table since the necessary
    # truncate has occurred earlier.
    ap.Delete_management(prop_vw)
    sql_proposed = "PROPNUM_INT <> -1 And STATUS LIKE 'P'"
    ap.MakeTableView_management(sde_prop, prop_vw, sql_proposed)
    ap.Delete_management(tmp_prop_lbl)
    ap.Statistics_analysis(prop_vw, tmp_prop_lbl, "PFI FIRST", "VIEW_PFI")
    ap.Append_management(tmp_prop_lbl, sde_prop_lbl, 'NO_TEST')
    # end of the proposed label block
    tb_vw = 'table_view'
    ap.MakeTableView_management(sde_add, tb_vw)
    ap.AddJoin_management(tb_vw, 'PROPERTY_PFI', sde_prop_lbl,
                          'FIRST_PFI', 'KEEP_COMMON')
    # The KEEP_COMMON param means everything after the join is
    # what we want to label, hence 'Y'
    ap.CalculateField_management(tb_vw, 'UNQ_LBL', "'Y'", 'PYTHON')
    ap.RemoveJoin_management(tb_vw)
    ap.Delete_management(tb_vw)
    # Multi assessments often share a view_pfi however have
    # different num_address(40%ish). In the below block we making sure they
    # get labelled if they are not sub addresses
    multi_prop_sql = "PROPNUM_INT <> -1 And MULTI_ASSESSMENT LIKE 'Y'"
    multi_vw = 'multi_vw'
    ap.MakeTableView_management(sde_prop, multi_vw, multi_prop_sql)
    address_sql = 'NUM_ADDRESS = HOU_NUM_1_2_CONCAT'
    add_vw = 'address_vw'
    ap.MakeTableView_management(sde_add, add_vw, address_sql)
    ap.AddJoin_management(add_vw, 'PROPERTY_PFI', multi_vw, 'PFI')
    ap.CalculateField_management(add_vw, 'UNQ_LBL', "'Y'", 'PYTHON')
    ap.RemoveJoin_management(add_vw)
    ap.Delete_management(add_vw)
    ap.Delete_management(multi_vw)
    # I don't like leaving nulls and it feels more consistent
    # to mark the remaining records as 'N'
    is_null = "UNQ_LBL IS NULL"
    ap.MakeTableView_management(sde_add, tb_vw, is_null)
    ap.CalculateField_management(tb_vw, 'UNQ_LBL', "'N'", 'PYTHON')
    ap.Delete_management(tb_vw)
except Exception as error:
    scriptName = os.path.basename(__file__)
    sendEmail(scriptName, error)
