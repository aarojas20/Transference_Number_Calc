# Transference-Number-Determination
Read data from chronoamperometry and electrochemical impedance spectroscopy testing to calculate a cation transport number.  
The normalized chronoamperometry data is graphed, the EIS data is graphed, and the resulting transference number is graphed.

The goal is to calculate the transference number (t+) as a function of time and display the results as graphs.
Read all of the .lst files and compile the resistance values from each into a pd.DataFrame, this is fed to the t+ calculation
Analyze two experiments from one .txt file:  Negative deltaV and positive deltaV of potential applied to a cell
For each experiment:  identify the initial identify each of the twelve 1-hr current profiles (loops) from the deltaV biases
                                        at the end of each 1-hr current prof., find the last value of current, feed it to the t+ calculation
Graph the transference number as a function of time with the normalized current as a function of time
Graph the EIS data and the fits
Graph the resistance values as a function of experiment number (loop #)
Save the t+ values to a .csv file and to a table as .png
