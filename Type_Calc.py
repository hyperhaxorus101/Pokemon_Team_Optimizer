import json
import os
import operator as op

def deleteXNumOfElement(element, num, list):
	'''
	Purpose: To delete an element from a list X number of times.

	element: The element to delete.

	num: The number of times to delete them element.

	list: The list to remove elements from.

	Returns: The modified list.
	'''

	i = 0
	newList = list.copy()
	if num != 0:
		for j in range(len(list)):
			if list[j] == element:
				del newList[j-i]
				i += 1
			if i>=num:
				break

	return newList

def getTypeCombos():
	'''
	Purpose: To get every possible type combination.

	Returns: A list of lists for every possible type combination.
	'''
	file = open(f'Scripts{os.path.sep}types.json', 'r')
	types = json.load(file)

	types = list(types.keys())

	typeCombos = []

	for type in types:
		currentCombo = []
		currentCombo.append(type)
		for otherType in types:
			currentInnerCombo = currentCombo.copy()
			currentInnerCombo.append(otherType)
			if sorted(currentInnerCombo) not in typeCombos:
				typeCombos.append(sorted(currentInnerCombo))
		
	return sorted(typeCombos)

def createMember(type1, type2 = None):
	'''
	Purpose: To create a member object.

	type1: First type of the member.

	type2: The second type of the member.

	Returns: The Member.
	'''

	file = open(f'Scripts{os.path.sep}types.json', 'r')
	types = json.load(file)

	if type2 == None:
		type2 = type1

	
	member = {}
	member['Types'] = [type1, type2]
	member['Weaknesses'], member['Resistances'], member['Immunities'] = get_member_defensive_properties(type1, type2)
	member['Effective'] = [*set(types[type1]['Effective'] + types[type2]['Effective'])]

	return member

def get_member_defensive_properties(type1, type2=None):
	'''
	Purpose: To identify defensive type combination properties of user entered type combos.

	type1: The first type entered.

	type2: The second type entered. Defaults to none.

	Returns: Three lists for weaknesses, resistances, and immunities, all sorted by alphabetical order.
	'''

	file = open(f'Scripts{os.path.sep}types.json', 'r')
	types = json.load(file)

	allWeaknesses = []
	allResistances = []
	allImmunities = []

	weaknesses = types[type1]['Weaknesses']
	resistances = types[type1]['Resistances']
	immunities = types[type1]['Immunities']

	if type2 != None and type2 != type1:

		weaknesses += types[type2]['Weaknesses']
		resistances += types[type2]['Resistances']
		immunities += types[type2]['Immunities']
	
		weaknesses = [*set(weaknesses)]
		resistances = [*set(resistances)]
		immunities = [*set(immunities)]
	
		for weakness in weaknesses:
			if weakness not in resistances and weakness not in immunities:
				allWeaknesses.append(weakness)
		
		for resistance in resistances:
			if resistance not in weaknesses and resistance not in immunities:
				allResistances.append(resistance)

	else:
		allWeaknesses = weaknesses
		allResistances = resistances

	allImmunities = immunities

	return sorted(allWeaknesses), sorted(allResistances), sorted(allImmunities)

