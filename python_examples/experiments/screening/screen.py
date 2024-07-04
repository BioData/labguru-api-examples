import pdb
import os
import base as lg

lg.BASE_URL = "http://localhost:3000/api/v1"
lg.TOKEN = lg.login(os.environ.get("LGEMAIL"), os.environ.get("LGPASSWORD"))
# EXAMPLE ONLY - DATA is not real and has no impact
# This experiment is going to test the impact of 10 differnt sugers on cell growth
# We are going to grow cells in 10, 384 well plates
# Each plate will have 1 type of compound (complex suger)
# With differnt conenteration and controls
# Each plate / well will be images 2 times (after 6 hours and after 20 hours)

#0. set up a project
project_id    = lg.add_project("Impact of Sugar concentration on Cell Growth")['id']
folder_id     = lg.add_folder(project_id,"Master Plate Design")['id']
experiment_id = lg.add_experiment(project_id,folder_id,"Master Plate")['id']
section_id    = lg.add_section(experiment_id,"Master Plate")['id']

#register 10 differnt compounds via SDF import
sugars          = lg.register("Chemistry::Compound","data/sugars.sdf")

#add the cell lines needs for this experiment
cell_ids         = lg.register("Biocollection::CellLine", "data/cell_line.xlsx")

#1. add an empty plate
plate_id      = lg.add_empty_plate(experiment_id,section_id,24,16,"Master Plate")['id']

#2. add cells to a sample element
sample_element = lg.add_sample_element(section_id,cell_ids,"Biocollection::CellLine")

#3. add cells to this plate
plate_json    = lg.add_layer_data_to_plate(plate_id,'data/plate_default_cells.csv')

# #4. add meta data layer to the plate - declare controls and borders ;
plate_json    = lg.add_layer_data_to_plate(plate_id,'data/plate_default_meta.csv')
plate_json    = lg.add_layer_data_to_plate(plate_id,'data/plate_clear_wells.csv')

#
#5. utility - get plate json from xlsx
# filename     = "data/screen.xlsx"
# xlsx_file    = lg.download_plate_xlsx(plate_id, filename)
# plate_data   = lg.convert_plate_xls_to_json(filename,section_id)
# #
# # #6. create another empty plate and populate it with plate data
# plate_json    = lg.add_empty_plate(experiment_id,section_id,24,16,"Base Replica Plate")
# new_plate_id  = plate_json["id"]
# plate_json["data"] = plate_data
# plate_data    = lg.update_plate(new_plate_id,plate_json)
# #
# # #7. Replicate Base plates
# names         = ["Replica A", "Replica B"]
# replicates    = lg.clone_plate(plate_id,names)
# #
# # #8. Createa a filter to display only plates related to this experiment
# # #search = add_search()
# # #9. Add this filter to the experiment page
# #
# # #10. Per plate attach an image
# #
# # #11. Per image - run an image analysis workflow
# #
# # #12. Add data per well
# #
# # #13. Add plate datasets
