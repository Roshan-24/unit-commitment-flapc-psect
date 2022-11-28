# Team members:
# Vignesh S   - 107119134
# Roshan B    - 107119104
# Prakash V   - 107119136

# Question 2:
# Consider N number of units that must be committed to meet a load demand of a commercial area in a day. 
# Assume you are provided with the load curve of the commercial area, the generation cost characteristics and generation limits of all the generators. 
# Develop a program to prepare the priority list based on FLAPC for committing the units to meet the demand.   

import prettytable

def compute(generator_load_input):
	# These are the input parameters for our algorithm (maximum error, maximum lambda, maximum pdelta, maximum time)

	e_max  =  0.1
	lambda_max  =  1.0
	pdelta_max  =  1.0
	time_max =  24

	# State class to calculate the coherence of states and generators during the load simulation.

	class current_state:
		def __init__(self, p_cost = 0, f_cost = 0, st_previous = None, feasibility = False, available_gens = {}):

			self.st_previous  =  st_previous
			self.feasibililty  =  False
			self.available_gens  =  {}
			self.p_cost  =  p_cost
			self.f_cost  =  f_cost

	# generator_class is used to simulate a single a generator at a time.

	class generator_class:
		def __init__(self, count = 0, pMax = 0, pMin = 0, a = 0, b = 0, c = 0, startingCost = 0, curr_generation = 0):

			self.a  =  a
			self.b  =  b
			self.c  =  c

			self.count  =  count


			self.pMax  =  pMax
			self.pMin  =  pMin
			
			self.current_gen  =  curr_generation
			self.startingCost  =  startingCost
			self.flapc  =  0

		def cost(self, p):
			return self.a + self.b * p + self.c * p * p

	# The economic_load_dispatch function calculates the overall economic load dispatch to minimize the cost of electricity generation without sacrificing quality and reliability.
			
	def economic_load_dispatch(gvn_gens, peak_demand):

		p_total = 0
		totat_c = 0
		_gen  =  gvn_gens
		lambda_current  =  lambda_max 
		pdelta  =  pdelta_max
		err = e_max
		
		while pdelta > err:

			p_total  =  0.0
			totat_c  =  0.0

			for i, generator in enumerate(gvn_gens):
				
				_gen[i].curr_generation  =  (lambda_current-generator.b)/(2*generator.c)
				
				if _gen[i].curr_generation > generator.pMax:
					_gen[i].curr_generation  =  generator.pMax
				
				if _gen[i].curr_generation < generator.pMin:
					_gen[i].curr_generation  =  generator.pMin
				
				p_total  =  _gen[i].curr_generation + p_total
				totat_c  =  totat_c + 1.0 / (2.0 * generator.c)
				
			pdelta  =  peak_demand-p_total
			lambda_current  =  lambda_current + pdelta / totat_c

		_st  =  current_state(p_cost = 0, f_cost = 0, st_previous = None, feasibility = None, available_gens = {})
		_st.load  =  peak_demand

		for i, generator in enumerate(_gen):

			_st.p_cost  =  _st.p_cost+gvn_gens[i].cost(generator.curr_generation)
			_st.available_gens[i]  =  generator.curr_generation

		return _st

	# This line acts as the input of all the 3 generator parameters.

	gens  =  generator_load_input['generators']

	generator_max  =  len(gens)

	generators  =  []

	for i in range(generator_max):

		generators.append(generator_class(
			a  =  gens[i]['a'], 
			b  =  gens[i]['b'], 
			c  =  gens[i]['c'], 
			count  =  gens[i]['count'],
			pMax  =  gens[i]['pMax'],
			pMin  =  gens[i]['pMin'],
			startingCost  =  gens[i]['startingCost']))



	# This line acts as the input of all the loads over 24 hrs period of time.

	load  =  generator_load_input['loads']
	for generator in generators:

		generator.flapc  =  generator.cost(generator.pMax)/generator.pMax

	# Using FLAPC (Full Load Average Production Cost), we sort the generators based on its feasibilty, states and peak load.

	generators.sort(key = lambda x:x.flapc)

	gen_index  =  [el.count for el in generators]


	st_all  =  [[current_state(feasibility = False) for x in range(time_max)] for y in range(generator_max)] 

	s_costs  =  [[0 for x in range(generator_max)] for y in range(generator_max)]

	# Here calculation of p_cost and the generators corresponding power generation at every state takes place. 

	for hour in range(time_max):

		for i, gen in enumerate(generators):

			capacity_maximum  =   sum(x.pMax for x in generators[0:(i+1)])

			if load[hour] <=  capacity_maximum:

				st_all[i][hour]  =  economic_load_dispatch(generators[0:(i+1)], load[hour])
				st_all[i][hour].feasibililty  =  True


	# This loop is used to find the transition cost of the model

	for i in range(generator_max):

		for j in range(generator_max):

			if i >=  j:

				s_costs[i][j]  =  0

			else:

				for k in range(i+1,j):

					s_costs[i][j]  =  s_costs[i][j]+generators[k].startingCost


	# This loop is used to find the F cost of the 1st hour

	for i in range(generator_max):

		st_all[i][0].f_cost  =  st_all[i][0].p_cost

		for k in range(0,i):

			st_all[i][0].f_cost  =  st_all[i][0].f_cost + generators[i].startingCost

	# This loop is used to find the 1st feasible state in the 1st hour and the minimum of all the feasible states

	for hour in range(1,time_max):

		for i in range(generator_max):
			
			
			feasible_gen_first  =  0

			for feasible_gen_first in range(generator_max):
				if st_all[feasible_gen_first][hour-1].feasibililty  ==  True:
					break
			
			minimum_cost  =  st_all[feasible_gen_first][hour-1].f_cost + s_costs[feasible_gen_first][i]
			minimum_count  =  feasible_gen_first

			for next_feasible in range(minimum_count, generator_max):

				if st_all[next_feasible][hour-1].feasibililty and minimum_cost > st_all[next_feasible][hour-1].f_cost+s_costs[next_feasible][i]: 
					minimum_cost  =  st_all[next_feasible][hour-1].f_cost+s_costs[next_feasible][i]
					minimum_count  =  next_feasible

			st_all[i][hour].f_cost  =  st_all[i][hour].p_cost + minimum_cost
			st_all[i][hour].st_previous  =  minimum_count


	# This loop is used to find the 1st feasible state in the 24th hour

	feasible_state  =  0;

	for feasible_state in range(generator_max):

		if st_all[feasible_gen_first][time_max-1].feasibililty  ==  True:
			feasible_state  =  feasible_gen_first

	# This snippet is used to store the final state for 24th hr by finding minimum of all states

	st_fin  =  [current_state() for x in range(time_max)]

	st_fin[time_max-1]  =  st_all[feasible_state][time_max-1];	

	for i in range(feasible_state, generator_max):

		if st_fin[time_max-1].f_cost > st_all[i][time_max-1].f_cost and st_all[i][time_max-1].feasibililty:
				st_fin[time_max-1]  =  st_all[i][time_max-1]

	# State backtracking for all the states for previous hours takes place

	for i in range(time_max-2, -1, -1):

		st_fin[i]  =  st_all[st_fin[i+1].st_previous][i]

	col  =  ['Hour','Load (MW)','P cost','F cost']

	for i in range(0, generator_max):

		col.append("Gen - " + str(gen_index[i]) + " (MW)")

	tab  =  prettytable.PrettyTable(col)

	for i, st in enumerate(st_fin):

		row  =  [i+1, st.load, st.p_cost, st.f_cost]

		for j in range(generator_max):

			if j in st.available_gens:
				row.append(st.available_gens[j])

			else:
				row.append(0) 

		roundvalue  =  3

		x = len(row)

		for i in range(2, x):
			row[i]  =  round(row[i] , roundvalue)
			
		tab.add_row(row)

	return tab.get_string()
	