def get_team_defensive_properties(members):
	'''
	Purpose: To identify defensive type combination properties of user entered teams.

	members: A dictionary containing dictionaries corresponding to team members and their type interactions.

	Returns: Three lists for weaknesses, resistances, and immunities, all sorted by alphabetical order.
	'''

	weaknesses = []
	resistances = []
	immunities = []

	for member in members:
		weaknesses += members[member]['Weaknesses']
		resistances += members[member]['Resistances']
		immunities += members[member]['Immunities']
	
	uniqueWeaknesses = [*set(weaknesses)]

	for weakness in uniqueWeaknesses:
		if weakness in resistances and weakness not in immunities:
			weaknessesCount = op.countOf(weaknesses, weakness)
			resistancesCount = op.countOf(resistances, weakness)
			if weaknessesCount == resistancesCount:
				weaknesses = list(filter((weakness).__ne__, weaknesses))
				resistances = list(filter((weakness).__ne__, resistances))
			elif weaknessesCount > resistancesCount:
				resistances = list(filter((weakness).__ne__, resistances))
				weaknesses = deleteXNumOfElement(weakness, resistancesCount, weaknesses)
			elif weaknessesCount < resistancesCount:
				weaknesses = list(filter((weakness).__ne__, weaknesses))
				resistances = deleteXNumOfElement(weakness, weaknessesCount, resistances)

		elif weakness in immunities and weakness not in resistances:
			weaknessesCount = op.countOf(weaknesses, weakness)
			immunitiesCount = op.countOf(immunities, weakness)
			if weaknessesCount == immunitiesCount:
				weaknesses = list(filter((weakness).__ne__, weaknesses))
				immunities = list(filter((weakness).__ne__, immunities))	
			elif weaknessesCount > immunitiesCount:
				immunities = list(filter((weakness).__ne__, immunities))	
				weaknesses = deleteXNumOfElement(weakness, immunitiesCount, weaknesses)
			elif weaknessesCount < immunitiesCount:
				weaknesses = list(filter((weakness).__ne__, weaknesses))
				immunities = deleteXNumOfElement(weakness, weaknessesCount, immunities)

		elif weakness in immunities and weakness in resistances:
			weaknessesCount = op.countOf(weaknesses, weakness)
			resistancesCount = op.countOf(resistances, weakness)
			immunitiesCount = op.countOf(immunities, weakness)

			if weaknessesCount == (immunitiesCount + resistancesCount):
				weaknesses = list(filter((weakness).__ne__, weaknesses))
				resistances = list(filter((weakness).__ne__, resistances))
				immunities = list(filter((weakness).__ne__, immunities))	

			elif weaknessesCount > (immunitiesCount + resistancesCount):
				resistances = list(filter((weakness).__ne__, resistances))
				immunities = list(filter((weakness).__ne__, immunities))										
				weaknesses = deleteXNumOfElement(weakness, (weaknessesCount + immunitiesCount), weaknesses)
			
			elif weaknessesCount < (immunitiesCount + resistancesCount) and (weaknessesCount>=resistancesCount):
				resistances = list(filter((weakness).__ne__, resistances))
				weaknesses = list(filter((weakness).__ne__, weaknesses))
				immunities = deleteXNumOfElement(weakness, (weaknessesCount-resistancesCount), immunities)
			
			elif weaknessesCount < (immunitiesCount + resistancesCount) and (weaknessesCount<resistancesCount):
				weaknesses = list(filter((weakness).__ne__, weaknesses))
				resistances = deleteXNumOfElement(weakness, (weaknessesCount), resistances)

	return sorted(weaknesses), sorted(resistances), sorted(immunities)

def get_team_offensive_properties(members):

	totalEffectiveness = []

	for member in members:
		totalEffectiveness += members[member]['Effective']

	return [*set(totalEffectiveness)]

def get_final_member_by_STAB_coverage(members):
	
	bestNewCombos = []
	currentEffectiveness = get_team_offensive_properties(members)
	numSTAB = len(currentEffectiveness)

	newMembers = members.copy()

	types = getTypeCombos()

	for type in types:
		type1, type2 = type
		newMember = createMember(type1, type2)

		effectiveness = newMember['Effective']

		tempEffectiveness = [*set(currentEffectiveness + effectiveness)]
		if len(tempEffectiveness) == numSTAB:
			bestNewCombos.append([type1, type2])
		if len(tempEffectiveness) > numSTAB:
			numSTAB = len(tempEffectiveness)
			bestNewCombos = [[type1, type2]]

	return bestNewCombos

def get_final_member_by_least_weaknesses(members, rerun=None):
	'''
	Purpose: To identify optimal type combinations for a last member based on current resistances and immunities.

	members: A dictionary corresponding to current members.

	rerun: Determines if the current run is a rerun or not. Will rerun if the only 6th member options are
			suboptimal and will result in more net weaknesses than currently incurred.

	Returns: A list of optimal type combinations.
	'''

	bestNewCombos = []

	newMembers = members.copy()

	if rerun != None:
		weaknesses, resistances, immunities = get_team_defensive_properties(newMembers)
		minWeaknesses = len(weaknesses)
	else:
		minWeaknesses = 109

	types = getTypeCombos()

	for type in types:
		type1, type2 = type
		newMember = {}

		newMember['Weaknesses'], newMember['Resistances'], newMember['Immunities'] = get_member_defensive_properties(type1, type2)
		newMembers['Member 6'] = newMember

		weaknesses, resistances, immunities = get_team_defensive_properties(newMembers)

		if len(weaknesses) == minWeaknesses:
			bestNewCombos.append([type1, type2])

		elif len(weaknesses)<minWeaknesses:
			minWeaknesses = len(weaknesses)
			bestNewCombos = [[type1, type2]]
	
	if len(bestNewCombos) == 0:
		bestNewCombos = get_final_member_by_least_weaknesses(members, True)

	return bestNewCombos


