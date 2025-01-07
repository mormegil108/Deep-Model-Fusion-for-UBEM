# -*- coding: utf-8 -*-

import rhinoscriptsyntax as rs
import os
import time

# Specify the directory containing the scenario templates
template_directory = r""

# Specify the directory to save UMI bundle files for different cycles
cycle_directories = {
    "C1": r"",
}

# Specify the number of simulations and other parameters
num_simulations = 196
check_limit = 10
max_simulation_time = 500

for cycle, umi_bundle_directory in cycle_directories.items():
    error_list = list()
    
    for i in range(1, num_simulations+1):
        # Construct the path to the template for this scenario
        template_filename = 'S{}.json'.format(i)
        template_path = os.path.join(template_directory, template_filename)

        # Import the scenario template
        import_command = '-UmiImportTemplateLibrary "{}"'.format(template_path)
        rs.Command(import_command)

        # Clear the command history
        rs.ClearCommandHistory()

        # Select all buildings and run energy simulation
        rs.Command("UmiSelectAllBuildings")
        rs.Command("UmiSimulateEnergy")
        start_time = time.time()

        while True:
            # Check for the completion message in the Rhino command history
            completion_message = "UMI energy simulation complete."
            history = rs.CommandHistory()

            if completion_message in history:
                break

            # Check if the simulation exceeds the maximum allowed time
            if time.time() - start_time >= max_simulation_time:
                print("Simulation {} took longer than expected in Cycle-{}.".format(i, cycle))
                error_list.append(i)
                rs.Command("UmiCancelEnergySimulation")
                break

            # Wait for the next check
            rs.Sleep(check_limit)

        # Specify the directory to save the UMI bundle
        bundle_filename = "S{}.umi".format(i)
        bundle_path = os.path.join(umi_bundle_directory, bundle_filename)
        save_command = '-UmiBundleSaveAs "{}"'.format(bundle_path)
        rs.Command(save_command)
        saving_message = "UMI bundle exported to {}".format(bundle_path)

        if saving_message not in rs.CommandHistory():
            # Try saving the UMI file once more
            rs.Command(save_command)
            if saving_message not in rs.CommandHistory():
                print("PROBLEM: In Cycle-{}, UMI bundle {} not saved.".format(cycle, bundle_filename))
                error_list.append(i)
    
    # Re-run the energy simulation for the missing scenarios
    missing_list = list()

    for missing in error_list:
        # Construct the path to the template for this scenario
        template_filename = 'S{}.json'.format(missing)
        template_path = os.path.join(template_directory, template_filename)

        # Import the scenario template
        import_command = '-UmiImportTemplateLibrary "{}"'.format(template_path)
        rs.Command(import_command)

        # Clear the command history
        rs.ClearCommandHistory()

        # Select objects by name
        selected_objects = []

        for building_name in selected_buildings:
            objects = rs.ObjectsByName(building_name)
            if objects:
                selected_objects.extend(objects)
        
        # Select all found objects
        if selected_objects:
            rs.UnselectAllObjects()
            rs.SelectObjects(selected_objects)
            #print("{} objects found and selected for simulation {}.".format(len(selected_objects), i))
        else:
            print("No objects found with the specified names for simulation {}. Skipping to the next iteration.".format(i))
            error_list.append(i)
            continue

        # Run energy simulation
        rs.Command("UmiSimulateEnergy")
        start_time = time.time()

        while True:
            # Check for the completion message in the Rhino command history
            completion_message = "UMI energy simulation complete."
            history = rs.CommandHistory()

            if completion_message in history:
                break

            # Check if the simulation exceeds the maximum allowed time
            if time.time() - start_time >= max_simulation_time:
                print("Simulation {} took longer than expected in Cycle-{}.".format(missing, cycle))
                missing_list.append(missing)
                rs.Command("UmiCancelEnergySimulation")
                break

            # Wait for the next check
            rs.Sleep(check_limit)

        # Specify the directory to save the UMI bundle
        bundle_filename = "S{}.umi".format(missing)
        bundle_path = os.path.join(umi_bundle_directory, bundle_filename)
        save_command = '-UmiBundleSaveAs "{}"'.format(bundle_path)
        rs.Command(save_command)
        saving_message = "UMI bundle exported to {}".format(bundle_path)

        if saving_message not in rs.CommandHistory():
            # Try saving the UMI file once more
            rs.Command(save_command)
            if saving_message not in rs.CommandHistory():
                print("PROBLEM: In Cycle-{}, UMI bundle {} not saved.".format(cycle, bundle_filename))
                missing_list.append(missing)

    # Print missing scenarios after double-check
    print("After double-check for Cycle-{} >> Missing Scenarios: {}".format(cycle, missing_list))