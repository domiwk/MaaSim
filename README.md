The differents folders contain :

	Data Generation : - the file "gisviz.py" is the file that computes the indicators (takes long time to run) 
			  - the file "prepareData" computes one time processes that have to be done before computing the indicators(might take long time to run)
			  - shapefiles needed for the computations



	Feature Selection : -An R markdown "Finge" for the process of feature engineering
			    -A python file "regression" with the model for the Random forest and the other compared algorithms 
			    -Csv files resulting from feature engineering and from the indicators


	OPtimization algorithms: - One file "gas.py" with the problem implementation and experiments for the genetic algorithms(Platypus needed)
				 - CSv file with indicators for Maastricht and the Random forest model used for evaluating individuals


	Simulation : - "gui.py" is the main file with the logic of the interface (Kivy needed)
		     - "test.kv" is the corresponding Kivy file with the structure 
		     - the file "ga.py" is the file containing the genetic algorithm chosen for the simulation
		     - the folder "icons" contains png files of icons for the interface and "song" the background music
		     - the csv "weights" is a file containing weights for indicator for computing the value of groupings
		     - "MassrawcleanNAMES" contains indicators values for the municipality of Maastricht