def filter_for_maximum_types_resisted(members, combos):
	'''
	Purpose: To filter combos further by maximum amount of immunities.

	members: A dictionary corresponding to current members.

	combos: The current combos to be filtered.

	Returns: A list of optimal type combinations, further filtered down.
	'''

	newMembers = members.copy()
	filteredCombos = []

	resistances = []
	immunities = []

	for member in newMembers:
		resistances += members[member]['Resistances']
		immunities += members[member]['Immunities']

	maxResistancesAndImmunities = len([*set(resistances + immunities)])

	for combo in combos:
		type1, type2 = combo

		newMember = {}

		newMember['Weaknesses'], newMember['Resistances'], newMember['Immunities'] = get_member_defensive_properties(type1, type2)
		newMembers['Member 6'] = newMember

		resistances = []
		immunities = []

		for member in newMembers:
			resistances += newMembers[member]['Resistances']
			immunities += newMembers[member]['Immunities']

		total = len([*set(resistances + immunities)])

		if total == maxResistancesAndImmunities:
			filteredCombos.append([type1, type2])
				
		if total > maxResistancesAndImmunities:
			maxResistancesAndImmunities = total
			filteredCombos = [[type1, type2]]

	return filteredCombos	

def filter_for_maximum_STAB_coverage(members, combos):
	'''
	Purpose: To filter combos further by STAB supperefective coverage of combos.

	members: A dictionary corresponding to current members.

	combos: The current combos to be filtered.

	Returns: A list of optimal type combinations, further filtered down.
	'''

	file = open(f'Scripts{os.path.sep}types.json', 'r')
	types = json.load(file)

	bestCombos = []
	effective = []
	mostSTABCoverage = 0

	for member in members:
		effective += members[member]['Effective']
	
	effective = [*set(effective)]
	mostSTABCoverage = len(effective)

	for combo in combos:
		type1, type2 = combo
		tempEffective = [*set(types[type1]['Effective'] + types[type2]['Effective'] + effective)]
		if len(tempEffective) == mostSTABCoverage:
			bestCombos.append([type1, type2])
		if len(tempEffective) > mostSTABCoverage:
			mostSTABCoverage = len(tempEffective)
			bestCombos = [[type1, type2]]
	
	return bestCombos


def filter_for_least_weaknesses(members, combos, rerun=None):
	'''
	Purpose: To filter optimal type combinations for a last member based on current resistances and immunities.

	members: A dictionary corresponding to current members.

	combos: Type combinations already predetermined for filtering.

	rerun: Determines if the current run is a rerun or not. Will rerun if the only 6th member options are
			suboptimal and will result in more net weaknesses than currently incurred.

	Returns: A list of optimal type combinations.
	'''

	bestNewCombos = []

	newMembers = members.copy()

	if rerun != None:
		weaknesses, resistances, immunities = get_team_defensive_properties(newMembers)
		minWeaknesses = len(weaknesses)
	else:
		minWeaknesses = 109

	types = getTypeCombos()

	for combo in combos:
		type1, type2 = combo
		newMember = createMember(type1, type2)

		newMembers['Member 6'] = newMember

		weaknesses, resistances, immunities = get_team_defensive_properties(newMembers)

		if len(weaknesses) == minWeaknesses:
			bestNewCombos.append([type1, type2])

		elif len(weaknesses)<minWeaknesses:
			minWeaknesses = len(weaknesses)
			bestNewCombos = [[type1, type2]]
	
	if len(bestNewCombos) == 0:
		bestNewCombos = get_final_member_by_least_weaknesses(members, True)

	return bestNewCombos

def offense_pipeline(members):

	new_combos = get_final_member_by_STAB_coverage(members)

	new_combos = filter_for_least_weaknesses(members, new_combos)

	new_combos = filter_for_maximum_types_resisted(members, new_combos)

	return new_combos

def defense_pipeline(members):

	new_combos = get_final_member_by_least_weaknesses(members)

	new_combos = filter_for_maximum_types_resisted(members, new_combos)

	new_combos = filter_for_maximum_STAB_coverage(members, new_combos)

	return new_combos

if __name__ == '__main__':


	member1 = createMember('Water', 'Ground')
	member2 = createMember('Fire', 'Normal')
	member3 = createMember('Electric', 'Flying')
	member4 = createMember('Psychic', 'Steel')
	
	members = {}

	members['Member 1'] = member1
	members['Member 2'] = member2
	members['Member 3'] = member3
	members['Member 4'] = member4

	types = getTypeCombos()

	weaknesses = []
	weaknessesTracker = 109
	new_member_tracking = []

	for type in types:
		type1, type2 = type

		member5 = createMember(type1, type2)
		members['Member 5'] = member5

		new_members = defense_pipeline(members)

		temp_members = members.copy()

		for new_member in new_members:
			second_type1, second_type2 = new_member
			new_member = createMember(second_type1, second_type2)
			temp_members['Member 6'] = new_member
			weaknesses, resistances, immunities = get_team_defensive_properties(temp_members)

			if len(weaknesses)==weaknessesTracker:
				new_member_tracking.append([member5, new_member])

			if len(weaknesses)<weaknessesTracker:
				print('Here')
				weaknessesTracker = len(weaknesses)
				new_member_tracking = [[member5, new_member]]




